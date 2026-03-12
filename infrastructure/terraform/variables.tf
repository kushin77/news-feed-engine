variable "frontend_port" {
  description = "Port to expose frontend on (8080 is default, 80 requires admin)"
  type        = number
  default     = 8080
}

variable "admin_port" {
  description = "Port to expose Appsmith admin portal on"
  type        = number
  default     = 3000
}

variable "api_port" {
  description = "Port to expose API backend on"
  type        = number
  default     = 8000
}

variable "enable_admin_portal" {
  description = "Enable Appsmith admin portal"
  type        = bool
  default     = true
}

variable "appsmith_encryption_salt" {
  description = "Encryption salt for Appsmith (generate with: openssl rand -base64 32)"
  type        = string
  sensitive   = true
  default     = "default-salt-change-me"
}

variable "appsmith_encryption_password" {
  description = "Encryption password for Appsmith"
  type        = string
  sensitive   = true
  default     = "default-password-change-me"
}

variable "enable_observability" {
  description = "Enable Prometheus and Grafana"
  type        = bool
  default     = false
}

variable "local_network_listen" {
  description = "Listen on all network interfaces (0.0.0.0) instead of localhost"
  type        = bool
  default     = true
}
