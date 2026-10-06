terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.6.0"
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "expense_tracker" {
  cidr_block = "10.20.0.0/16"

  tags = {
    Name = "expense-tracker-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.expense_tracker.id
  cidr_block              = "10.20.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "expense-tracker-public-subnet"
  }
}

resource "aws_internet_gateway" "expense_tracker" {
  vpc_id = aws_vpc.expense_tracker.id

  tags = {
    Name = "expense-tracker-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.expense_tracker.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.expense_tracker.id
  }

  tags = {
    Name = "expense-tracker-public-route-table"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "web" {
  name        = "expense-tracker-web-sg"
  description = "Security group for Expense Tracker web server"
  vpc_id      = aws_vpc.expense_tracker.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Flask application"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "expense-tracker-web-sg"
  }
}

resource "aws_instance" "web" {
  ami           = "ami-0d27e0fb3bac4d724"
  instance_type = "t3.micro"

  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true


  user_data = <<-EOF
#!/bin/bash

    # Update the server
    dnf update -y

    # Install Python and pip
    dnf install -y python3 python3-pip

    # Create a folder for the Expense Tracker
    mkdir -p /home/ec2-user/expense-tracker

    # Copy the application from the Terraform project to EC2
    cat > /home/ec2-user/expense-tracker/app.py <<'PYAPP'
${file("${path.module}/app.py")}
PYAPP

    # Give the application folder to ec2-user
    chown -R ec2-user:ec2-user /home/ec2-user/expense-tracker

    # Create a Python virtual environment
    python3 -m venv /home/ec2-user/expense-tracker/venv

    # Install Flask inside the virtual environment
    /home/ec2-user/expense-tracker/venv/bin/python -m pip install flask

    # Create systemd service
    cat > /etc/systemd/system/expense-tracker.service <<'SERVICE'
[Unit]
Description=Expense Tracker Flask Application
After=network-online.target
Wants=network-online.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/expense-tracker
ExecStart=/home/ec2-user/expense-tracker/venv/bin/python /home/ec2-user/expense-tracker/app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

    # Enable and start the application
    systemctl daemon-reload
    systemctl enable expense-tracker
    systemctl start expense-tracker
  EOF

  user_data_replace_on_change = true

  lifecycle {
    create_before_destroy = true
  }


  tags = {
    Name = "expense-tracker-web"
  }
}