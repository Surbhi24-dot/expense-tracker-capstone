# AWS Capstone Project Documentation

## Personal Expense Tracker

**Project type:** AWS cloud infrastructure and application capstone\
**Application:** Python Flask Personal Expense Tracker\
**Infrastructure as Code:** Terraform\
**Deployment orchestration:** HCP Terraform connected to GitHub\
**AWS Region:** `us-east-1` (US East --- N. Virginia)\
**Repository:** https://github.com/Surbhi24-dot/expense-tracker-capstone

## 1. Project overview

The goal was to create a simple web application for recording personal
expenses and to deploy it on AWS using infrastructure as code. Users can
add, view, edit, and delete expenses, assign categories, and see the
total of the recorded expenses.

The project was built in stages to practise the progression from a
simple application deployment to a multi-tier AWS architecture.

## 2. Functional requirements

The application supports the following actions:

-   Add an expense.
-   View expense records.
-   Edit an expense.
-   Delete an expense.
-   Use categories such as Food, Shopping, Bills, Transport, and Other.
-   Record expense information and dates.
-   Calculate and display the total of the saved expenses.

The main application actions were tested on the deployed application.

## 3. AWS architecture

### Network

-   VPC CIDR: `10.20.0.0/16`
-   Public subnet 1: `10.20.1.0/24` in `us-east-1a`
-   Private subnet 1: `10.20.2.0/24` in `us-east-1a`
-   Private subnet 2: `10.20.3.0/24` in `us-east-1b`
-   Public subnet 2: `10.20.4.0/24` in `us-east-1b`
-   Internet Gateway and public route table for internet routing.
-   Security groups control permitted traffic between the load balancer,
    application instances, and database.

### Application tier

-   Application Load Balancer listens on HTTP port 80.
-   The target group forwards requests to the Flask application on port
    5000.
-   An Auto Scaling Group was configured with a minimum, maximum, and
    desired capacity of two EC2 instances.
-   The launch template specifies a `t3.micro` instance type and starts
    the Flask application using a system service.

### Database tier

-   Amazon RDS for MySQL was deployed in private subnets.
-   The database security group allowed MySQL traffic on port 3306 from
    the application security group, rather than directly from the public
    internet.
-   The application connected to RDS using environment variables and
    PyMySQL.

### Infrastructure management

-   Terraform defined the AWS resources.
-   HCP Terraform provided remote runs and state management.
-   The HCP Terraform workspace was connected to the GitHub repository
    and configured to trigger runs from the `main` branch.
-   Automatic apply was disabled so that a plan could be reviewed before
    applying changes.

## 4. Request flow

1.  A user opens the application URL in a browser.
2.  The Application Load Balancer receives the HTTP request.
3.  The load balancer forwards the request to a healthy EC2 application
    target on port 5000.
4.  The Flask application processes the request.
5.  The application reads or writes expense data in the private RDS
    MySQL database.
6.  The response returns through the load balancer to the user's
    browser.

## 5. Deployment workflow

1.  Store Terraform and application files in the GitHub repository.
2.  Push changes to `main`.
3.  HCP Terraform detects the repository update and queues a run.
4.  Review the plan for unexpected additions, changes, or deletions.
5.  Approve and apply the plan when the account, region, and cost
    implications are understood.
6.  Check the run outputs and AWS resource health.
7.  Test the application through the ALB URL.
8.  When finished, destroy the temporary resources and verify cleanup in
    the AWS Console.

The current infrastructure has been destroyed. Reapplying the
configuration will create resources and may incur AWS charges.

## 6. Testing and validation

The application was tested for:

-   Creating an expense.
-   Editing an expense.
-   Deleting an expense.
-   Viewing expense records and their total.

The Terraform deployment completed successfully with 19 resources added.
The application was accessible through the ALB and its
expense-management actions were tested.

After testing, a Terraform destroy run completed successfully with **0
added, 0 changed, and 19 destroyed**. The user subsequently checked the
AWS Console and reported that the EC2 instances, RDS database, and load
balancer were no longer present. Only the account's default VPC remained
visible.

## 7. Security considerations

-   The database was configured in private subnets.
-   The database security group allowed port 3306 from the application
    security group.
-   The application port was intended to accept traffic from the load
    balancer security group.
-   The load balancer accepted HTTP traffic on port 80 during the
    capstone.
-   The database password was configured as a sensitive HCP Terraform
    variable.
-   Real credentials and Terraform state files must not be committed to
    GitHub.

This was an educational project. For production, add HTTPS,
authentication and authorisation, stronger secrets and access controls,
backups, monitoring, and further security testing.

## 8. Cost management and cleanup

AWS resources such as RDS, EC2, and an Application Load Balancer can
generate costs while deployed. Billing data can also appear after a
resource has been deleted.

For this project, the infrastructure was destroyed after testing to
reduce ongoing charges. The default VPC was not part of the capstone
cleanup and was left in place. AWS Billing should continue to be
monitored after cleanup to confirm that new usage costs have stopped.

## 9. Challenges and learning outcomes

The project provided practice with:

-   Terraform resource definitions, variables, outputs, and state.
-   HCP Terraform workspace setup and GitHub integration.
-   Reviewing plans before applying infrastructure changes.
-   VPCs, public and private subnets, route tables, and security groups.
-   EC2 launch templates and Auto Scaling Groups.
-   Application Load Balancer listeners, target groups, and health
    checks.
-   RDS MySQL connectivity from a Flask application.
-   Git-based infrastructure workflows.
-   AWS cost awareness and cleanup of temporary resources.

## 10. Known limitations and possible improvements

The application is a learning project, not a production financial
system. Possible future improvements include:

-   User login and per-user expense separation.
-   HTTPS using a managed certificate.
-   A custom domain name.
-   More comprehensive input validation and error handling.
-   Automated application and infrastructure tests.
-   Centralised logs, alarms, and monitoring.
-   Database backup and recovery planning.
-   Production-oriented network design and access controls.

## 11. Current status

**Application and Terraform configuration:** Kept in GitHub.\
**HCP Terraform workspace:** Kept for future runs.\
**AWS capstone infrastructure:** Destroyed after testing.\
**Live application URL:** Not expected to work until the infrastructure
is deployed again.\
**Expense data in the deleted RDS database:** Not retained by the
destroy operation; no final snapshot was configured.

## 12. Important safety reminder

Before recreating the environment, review the Terraform plan and verify
the correct AWS account, region, workspace, and sensitive variables.
Applying the configuration creates billable resources. Destroy temporary
resources when finished, then check the AWS Console and Billing
dashboard.
