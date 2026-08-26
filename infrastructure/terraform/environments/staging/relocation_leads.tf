module "relocation_leads" {
  source = "../../modules/relocation_leads"

  project_name       = var.project_name
  environment        = var.environment
  notification_email = var.notification_email

  lambda_source_file = "${path.root}/../../../lambda/relocation_lead/handler.py"

  allowed_origins = [
    "https://ajtayfel.com",
    "https://www.ajtayfel.com",
    "http://localhost:4321"
  ]
}
