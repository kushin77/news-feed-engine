output "frontend_url" {
  description = "URL to access the frontend"
  value       = "http://192.168.168.23:${var.frontend_port}"
}

output "frontend_url_local" {
  description = "Local URL to access the frontend"
  value       = "http://localhost:${var.frontend_port}"
}

output "admin_portal_url" {
  description = "URL to access the admin portal"
  value       = var.enable_admin_portal ? "http://192.168.168.23:${var.admin_port}" : "Admin portal disabled"
}

output "admin_portal_url_local" {
  description = "Local URL to access the admin portal"
  value       = var.enable_admin_portal ? "http://localhost:${var.admin_port}" : "Admin portal disabled"
}

output "docker_network" {
  description = "Docker network name"
  value       = docker_network.main.name
}

output "frontend_container_id" {
  description = "Frontend container ID"
  value       = docker_container.frontend.id
}

output "access_instructions" {
  description = "How to access the services from other PCs"
  value = <<-EOT
    From another PC on the WiFi network (192.168.168.x):
    - Frontend: http://192.168.168.23:${var.frontend_port}
    - Admin Portal: http://192.168.168.23:${var.admin_port}
    
    From this PC:
    - Frontend: http://localhost:${var.frontend_port}
    - Admin Portal: http://localhost:${var.admin_port}
    
    To view running containers:
      terraform state list
      docker ps
    
    To stop services:
      terraform destroy
  EOT
}
