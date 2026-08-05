data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  resource_prefix = "${var.project_name}-${var.environment}"
}

module "website_bucket" {
  source = "../../modules/s3"

  bucket_name = "${local.resource_prefix}-website"
  environment = var.environment
}
