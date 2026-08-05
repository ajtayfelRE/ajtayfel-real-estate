variable "bucket_name" {
  description = "S3 bucket name used as CloudFront origin"
  type        = string
}

variable "bucket_arn" {
  description = "S3 bucket ARN"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN"
  type        = string
}

variable "aliases" {
  description = "Alternate domain names"
  type        = list(string)
  default     = []
}
