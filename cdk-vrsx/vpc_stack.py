from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    RemovalPolicy,
    Tags
)
from aws_cdk import aws_ssm as ssm
from constructs import Construct

class vSRXVPCStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------------------------------------------------------------------------------------
        # Step 1: Create the VPC
        # ---------------------------------------------------------------------------------------
        self.vpc = ec2.CfnVPC(self, "vSRX-VPC",
            cidr_block="10.0.0.0/20", 
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=[{"key": "Name", "value": "vSRX-VPC"}]
        )

        # ---------------------------------------------------------------------------------------
        # Step 2: Create the Internet Gateway (IGW)
        # ---------------------------------------------------------------------------------------
        self.igw = ec2.CfnInternetGateway(self, "vSRX-IGW",
            tags=[{"key": "Name", "value": "vSRX-IGW"}]
        )

        # ---------------------------------------------------------------------------------------
        # Step 3: Attach IGW to the VPC
        # ---------------------------------------------------------------------------------------
        ec2.CfnVPCGatewayAttachment(self, "vSRX-VPCGW-Attachment",
            vpc_id=self.vpc.ref,
            internet_gateway_id=self.igw.ref
        )

        # ---------------------------------------------------------------------------------------
        # Step 4: Create Route Tables
        # ---------------------------------------------------------------------------------------
        self.public_rt = ec2.CfnRouteTable(self, "vSRX-Public-RT",
            vpc_id=self.vpc.ref,
            tags=[{"key": "Name", "value": "vSRX-Public-RT"}]
        )
        self.management_rt = ec2.CfnRouteTable(self, "vSRX-Management-RT",
            vpc_id=self.vpc.ref,
            tags=[{"key": "Name", "value": "vSRX-Management-RT"}]
        )
        self.private_rts = {}
        self.tgw_rts = {}
        for az in ['a', 'b', 'c']:
            self.private_rts[az] = ec2.CfnRouteTable(self, f"vSRX-Private-RT-{az}",
                vpc_id=self.vpc.ref,
                tags=[{"key": "Name", "value": f"vSRX-Private-RT-{az.upper()}"}]
            )
            self.tgw_rts[az] = ec2.CfnRouteTable(self, f"vSRX-TGW-RT-{az}",
                vpc_id=self.vpc.ref,
                tags=[{"key": "Name", "value": f"vSRX-TGW-RT-{az.upper()}"}]
            )

        # ---------------------------------------------------------------------------------------
        # Step 5: Create Subnets and Associate with Route Tables
        # ---------------------------------------------------------------------------------------
        self.subnets = {}
        subnet_config = [
            ("Public", ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]),
            ("Management", ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]),
            ("Private", ["10.0.8.0/24", "10.0.9.0/24", "10.0.10.0/24"]),
            ("TGW", ["10.0.15.192/28", "10.0.15.208/28", "10.0.15.224/28"])
        ]

        for subnet_type, cidrs in subnet_config:
            for i, cidr in enumerate(cidrs):
                az = chr(ord('a') + i)
                subnet = ec2.CfnSubnet(self, f"vSRX-{subnet_type}-Subnet-{az}",
                    vpc_id=self.vpc.ref,
                    cidr_block=cidr,
                    availability_zone=f"{self.region}{az}",
                    map_public_ip_on_launch=(subnet_type in ['Public', 'Management']),
                    tags=[{"key": "Name", "value": f"vSRX-{subnet_type}-Subnet-{az.upper()}"}]
                )
                self.subnets[f"{subnet_type}1{az.upper()}"] = subnet

                # Associate subnet with its route table
                if subnet_type == "Private":
                    rt_ref = self.private_rts[az].ref
                elif subnet_type == "Public":
                    rt_ref = self.public_rt.ref
                elif subnet_type == "Management":
                    rt_ref = self.management_rt.ref
                else:  # TGW
                    rt_ref = self.tgw_rts[az].ref

                ec2.CfnSubnetRouteTableAssociation(self, f"vSRX-{subnet_type}-RTAssoc-{az}",
                    subnet_id=subnet.ref,
                    route_table_id=rt_ref
                )

        # ---------------------------------------------------------------------------------------
        # Step 6: Add Routes to IGW for Management and Public Route Tables
        # ---------------------------------------------------------------------------------------
        ec2.CfnRoute(self, "vSRX-Management-IGW-Route",
            route_table_id=self.management_rt.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.igw.ref
        )

        ec2.CfnRoute(self, "vSRX-Public-IGW-Route",
            route_table_id=self.public_rt.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.igw.ref
        )
        # ---------------------------------------------------------------------------------------
        # Step 7: Create Security Groups (Management, Public, Private)
        # ---------------------------------------------------------------------------------------
        self.vsrx_management_sg = ec2.CfnSecurityGroup(self, "vSRX-Management-SG",
            group_description="Security group for vSRX management",
            group_name="vSRX-Management-SG",
            vpc_id=self.vpc.ref,
            security_group_egress=[{
                "ipProtocol": "-1",
                "cidrIp": "0.0.0.0/0"
            }],
            tags=[{"key": "Name", "value": "vSRX-Management-SG"}]
        )

        approved_ips_param = ssm.StringParameter.value_from_lookup(self, "/vsrx/approved_management_ips")
        approved_ips = approved_ips_param.split("\n")

        for i, ip in enumerate(approved_ips):
            ec2.CfnSecurityGroupIngress(self, f"vSRX-Management-SG-Ingress-{i}",
                group_id=self.vsrx_management_sg.ref,
                ip_protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_ip=ip,
                description=f'Allow approved IP {ip} for SSH'
            )

        self.vsrx_public_sg = ec2.CfnSecurityGroup(self, "vSRX-Public-SG",
            group_description="Security group for vSRX public access",
            group_name="vSRX-Public-SG",
            vpc_id=self.vpc.ref,
            security_group_egress=[{
                "ipProtocol": "-1",
                "cidrIp": "0.0.0.0/0"
            }],
            security_group_ingress=[{
                "ipProtocol": "tcp",
                "fromPort": 443,
                "toPort": 443,
                "cidrIp": "0.0.0.0/0",
                "description": "Allow HTTPS traffic from anywhere"
            }],
            tags=[{"key": "Name", "value": "vSRX-Public-SG"}]
        )

        # Create the security group without the ingress rule
        self.vsrx_private_sg = ec2.CfnSecurityGroup(self, "vSRX-Private-SG",
            group_description="Security group for vSRX private access",
            group_name="vSRX-Private-SG",
            vpc_id=self.vpc.ref,
            security_group_egress=[{
                "ipProtocol": "-1",
                "cidrIp": "0.0.0.0/0"
            }],
            tags=[{"key": "Name", "value": "vSRX-Private-SG"}]
        )

        # Add the ingress rule as a separate resource
        ec2.CfnSecurityGroupIngress(self, "vSRX-Private-SG-SelfIngress",
            group_id=self.vsrx_private_sg.ref,
            ip_protocol="tcp",
            from_port=0,
            to_port=65535,
            source_security_group_id=self.vsrx_private_sg.ref,
            description="Allow all TCP traffic from vSRX-Private-SG"
        )

        # ---------------------------------------------------------------------------------------
        # Step 8: Create Log group, role, and Policy
        # ---------------------------------------------------------------------------------------
        self.log_group = logs.LogGroup(
            self,
            'vSRX-VPC-Flow-LogGroup',
            log_group_name="/aws/vpc/flowlogs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.vpc_flow_role = iam.Role(
            self,
            "vSRX-VPCFlowLogRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com")
        )

        flow_logs_policy = iam.PolicyStatement(
            actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[self.log_group.log_group_arn]
        )
        self.vpc_flow_role.add_to_policy(flow_logs_policy)

        self.flow_log = ec2.CfnFlowLog(
            self,
            'vSRX-VPC-Flow-Log',
            resource_id=self.vpc.ref,
            resource_type="VPC",
            traffic_type="ALL",
            deliver_logs_permission_arn=self.vpc_flow_role.role_arn,
            log_destination_type="cloud-watch-logs",
            log_group_name=self.log_group.log_group_name
        )

        # ---------------------------------------------------------------------------------------
        # Step 9: Output for Reference
        # ---------------------------------------------------------------------------------------
        CfnOutput(self, "vSRX-VPC-ID", value=self.vpc.ref)
        CfnOutput(self, "vSRX-Management-SG-ID", value=self.vsrx_management_sg.ref)
        CfnOutput(self, "vSRX-Public-SG-ID", value=self.vsrx_public_sg.ref)
        CfnOutput(self, "vSRX-Private-SG-ID", value=self.vsrx_private_sg.ref)

        CfnOutput(self, "vSRX-Management-RT-ID", value=self.management_rt.ref)
        CfnOutput(self, "vSRX-Public-RT-ID", value=self.public_rt.ref)


        for az in ['a', 'b', 'c']:
            CfnOutput(self, f"vSRX-Private-RT-ID-{az.upper()}", value=self.private_rts[az].ref)

        for subnet_type in ["Public", "Management", "Private", "Attachment"]:
            for az in ['A', 'B', 'C']:
                subnet_key = f"{subnet_type}1{az}"
                if subnet_key in self.subnets:
                    CfnOutput(self, f"vSRX-{subnet_key}-Subnet-ID", value=self.subnets[subnet_key].ref)