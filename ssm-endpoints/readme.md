# SSM Access CloudFormation Template

This CloudFormation template sets up the necessary resources for Systems Manager (SSM) access to EC2 instances without internet access. It creates VPC endpoints, IAM roles, and security group rules required for SSM functionality.

## Template Overview

This template creates the following resources:

1. SSM VPC Endpoints:
   - SSM Endpoint
   - SSM Messages Endpoint
   - EC2 Messages Endpoint

2. IAM Role and Instance Profile for SSM access

3. Security Group Rules:
   - For SSM access (port 443)
   - For RDP access (port 3389)

## Parameters

The template uses the following parameters:

- `VpcId`: The VPC ID where the resources will be created
- `SubnetIds`: List of Subnet IDs where the SSM endpoints will be created
- `SecurityGroupId`: The Security Group ID to modify for SSM access

These parameters are presented as dropdown lists of existing resources for ease of use.

## Resources Created

1. **VPC Endpoints**:
   - SSM Endpoint
   - SSM Messages Endpoint
   - EC2 Messages Endpoint

2. **IAM Resources**:
   - SSM IAM Role
   - SSM Instance Profile

3. **Security Group Rules**:
   - SSM Security Group Rule (TCP 443)
   - RDP Security Group Rule (TCP 3389)

## Outputs

- `SSMIAMRoleArn`: ARN of the IAM Role created for SSM

## Usage

1. Upload this template to CloudFormation in the AWS Console or use AWS CLI.
2. Provide the required parameters (VPC ID, Subnet IDs, Security Group ID).
3. Create the stack.
4. Once the stack is created, you can use the SSM Instance Profile for EC2 instances that need SSM access.

## Notes

- This template is designed for Windows environments, hence the RDP access
- Ensure that the VPC, Subnets, and Security Group you select are appropriate for your use case.
- The template uses `!Select` to convert single-item lists to strings where required by AWS resources.

