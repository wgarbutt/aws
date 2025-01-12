from aws_cdk import (
    Stack,
    aws_ssm as ssm
)
from constructs import Construct

class ParameterStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # List of approved IPs
        approved_ips = [
            "X.X.X.X/32",
            
        ]

        # Combine IPs into a single string
        ip_list_string = "\n".join(approved_ips)

        # Create and store the IPs in Parameter Store
        ssm.StringParameter(
            self, "ApprovedVSRXManagementIPs",
            parameter_name="/vsrx/approved_management_ips",  
            string_value=ip_list_string,                     
            description="Approved IPs for vSRX management interface",
            tier=ssm.ParameterTier.STANDARD  
        )

        # Add the vSRX AMI name parameter
        ssm.StringParameter(
            self, "VSRXAmiName",
            parameter_name="/vsrx/ami-name",
            string_value="junos-vsrx3-x86-64",
            description="AMI name for vSRX instances",
            tier=ssm.ParameterTier.STANDARD
        )
        
        # Add the vSRX instance type parameter
        ssm.StringParameter(
            self, "VSRXInstanceType",
            parameter_name="/vsrx/instance-type",
            string_value="c5.xlarge",
            description="EC2 instance type for vSRX instances",
            tier=ssm.ParameterTier.STANDARD
        )

        # Add the vSRX key pair name parameter
        ssm.StringParameter(
            self, "VSRXKeyPairName",
            parameter_name="/vsrx/key-pair-name",
            string_value="vSRXKeyPair",
            description="Key pair name for vSRX instances",
            tier=ssm.ParameterTier.STANDARD
        )