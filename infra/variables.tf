# Prefer env vars or tfvars; avoid committing real credentials.
# For LocalStack: TF_VAR_aws_access_key=test TF_VAR_aws_secret_key=test

variable "aws_access_key" {
  type        = string
  default     = "test"
  description = "AWS access key (use test for LocalStack)."
  sensitive   = true
}

variable "aws_secret_key" {
  type        = string
  default     = "test"
  description = "AWS secret key (use test for LocalStack)."
  sensitive   = true
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region."
}

variable "ec2_endpoint" {
  type        = string
  default     = "http://localhost:4566"
  description = "EC2 endpoint URL (LocalStack or real AWS)."
}

variable "availability_zone" {
  type        = string
  default     = "us-east-1a"
  description = "Availability zone for EBS volumes."
}
