# Cloud Resume Project

This repository contains the artifacts and code for my Cloud Resume Project, which is part of the [Cloud Resume Challenge](https://cloudresumechallenge.dev/). The project demonstrates my skills in AWS services, serverless architecture, and DevOps practices.

## Project Overview

The Cloud Resume Project is a full-stack application that displays my resume as a static website, with a visitor counter implemented using serverless technologies. The main components of this project include:

1. S3 buckets for static website hosting
2. CloudFront for content delivery
3. AWS Lambda functions for backend logic
4. DynamoDB for storing visitor count
5. API Gateway for creating a RESTful API
6. CodePipeline for CI/CD

## Repository Contents

This repository contains the following key files:

1. `addvisitor.py`: Lambda function to increment the visitor count
2. `getvisitor.py`: Lambda function to retrieve the current visitor count
3. `template.yaml`: CloudFormation template that defines the AWS infrastructure

## Infrastructure as Code

The `template.yaml` file is a CloudFormation template that defines the following resources:

- S3 buckets for website hosting and pipeline artifacts
- CodePipeline for CI/CD
- DynamoDB table for visitor count
- Lambda functions for visitor count logic
- API Gateway for exposing Lambda functions
- Necessary IAM roles and permissions

## Lambda Functions

### Add Visitor (`addvisitor.py`)

This function increments the visitor count in the DynamoDB table.

### Get Visitor (`getvisitor.py`)

This function retrieves the current visitor count from the DynamoDB table.

## Deployment

The project is set up with a CI/CD pipeline using AWS CodePipeline. Any changes pushed to the main branch of this repository will trigger an automatic deployment to the S3 bucket hosting the website.

## Website

The resume website is hosted at [https://will-garbutt.me](https://will-garbutt.me).