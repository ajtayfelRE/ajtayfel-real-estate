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


provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "AJ Tayfel Real Estate"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "AJ Tayfel"
    }
  }
}
