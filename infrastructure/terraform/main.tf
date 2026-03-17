locals {
  frontend_port = var.frontend_port
  admin_port    = var.admin_port
  api_port      = var.api_port
  network_name  = "elevatediq-network"
}

# Create Docker network for services
resource "docker_network" "main" {
  name   = local.network_name
