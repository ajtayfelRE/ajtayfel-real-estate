variable "project_name" {
  description = "Project identifier used in AWS resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "lambda_source_file" {
  description = "Path to the Python Lambda source file."
  type        = string
}

variable "allowed_origins" {
  description = "Origins permitted by API Gateway CORS."
  type        = list(string)
}
