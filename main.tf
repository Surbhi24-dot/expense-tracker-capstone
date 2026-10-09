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

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.expense_tracker.id
  cidr_block              = "10.20.4.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "expense-tracker-public-subnet-2"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.expense_tracker.id
  cidr_block        = "10.20.2.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "expense-tracker-private-subnet"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.expense_tracker.id
  cidr_block        = "10.20.3.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "expense-tracker-private-subnet-2"
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

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "web" {
  name        = "expense-tracker-web-sg"
  description = "Security group for Expense Tracker web server"
  vpc_id      = aws_vpc.expense_tracker.id

  ingress {
    description     = "Flask traffic from the ALB only"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
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

resource "aws_security_group" "alb" {
  name        = "expense-tracker-alb-sg"
  description = "Allow HTTP traffic to the Application Load Balancer"
  vpc_id      = aws_vpc.expense_tracker.id

  ingress {
    description = "HTTP from the internet"
    from_port   = 80
    to_port     = 80
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
    Name = "expense-tracker-alb-sg"
  }
}

resource "aws_security_group" "database" {
  name        = "expense-tracker-database-sg"
  description = "Security group for Expense Tracker RDS"
  vpc_id      = aws_vpc.expense_tracker.id

  ingress {
    description     = "MySQL from Expense Tracker EC2"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "expense-tracker-database-sg"
  }
}

resource "aws_db_subnet_group" "expense_tracker" {
  name = "expense-tracker-db-subnet-group"

  subnet_ids = [
    aws_subnet.private.id,
    aws_subnet.private_2.id
  ]

  tags = {
    Name = "expense-tracker-db-subnet-group"
  }
}

resource "aws_db_instance" "expense_tracker" {
  identifier = "expense-tracker-db"

  engine         = "mysql"
  engine_version = "8.0.46"

  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  max_allocated_storage = 20
  storage_type          = "gp3"

  db_name  = "expense_tracker"
  username = "expense_user"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.expense_tracker.name
  vpc_security_group_ids = [aws_security_group.database.id]

  publicly_accessible = false
  skip_final_snapshot = true
  deletion_protection = false

  backup_retention_period = 0

  tags = {
    Name = "expense-tracker-rds"
  }
}

# Application Load Balancer
resource "aws_lb" "expense_tracker" {
  name               = "expense-tracker-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]

  subnets = [
    aws_subnet.public.id,
    aws_subnet.public_2.id
  ]

  tags = {
    Name = "expense-tracker-alb"
  }
}

# Target group for the Flask application
resource "aws_lb_target_group" "expense_tracker" {
  name     = "expense-tracker-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.expense_tracker.id

  health_check {
    enabled             = true
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "expense-tracker-target-group"
  }
}

# HTTP listener for the load balancer
resource "aws_lb_listener" "expense_tracker" {
  load_balancer_arn = aws_lb.expense_tracker.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.expense_tracker.arn
  }
}

# Launch Template for Expense Tracker EC2 instances
resource "aws_launch_template" "expense_tracker" {
  name_prefix   = "expense-tracker-"
  image_id      = "ami-0d27e0fb3bac4d724"
  instance_type = "t3.micro"

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.web.id]
  }

  user_data = base64encode(<<-EOF
#!/bin/bash
set -e

dnf update -y
dnf install -y python3 python3-pip

mkdir -p /home/ec2-user/expense-tracker

curl -fL -o /home/ec2-user/expense-tracker/app.py \
  https://raw.githubusercontent.com/Surbhi24-dot/expense-tracker-capstone/main/app.py

chown -R ec2-user:ec2-user /home/ec2-user/expense-tracker

python3 -m venv /home/ec2-user/expense-tracker/venv

/home/ec2-user/expense-tracker/venv/bin/python -m pip install flask pymysql

cat > /etc/systemd/system/expense-tracker.service <<'SERVICE'
[Unit]
Description=Expense Tracker Flask Application
After=network-online.target
Wants=network-online.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/expense-tracker
Environment="DB_HOST=${aws_db_instance.expense_tracker.address}"
Environment="DB_USER=expense_user"
Environment="DB_PASSWORD=${var.db_password}"
Environment="DB_NAME=expense_tracker"
ExecStart=/home/ec2-user/expense-tracker/venv/bin/python /home/ec2-user/expense-tracker/app.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable expense-tracker
systemctl start expense-tracker
EOF
  )

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "expense-tracker-asg-instance"
    }
  }
}

# Auto Scaling Group for Expense Tracker
resource "aws_autoscaling_group" "expense_tracker" {
  name             = "expense-tracker-asg"
  min_size         = 2
  max_size         = 2
  desired_capacity = 2
  vpc_zone_identifier = [
    aws_subnet.public.id,
    aws_subnet.public_2.id
  ]

  target_group_arns = [
    aws_lb_target_group.expense_tracker.arn
  ]

  health_check_type         = "ELB"
  health_check_grace_period = 300

  launch_template {
    id      = aws_launch_template.expense_tracker.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "expense-tracker-asg-instance"
    propagate_at_launch = true
  }
}