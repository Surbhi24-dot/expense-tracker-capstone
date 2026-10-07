# AWS Expense Tracker

A simple personal expense tracker application deployed on AWS using Terraform.

The project is built as part of my AWS and Terraform learning journey. The goal is to start with a small working application and gradually improve the infrastructure as I learn more AWS services.

## Project Overview

The Expense Tracker allows users to:

* Add an expense
* View expenses
* Edit expenses
* Delete expenses
* See the total expenses
* Organize expenses by category
* Store the expense date

The application is built with Python and Flask. The current version uses SQLite for data storage.

## Architecture

```text
GitHub
   |
   | Push to main
   v
Terraform Cloud
   |
   | Terraform plan and apply
   v
AWS
   |
   +----------------------+
   |                      |
   v                      v
  VPC                Security Group
   |
   v
Public Subnet
   |
   v
EC2 Instance
   |
   +-- Python
   +-- Flask
   +-- SQLite
   |
   v
Expense Tracker
```

## AWS Resources

The current version creates the following AWS resources using Terraform:

* VPC
* Public Subnet
* Internet connectivity
* Security Group
* EC2 Instance

The EC2 instance runs the Flask Expense Tracker application.

## Terraform

Terraform is used to create and manage the AWS infrastructure as code.

The main Terraform configuration contains:

* AWS provider
* VPC
* Public subnet
* Security group
* EC2 instance
* Terraform outputs

Terraform state is managed by Terraform Cloud.

## Automated Deployment

The project uses GitHub and Terraform Cloud.

The deployment flow is:

```text
1. Make a change to the project
          |
          v
2. Push the change to GitHub
          |
          v
3. GitHub triggers Terraform Cloud
          |
          v
4. Terraform Cloud creates a plan
          |
          v
5. Terraform Cloud applies the infrastructure
          |
          v
6. AWS infrastructure is updated
```

Auto Apply is currently disabled so that infrastructure changes can be reviewed before they are applied.

## EC2 Application Setup

The EC2 instance uses Terraform `user_data` to automatically configure the application when the instance starts.

The startup process:

```text
EC2 starts
   |
   v
Install Python and pip
   |
   v
Create application directory
   |
   v
Copy app.py to EC2
   |
   v
Create Python virtual environment
   |
   v
Install Flask
   |
   v
Create systemd service
   |
   v
Start Expense Tracker
```

This means the application does not need to be manually installed after a new EC2 instance is created.

## Application

The application is built with:

* Python
* Flask
* SQLite
* HTML

The current application runs on port `5000`.

## Project Structure

```text
expense-tracker-capstone/
│
├── app.py
├── main.tf
├── outputs.tf
├── .gitignore
└── .terraform.lock.hcl
```

### `app.py`

Contains the Flask Expense Tracker application.

### `main.tf`

Contains the Terraform configuration for the AWS infrastructure.

### `outputs.tf`

Displays useful Terraform outputs such as:

* VPC ID
* Subnet ID
* EC2 Instance ID
* Public IP address

### `.gitignore`

Prevents files such as Terraform state files, the SQLite database, and Python cache files from being uploaded to GitHub.

## Current Level

The project has now reached Level 2.

The application runs on Amazon EC2 and uses Amazon RDS MySQL as the database.

The current architecture is:

Internet
↓
Public Subnet
↓
EC2
↓
Private Subnets
↓
RDS MySQL

The focus of Level 2 is on understanding:

* Terraform
* AWS VPC
* Public and private subnets
* Internet Gateway
* Route Tables
* Security Groups
* EC2
* Amazon RDS MySQL
* Database connectivity
* Infrastructure as Code
* GitHub
* Terraform Cloud
* Automated application setup

The Terraform infrastructure is stored in GitHub and connected to Terraform Cloud. Changes pushed to the main branch automatically trigger a Terraform plan.

## Future Improvements

The project can be extended as I learn more AWS services.

### Level 3

Possible future improvements include:

* Application Load Balancer
* Auto Scaling Group
* Multiple EC2 instances
* RDS MySQL database
* Improved high availability
* More scalable architecture

## Learning Goals

This project is designed to demonstrate practical knowledge of:

* AWS infrastructure
* Terraform
* Infrastructure as Code
* GitHub version control
* Terraform Cloud
* EC2 deployment
* Amazon RDS
* Basic cloud networking
* Public and private subnets
* Security Groups
* Database connectivity
* Application deployment
* AWS architecture

## Author

Surbhi Suman

AWS / Terraform Learning Project
