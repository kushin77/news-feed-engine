# Terraform Infrastructure for ElevatedIQ

This directory contains Terraform configuration to manage the ElevatedIQ infrastructure using Docker containers.

## Prerequisites

- Terraform >= 1.0
- Docker Desktop (running)
- Kreuzwerker Docker provider

## Quick Start

### 1. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 2. Review the Plan

```bash
terraform plan
```

### 3. Apply Infrastructure

```bash
terraform apply
```

Terraform will create:
- Docker network (`elevatediq-network`)
- Frontend container (port 8080)
- Appsmith admin portal (port 3000)

## Accessing Services

### From this PC
- **Frontend**: http://localhost:8080
- **Admin Portal**: http://localhost:3000

### From other PCs on the WiFi
- **Frontend**: http://192.168.168.23:8080
- **Admin Portal**: http://192.168.168.23:3000

Replace `192.168.168.23` with your actual IP if different.

## Configuration

Edit `terraform.tfvars` to customize:
- `frontend_port` - Port for frontend (default: 8080)
- `admin_port` - Port for admin/Appsmith (default: 3000)
- `enable_admin_portal` - Toggle admin portal (default: true)
- `enable_observability` - Toggle monitoring stack (default: false)

## Managing Services

### View Infrastructure

```bash
terraform state list
terraform show
docker ps
```

### Update a Service

```bash
terraform apply
```

### Destroy Everything

```bash
terraform destroy
```

## Environment Variables

For sensitive values, use Terraform environment variables:

```bash
# Windows PowerShell
$env:TF_VAR_appsmith_encryption_salt = "your-salt-value"
$env:TF_VAR_appsmith_encryption_password = "your-password"

# Or create terraform.auto.tfvars (add to .gitignore)
# frontend_port = 8080
# appsmith_encryption_salt = "..."
# appsmith_encryption_password = "..."
```

## Troubleshooting

### Docker not found
Ensure Docker Desktop is running: `docker ps`

### Port already in use
Change the port in `terraform.tfvars`:
```hcl
frontend_port = 8081
admin_port = 3001
```

### Containers won't start
Check Docker logs:
```bash
docker logs elevatediq-frontend
docker logs elevatediq-appsmith
```

## Next Steps

- [ ] Add news-feed-engine API container
- [ ] Add processor service
- [ ] Add observability stack (Prometheus, Grafana)
- [ ] Add load balancing with Traefik
- [ ] Set up remote state backend (if needed)

## References

- [Terraform Docker Provider](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs)
- [Docker Compose vs Terraform](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs/guides/migration)
