# Stuffabout.cloud VPC and Public Instance CloudFormation Template

This CloudFormation template creates a VPC with a public subnet and launches an EC2 instance with Systems Manager Session Manager access. It's designed for the stuffabout.cloud infrastructure before I moved over to a static website using Hugo hosted on s3

## Template Overview

This template sets up the following AWS resources:

1. VPC with IPv4 and IPv6 CIDR blocks
2. Internet Gateway
3. Public Subnet
4. Route Table with routes for IPv4 and IPv6 internet access
5. EC2 Instance in the public subnet
6. Security Group for the EC2 instance
7. IAM Role and Instance Profile for Systems Manager Session Manager

## Parameters

- `LatestAmiId`: The ID of the Amazon Machine Image (AMI) to use for the EC2 instance. Default is the latest Amazon Linux 2 AMI.

## Resources Created

1. **VPC**: 
   - CIDR Block: 10.16.0.0/16
   - Enabled for DNS support and hostnames

2. **Internet Gateway**: 
   - Attached to the VPC

3. **Public Subnet**:
   - CIDR Block: 10.16.0.0/20
   - Configured for IPv6
   - Auto-assigns public IPv4 addresses

4. **Route Table**:
   - Routes for IPv4 and IPv6 internet access

5. **EC2 Instance**:
   - Instance Type: t2.micro
   - Uses the specified AMI
   - Located in the public subnet
   - Tagged with Name: Stuffabout.cloud

6. **Security Group**:
   - Allows inbound SSH (port 22) for IPv4 and IPv6
   - Allows inbound HTTPS (port 443) and HTTP (port 80) for IPv4

7. **IAM Role and Instance Profile**:
   - Configured for Systems Manager Session Manager access

## Usage

1. Upload this template to CloudFormation in the AWS Console or use AWS CLI.
2. Provide the required parameter (AMI ID) if you want to use a specific AMI.
3. Create the stack.
4. Once the stack is created, you can access the EC2 instance using Systems Manager Session Manager.

## Notes

- The EC2 instance is launched with a key pair named "stuffaboutcloud". Ensure this key pair exists in your account or modify the template accordingly.
- The template uses the latest Amazon Linux 2 AMI by default, but you can specify a different AMI if needed.
- The EC2 instance is publicly accessible via SSH and HTTP/HTTPS. Ensure this aligns with your security requirements.

## Customization

You can customize this template by:
- Modifying the VPC and subnet CIDR blocks
- Changing the instance type of the EC2 instance
- Adding more subnets or Availability Zones
- Modifying the security group rules

