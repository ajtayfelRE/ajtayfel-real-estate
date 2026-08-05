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


module "cloudfront" {
  source = "../../modules/cloudfront"

  bucket_name = module.website_bucket.bucket_name

  bucket_arn = module.website_bucket.bucket_arn

  environment = var.environment

  certificate_arn = module.acm.certificate_arn

  aliases = [
    "ajtayfel.com",
    "www.ajtayfel.com"
  ]
}

module "acm" {
  source = "../../modules/acm"

  providers = {
    aws = aws.us_east_1
  }

  domain_name = "ajtayfel.com"

  subject_alternative_names = [
    "www.ajtayfel.com"
  ]
}
resource "aws_s3_bucket_policy" "website" {

  bucket = module.website_bucket.bucket_name

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid = "AllowCloudFrontRead"

        Effect = "Allow"

        Principal = {
          Service = "cloudfront.amazonaws.com"
        }

        Action = [
          "s3:GetObject"
        ]

        Resource = "${module.website_bucket.bucket_arn}/*"

        Condition = {
          StringEquals = {
            "AWS:SourceArn" = module.cloudfront.distribution_arn
          }
        }
      }
    ]
  })
}
