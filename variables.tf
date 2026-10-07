variable "db_password" {
  description = "Password for the Expense Tracker RDS database"
  type        = string
  sensitive   = true
}