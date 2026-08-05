output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  value = data.aws_region.current.region
}

output "resource_prefix" {
  value = local.resource_prefix
}

output "cloudfront_distribution_id" {
  value = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  value = module.cloudfront.domain_name
}

output "cloudfront_distribution_arn" {
  value = module.cloudfront.distribution_arn
}

output "certificate_arn" {
  value = module.acm.certificate_arn
}
