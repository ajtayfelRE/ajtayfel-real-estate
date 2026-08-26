locals {
  name_prefix = "${var.project_name}-${var.environment}-relocation-leads"
}

data "aws_caller_identity" "current" {}

resource "aws_dynamodb_table" "leads" {
  name         = local.name_prefix
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "lead_id"

  attribute {
    name = "lead_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Purpose = "Relocation lead storage"
  }
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = var.lambda_source_file
  output_path = "${path.root}/.terraform/relocation-lead-handler.zip"
}

resource "aws_iam_role" "lambda" {
  name = "${local.name_prefix}-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "dynamodb" {
  name = "${local.name_prefix}-dynamodb"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "dynamodb:PutItem"
        ]

        Resource = aws_dynamodb_table.leads.arn
      }
    ]
  })
}


resource "aws_iam_role_policy" "ses" {
  name = "${local.name_prefix}-ses"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ses:SendEmail"
        ]

        Resource = "arn:aws:ses:*:${data.aws_caller_identity.current.account_id}:identity/${var.notification_email}"
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name_prefix}"
  retention_in_days = 30
}

resource "aws_lambda_function" "lead_handler" {
  function_name = local.name_prefix

  role    = aws_iam_role.lambda.arn
  handler = "handler.lambda_handler"
  runtime = "python3.12"

  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  timeout     = 10
  memory_size = 128

  environment {
    variables = {
      TABLE_NAME   = aws_dynamodb_table.leads.name
      NOTIFY_EMAIL = var.notification_email
      FROM_EMAIL   = var.notification_email
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.lambda
  ]
}

resource "aws_apigatewayv2_api" "leads" {
  name          = "${local.name_prefix}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.allowed_origins

    allow_methods = [
      "POST",
      "OPTIONS"
    ]

    allow_headers = [
      "content-type"
    ]

    max_age = 300
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.leads.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lead_handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "relocation_lead" {
  api_id = aws_apigatewayv2_api.leads.id

  route_key = "POST /leads/relocation"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "contact_lead" {
  api_id = aws_apigatewayv2_api.leads.id

  route_key = "POST /leads/contact"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.leads.id

  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 10
    throttling_rate_limit  = 5
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id = "AllowExecutionFromApiGateway"

  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lead_handler.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.leads.execution_arn}/*/*"
}
