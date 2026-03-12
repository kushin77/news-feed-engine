# Local Development Configuration
frontend_port       = 8080
admin_port          = 3000
api_port            = 8000
enable_admin_portal = true
enable_observability = false

# For sensitive values, use environment variables:
# export TF_VAR_appsmith_encryption_salt="<base64-value>"
# export TF_VAR_appsmith_encryption_password="<password>"
# Or set them in a separate terraform.auto.tfvars file (NOT in git)
