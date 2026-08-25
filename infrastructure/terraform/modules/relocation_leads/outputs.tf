output "api_endpoint" {
  description = "Base URL for the relocation lead API."
  value       = aws_apigatewayv2_api.leads.api_endpoint
}

output "table_name" {
  description = "DynamoDB relocation lead table."
  value       = aws_dynamodb_table.leads.name
}

output "lambda_function_name" {
  description = "Lambda function processing relocation leads."
  value       = aws_lambda_function.lead_handler.function_name
}
