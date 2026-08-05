variable "bucket_name" {
  description = "S3 bucket name used as CloudFront origin"
  type        = string
}

variable "bucket_arn" {
  description = "S3 bucket ARN used for permissions"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}
