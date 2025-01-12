from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
    Tags
)
from constructs import Construct

class VSRXStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------------------------------------------------------------------------------------
        # Step 1: Lookup the parameters and print to console
        # ---------------------------------------------------------------------------------------
        vsrx_ami_name = ssm.StringParameter.value_from_lookup(self, "/vsrx/ami-name")
        vsrx_instance_type = ssm.StringParameter.value_from_lookup(self, "/vsrx/instance-type")
        vsrx_key_pair_name = ssm.StringParameter.value_from_lookup(self, "/vsrx/key-pair-name")

        print(f"Using AMI name: {vsrx_ami_name}")
        print(f"Using instance type: {vsrx_instance_type}")
        print(f"Using key pair name: {vsrx_key_pair_name}")

        vsrx_ami = ec2.MachineImage.lookup(
            name=vsrx_ami_name
        )

        # ---------------------------------------------------------------------------------------
        # Step 2: Create Elastic IPs for both Management and Public ENIs
        # ---------------------------------------------------------------------------------------
        management_eip = ec2.CfnEIP(self, "vSRX-Management-EIP")
        public_eip = ec2.CfnEIP(self, "vSRX-Public-EIP")

        # ---------------------------------------------------------------------------------------
        # Step 3: Create Management ENI
        # ---------------------------------------------------------------------------------------
        management_eni = ec2.CfnNetworkInterface(
            self, "vSRX-Management-ENI",
            subnet_id=vpc_stack.subnets['Management1A'].ref,
            group_set=[vpc_stack.vsrx_management_sg.ref],
            source_dest_check=False,
            description="vSRX Management ENI"
        )

        # ---------------------------------------------------------------------------------------
        # Step 4: Associate Elastic IP with the Management ENI
        # ---------------------------------------------------------------------------------------
        ec2.CfnEIPAssociation(self, "vSRX-Management-EIP-Association",
            allocation_id=management_eip.attr_allocation_id,
            network_interface_id=management_eni.ref
        )

        # ---------------------------------------------------------------------------------------
        # Step 5: Create Public ENI
        # ---------------------------------------------------------------------------------------
        public_eni = ec2.CfnNetworkInterface(
            self, "vSRX-Public-ENI",
            subnet_id=vpc_stack.subnets['Public1A'].ref,
            group_set=[vpc_stack.vsrx_public_sg.ref],
            source_dest_check=False,
            description="vSRX Public ENI"
        )

        # ---------------------------------------------------------------------------------------
        # Step 6: Associate Elastic IP with the Public ENI
        # ---------------------------------------------------------------------------------------
        ec2.CfnEIPAssociation(self, "vSRX-Public-EIP-Association",
            allocation_id=public_eip.attr_allocation_id,
            network_interface_id=public_eni.ref
        )

        # ---------------------------------------------------------------------------------------
        # Step 7: Create Private ENI (No Elastic IP needed here)
        # ---------------------------------------------------------------------------------------
        private_eni = ec2.CfnNetworkInterface(
            self, "vSRX-Private-ENI",
            subnet_id=vpc_stack.subnets['Private1A'].ref,
            group_set=[vpc_stack.vsrx_private_sg.ref],
            source_dest_check=False,
            description="vSRX Private ENI"
        )

        # ---------------------------------------------------------------------------------------
        # Step 8: Create a Custom IAM Role and a Custom Instance Profile
        # ---------------------------------------------------------------------------------------
        vsrx_role = iam.Role(
            self, "vSRXInstanceRole",  
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        instance_profile = iam.CfnInstanceProfile(
            self, "vSRX-Instance-Profile",  
            roles=[vsrx_role.role_name],
            instance_profile_name="vSRXInstanceProfile"
        )

        # ---------------------------------------------------------------------------------------
        # Step 9: Deploy the vSRX Instance using the looked-up AMI and pre-created ENIs
        # ---------------------------------------------------------------------------------------
        self.vsrx_instance = ec2.CfnInstance(
            self, "vSRX-Instance",
            instance_type=vsrx_instance_type,
            image_id=vsrx_ami.get_image(self).image_id,
            key_name=vsrx_key_pair_name,
            network_interfaces=[
                ec2.CfnInstance.NetworkInterfaceProperty(
                    device_index="0",
                    network_interface_id=management_eni.ref
                ),
                ec2.CfnInstance.NetworkInterfaceProperty(
                    device_index="1",
                    network_interface_id=public_eni.ref
                ),
                ec2.CfnInstance.NetworkInterfaceProperty(
                    device_index="2",
                    network_interface_id=private_eni.ref
                ),
            ],
            iam_instance_profile=instance_profile.ref,
            tags=[{"key": "Name", "value": "vSRX-Instance"}]
        )

        # ---------------------------------------------------------------------------------------
        # Step 10: Outputs for Network Interfaces and Elastic IPs
        # ---------------------------------------------------------------------------------------
        CfnOutput(self, "vSRX-Management-ENI-Id", value=management_eni.ref)
        CfnOutput(self, "vSRX-Public-ENI-Id", value=public_eni.ref)
        CfnOutput(self, "vSRX-Private-ENI-Id", value=private_eni.ref)

        CfnOutput(self, "vSRX-Management-ElasticIP", value=management_eip.ref)
        CfnOutput(self, "vSRX-Public-ElasticIP", value=public_eip.ref)

        CfnOutput(self, "vSRX-Instance-Id", value=self.vsrx_instance.ref)
