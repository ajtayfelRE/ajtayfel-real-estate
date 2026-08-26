variable "aws_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be staging or production."
  }
}

variable "project_name" {
  description = "Project identifier used for resource names"
  type        = string
  default     = "ajtayfel-real-estate"
}

variable "notification_email" {
  description = "Verified SES email used for relocation lead notifications."
  type        = string
  sensitive   = true
}
