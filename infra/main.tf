# main.tf
provider "aws" {
  access_key = "test"
  secret_key = "test"
  region     = "us-east-1"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints { ec2 = "http://localhost:4566" }
}

# 1. COMPLIANT VOLUME
resource "aws_ebs_volume" "compliant_vol" {
  availability_zone = "us-east-1a"
  size              = 20
  encrypted         = true
  tags = {
    Name  = "User-Data-PROD"
    Env   = "Production"
    Owner = "Infrastructure-Team"
  }
}

# 2. THE ZOMBIE (No Owner, No Encryption - WASTE)
resource "aws_ebs_volume" "zombie_vol" {
  availability_zone = "us-east-1a"
  size              = 5
  encrypted         = false
  tags = {
    Name = "test-temporary-disk"
  }
}

# 3. THE SECURITY RISK (Production Env but NOT Encrypted - DANGER)
resource "aws_ebs_volume" "security_risk_vol" {
  availability_zone = "us-east-1a"
  size              = 50
  encrypted         = false
  tags = {
    Env  = "Production"
    Name = "Finance-Records-2025"
  }
}