locals {
  frontend_port = var.frontend_port
  admin_port    = var.admin_port
  api_port      = var.api_port
  network_name  = "elevatediq-network"
}

# Create Docker network for services
resource "docker_network" "main" {
  name   = local.network_name
  driver = "bridge"
}

# Build frontend image
resource "docker_image" "frontend" {
  name         = "elevatediq-frontend:latest"
  build {
    context    = "../.."
    dockerfile = "services/frontend/Dockerfile"
  }
  depends_on = [docker_network.main]
}

# Run frontend container
resource "docker_container" "frontend" {
  name  = "elevatediq-frontend"
  image = docker_image.frontend.image_id

  ports {
    internal = 8080
    external = local.frontend_port
  }

  networks_advanced {
    name = docker_network.main.name
  }

  restart_policy {
    condition = "unless-stopped"
  }

  depends_on = [docker_image.frontend]
}

# Appsmith container for admin portal (from official image)
resource "docker_image" "appsmith" {
  name = "appsmith/appsmith:latest"
}

resource "docker_container" "appsmith" {
  count = var.enable_admin_portal ? 1 : 0
  name  = "elevatediq-appsmith"
  image = docker_image.appsmith.image_id

  ports {
    internal = 80
    external = local.admin_port
  }

  networks_advanced {
    name = docker_network.main.name
  }

  env = [
    "APPSMITH_DISABLE_TELEMETRY=true",
    "APPSMITH_ENCRYPTION_SALT=${var.appsmith_encryption_salt}",
    "APPSMITH_ENCRYPTION_PASSWORD=${var.appsmith_encryption_password}"
  ]

  restart_policy {
    condition = "unless-stopped"
  }

  depends_on = [docker_image.appsmith]
}
