# main.tf - EBS volumes for policy audit demo (LocalStack or AWS)
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  access_key                  = var.aws_access_key
  secret_key                  = var.aws_secret_key
  region                      = var.aws_region
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    ec2 = var.ec2_endpoint
  }
}

# Only COMPLIANT resources live in Terraform (= desired state).
# Non-compliant / junk volumes are NOT in Terraform; they come from drift,
# legacy, or the demo seed script. Sentinel finds them; Janitor removes them.
# So: apply → compliant only. Seed (demo) → sentinel → janitor → junk stays gone.

resource "aws_ebs_volume" "compliant_vol" {
  availability_zone = var.availability_zone
  size              = 20
  encrypted         = true
  tags = {
    Name  = "User-Data-PROD"
    Env   = "Production"
    Owner = "Infrastructure-Team"
  }
}