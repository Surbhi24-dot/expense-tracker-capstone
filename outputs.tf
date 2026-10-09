output "vpc_id" {
  description = "ID of the Expense Tracker VPC"
  value       = aws_vpc.expense_tracker.id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.expense_tracker.dns_name
}

output "expense_tracker_url" {
  description = "URL to access the Expense Tracker application"
  value       = "http://${aws_lb.expense_tracker.dns_name}"
}

output "autoscaling_group_name" {
  description = "Name of the Expense Tracker Auto Scaling Group"
  value       = aws_autoscaling_group.expense_tracker.name
}

output "rds_endpoint" {
  description = "Endpoint of the Expense Tracker database"
  value       = aws_db_instance.expense_tracker.address
}