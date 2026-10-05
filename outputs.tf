output "vpc_id" {
  description = "ID of the Expense Tracker VPC"
  value       = aws_vpc.expense_tracker.id
}

output "subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

output "instance_id" {
  description = "ID of the Expense Tracker EC2 instance"
  value       = aws_instance.web.id
}

output "public_ip" {
  description = "Public IP address of the Expense Tracker server"
  value       = aws_instance.web.public_ip
}