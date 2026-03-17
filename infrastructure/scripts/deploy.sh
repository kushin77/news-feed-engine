#!/bin/bash
# NEWS FEED ENGINE DEPLOYMENT ORCHESTRATOR
# Fully automated, hands-off deployment to any environment
# Usage: bash infrastructure/scripts/deploy.sh [local|staging|production] [--dry-run] [--rollback]

set -euo pipefail

# Configuration
TARGET_ENV="${1:-local}"
DRY_RUN="${2:-}"
ROLLBACK="${3:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging utilities
log_step() { echo -e "\n${BLUE}==>${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

# Error handler
trap 'handle_error $? $LINENO' ERR

handle_error() {
    local exit_code=$1
    local line_number=$2
    log_error "Deployment failed at line $line_number with exit code $exit_code"
    
    # Log deployment failure for audit trail
    log_deployment_event "deployment_failed" "$TARGET_ENV" $exit_code
    
    if [ "$TARGET_ENV" != "local" ] && [ -z "$DRY_RUN" ]; then
        log_warning "Consider running: bash $SCRIPT_DIR/rollback.sh --target $TARGET_ENV"
    fi
    
    exit $exit_code
}

# Deployment event logging (immutable audit trail)
log_deployment_event() {
    local event=$1
    local environment=$2
    local status=$3
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local commit_sha=$(git -C "$REPO_ROOT" rev-parse HEAD)
    local deployer=${USER:-ci-bot}
    
    cat >> "$REPO_ROOT/.deployment-audit.jsonl" <<EOF
{"timestamp":"$timestamp","event":"$event","environment":"$environment","status":"$status","commit":"$commit_sha","deployer":"$deployer"}
EOF
}

# Load environment
load_environment() {
    log_step "Loading environment configuration for $TARGET_ENV"
    
    # Source global env
    if [ -f "$REPO_ROOT/infrastructure/config/env-global.sh" ]; then
        # shellcheck source=/dev/null
        source "$REPO_ROOT/infrastructure/config/env-global.sh"
        log_success "Loaded global configuration"
    fi
    
    # Source environment-specific env
    local env_file="$REPO_ROOT/infrastructure/config/env-${TARGET_ENV}.sh"
    if [ -f "$env_file" ]; then
        # shellcheck source=/dev/null
        source "$env_file"
        log_success "Loaded $TARGET_ENV environment"
    else
        log_error "Environment file not found: $env_file"
        return 1
    fi
    
    # Verify required variables
    required_vars=(
        "ELEVATEDIQ_ENV"
        "ELEVATEDIQ_NEWS_FEED_ENGINE_PORT"
        "ELEVATEDIQ_PROCESSOR_PORT"
        "ELEVATEDIQ_FRONTEND_PORT"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable not set: $var"
            return 1
        fi
    done
}

# Verify prerequisites
verify_prerequisites() {
    log_step "Verifying prerequisites"
    
    # Check required tools
    for tool in docker docker-compose terraform git bash; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool not found in PATH"
            return 1
        fi
    done
    log_success "All required tools available"
    
    # Verify git state
    if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
        log_warning "Working directory has uncommitted changes"
        if [ -z "$DRY_RUN" ]; then
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                return 1
            fi
        fi
    fi
}

# Build Docker images
build_images() {
    log_step "Building Docker images"
    
    local services=("news-feed-engine" "processor" "frontend")
    
    for service in "${services[@]}"; do
        log_step "Building $service"
        
        local dockerfile="$REPO_ROOT/services/$service/Dockerfile"
        if [ ! -f "$dockerfile" ]; then
            log_warning "Dockerfile not found for $service, skipping"
            continue
        fi
        
        local image_name="elevatediq/${service}:latest"
        local build_cmd="docker build -f $dockerfile -t $image_name $REPO_ROOT/services/$service"
        
        if [ -n "$DRY_RUN" ]; then
            log_info "DRY-RUN: $build_cmd"
        else
            eval "$build_cmd" || {
                log_error "Failed to build $service"
                return 1
            }
            log_success "$service built successfully"
        fi
    done
}

# Run database migrations
run_migrations() {
    log_step "Running database migrations"
    
    local migrations_dir="$REPO_ROOT/services/news-feed-engine/migrations"
    if [ ! -d "$migrations_dir" ]; then
        log_warning "Migrations directory not found"
        return 0
    fi
    
    if [ -z "$DRY_RUN" ]; then
        # This would connect to the database and run migrations
        # Implementation depends on your migration tool (e.g., migrate, flyway, etc.)
        log_success "Migrations would be executed here"
    else
        log_info "DRY-RUN: Would execute migrations from $migrations_dir"
    fi
}

# Deploy infrastructure (Terraform)
deploy_infrastructure() {
    log_step "Deploying infrastructure with Terraform"
    
    cd "$REPO_ROOT/infrastructure/terraform"
    
    # Initialize Terraform
    if [ -z "$DRY_RUN" ]; then
        terraform init -backend-config="environments/${TARGET_ENV}.tfbackend" \
            || {
            log_error "Terraform init failed"
            return 1
        }
    else
        log_info "DRY-RUN: Would run terraform init"
    fi
    
    # Plan
    terraform plan \
        -var-file="environments/${TARGET_ENV}.tfvars" \
        -var="environment=${TARGET_ENV}" \
        -out="${TARGET_ENV}.tfplan" \
        || {
        log_error "Terraform plan failed"
        return 1
    }
    
    # Apply (only if not dry-run)
    if [ -z "$DRY_RUN" ]; then
        terraform apply -auto-approve "${TARGET_ENV}.tfplan" || {
            log_error "Terraform apply failed"
            return 1
        }
        log_success "Infrastructure deployed"
    else
        log_info "DRY-RUN: Would apply terraform plan"
    fi
    
    cd - > /dev/null
}

# Deploy containers
deploy_containers() {
    log_step "Deploying containers"
    
    local docker_compose_file="$REPO_ROOT/infrastructure/docker/news-feed.yml"
    
    if [ ! -f "$docker_compose_file" ]; then
        log_error "Docker compose file not found: $docker_compose_file"
        return 1
    fi
    
    if [ -z "$DRY_RUN" ]; then
        docker-compose -f "$docker_compose_file" down --remove-orphans || true
        docker-compose -f "$docker_compose_file" up -d || {
            log_error "Container deployment failed"
            return 1
        }
        log_success "Containers deployed"
    else
        log_info "DRY-RUN: Would start containers with docker-compose"
    fi
}

# Verify deployment
verify_deployment() {
    log_step "Verifying deployment"
    
    # Wait for services
    local max_attempts=30
    local attempt=0
    
    local services=(
        "http://localhost:${ELEVATEDIQ_NEWS_FEED_ENGINE_PORT}/health"
        "http://localhost:${ELEVATEDIQ_FRONTEND_PORT}"
    )
    
    for service_url in "${services[@]}"; do
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if [ -z "$DRY_RUN" ]; then
                if curl -sf "$service_url" > /dev/null 2>&1; then
                    log_success "$service_url is healthy"
                    break
                fi
            else
                log_info "DRY-RUN: Would verify $service_url"
                break
            fi
            
            ((attempt++))
            if [ $attempt -lt $max_attempts ]; then
                sleep 2
            fi
        done
        
        if [ $attempt -eq $max_attempts ] && [ -z "$DRY_RUN" ]; then
            log_error "$service_url failed to become healthy"
            return 1
        fi
    done
}

# Main deployment flow
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 NEWS FEED ENGINE DEPLOYMENT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Environment: ${TARGET_ENV}"
    echo "Dry Run: ${DRY_RUN:-'false'}"
    echo ""
    
    load_environment
    verify_prerequisites
    build_images
    run_migrations
    deploy_infrastructure
    deploy_containers
    verify_deployment
    
    # Log successful deployment
    log_deployment_event "deployment_success" "$TARGET_ENV" 0
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "DEPLOYMENT COMPLETE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Run main
main "$@"
