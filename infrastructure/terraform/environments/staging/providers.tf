provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AJ Tayfel Real Estate"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "AJ Tayfel"
    }
  }
}
