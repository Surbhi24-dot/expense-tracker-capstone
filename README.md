Personal Expense Tracker on AWS

A cloud-based Personal Expense Tracker built as an AWS capstone project.
The application is written in Python with Flask and uses Amazon RDS for
persistent MySQL storage. The AWS infrastructure was defined with
Terraform and deployed through HCP Terraform, connected to this GitHub
repository.

Current status: The capstone infrastructure was successfully
deployed and tested, then destroyed to avoid ongoing AWS charges. The
repository contains the project code and infrastructure configuration;
the live AWS URL is not expected to work while the infrastructure is
destroyed.

Project goals

Build a simple web application to manage personal expenses.

Practise Infrastructure as Code (IaC) with Terraform.

Deploy an application behind an Application Load Balancer.

Run multiple EC2 instances using an Auto Scaling Group.

Store application data in Amazon RDS for MySQL.

Connect GitHub to HCP Terraform so code changes can trigger
Terraform runs.

Features

Add an expense.

View expense entries.

Edit an existing expense.

Delete an expense.

Categorise expenses (for example, Food, Shopping, Bills, Transport,
and Other).

Record expense details and dates.

View the total of recorded expenses.

Architecture

                         Users / Browser
                                |
                                v
                     Application Load Balancer
                                |
                                v
                      Target Group (HTTP :5000)
                                |
                                v
                    Auto Scaling Group (2 x EC2)
                      Flask / Python application
                                |
                                v
                    Amazon RDS for MySQL
                       Private subnets

        VPC: 10.20.0.0/16
        Public subnets:  10.20.1.0/24, 10.20.4.0/24
        Private subnets: 10.20.2.0/24, 10.20.3.0/24

        Terraform configuration -> HCP Terraform -> AWS
        GitHub main branch ----------------^

The diagram describes the architecture that was deployed during the
capstone. The AWS resources have since been destroyed, so this is not a
diagram of currently running resources.

AWS services and tools

Amazon VPC: Network boundary and subnets.

Internet Gateway and route table: Internet routing for public
subnets.

Amazon EC2: Compute capacity for the Flask application.

Auto Scaling Group: Maintains the configured EC2 fleet.

Application Load Balancer (ALB): Routes HTTP requests to healthy
application targets.

Amazon RDS for MySQL: Managed relational database in private
subnets.

Amazon VPC security groups: Restrict access between the ALB,
application instances, and database.

Terraform: Defines and manages the infrastructure as code.

HCP Terraform: Remote Terraform runs and state management.

GitHub: Version control and source repository.

Python / Flask / PyMySQL: Application framework and MySQL
connectivity.

Repository contents

The repository contains the Flask application and Terraform
configuration files used for the capstone. The exact filenames may vary
with the current repository version. Common Terraform files include:

main.tf --- AWS resource definitions.

variables.tf --- configurable values, including sensitive database
settings.

outputs.tf --- useful outputs such as the ALB URL and RDS
endpoint.

versions.tf or provider configuration --- Terraform and AWS
provider requirements.

app.py --- Flask application code.

Deployment workflow

Make a change in the repository and push it to the main branch.

HCP Terraform detects the change and queues a run.

Review the Terraform plan carefully.

Approve the run to apply the changes (automatic apply was disabled
for this workspace).

After a successful apply, review the outputs and test the
application URL.

Important: Do not run Terraform locally against a stale local state
file. Use the configured HCP Terraform workspace for runs, and confirm
the correct workspace and AWS account before applying or destroying
resources.

Configuration and secrets

Store the database password as a sensitive variable in HCP
Terraform.

Do not commit real passwords, access keys, tokens, .tfstate files,
or private .tfvars files.

Keep sensitive local configuration excluded using .gitignore.

Never put credentials in screenshots or documentation.

Testing performed

The deployed application was tested for the main expense-management
actions:

Adding an expense.

Editing an expense.

Deleting an expense.

Viewing entries and the calculated total.

The AWS deployment completed successfully, and the application was
accessible through the ALB at the time of testing. The infrastructure
was later destroyed as a cost-control measure.

Cost and cleanup

AWS resources can incur charges while they exist, even when the
application is not actively used. For this capstone, the Terraform
destroy run completed with 0 added, 0 changed, and 19 destroyed. The
EC2 instances, RDS database, and load balancer were subsequently
confirmed absent from the AWS Console.

To recreate the infrastructure, review the code and variables first,
then run a plan and apply from the intended HCP Terraform workspace.
This will create billable resources again. Destroy resources when
finished, and check AWS Billing because charges can be delayed.

The default VPC in the account is separate from the capstone VPC and was
left untouched.

Lessons learned

How to define AWS infrastructure using Terraform.

How to use HCP Terraform for remote state and runs.

How to connect a GitHub repository to an HCP Terraform workspace.

How to deploy a Flask application with EC2, an ALB, an Auto Scaling
Group, and RDS.

How security groups control traffic between application tiers.

Why it is important to review AWS costs and clean up resources after
testing.

Further documentation

See PROJECT_DOCUMENTATION.md for a fuller
project summary, architecture, deployment workflow, testing, and cleanup
notes.

Disclaimer

This is an educational capstone project. It is not intended to be a
production-ready financial application. Before production use,
additional work would be needed for authentication, authorisation,
HTTPS, robust secrets management, backups, monitoring, and application
hardening.
