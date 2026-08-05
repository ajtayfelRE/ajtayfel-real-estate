output "aws_account_id" {
  description = "AWS account used by this environment"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "AWS region used by this environment"
  value       = data.aws_region.current.region
}

output "resource_prefix" {
  description = "Prefix that will be used for staging resources"
  value       = local.resource_prefix
}
