#!/bin/bash
# NEWS FEED ENGINE DEPLOYMENT VERIFICATION SCRIPT
# Validates deployment readiness before go-live
# Usage: bash infrastructure/scripts/verify.sh --environment <production|staging|development>

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-development}"
VERBOSE="${VERBOSE:-false}"
FAILED_CHECKS=0
PASSED_CHECKS=0

# Logging
log_success() { echo -e "${GREEN}✓${NC} $1"; ((PASSED_CHECKS++)) || true; }
log_error() { echo -e "${RED}✗${NC} $1"; ((FAILED_CHECKS++)) || true; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_info() { echo -e "ℹ $1"; }

# Main verification
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 NEWS FEED ENGINE DEPLOYMENT VERIFICATION"
    echo "Environment: ${ENVIRONMENT}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Load environment
    verify_environment_setup
    
    # Security checks
    verify_security
    
    # Infrastructure checks
    verify_infrastructure
    
    # Application checks
    verify_applications
    
    # Data checks
    verify_data
    
    # Performance baseline
    verify_performance
    
    # Report
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 VERIFICATION SUMMARY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Passed: ${GREEN}${PASSED_CHECKS}${NC}"
    echo -e "Failed: ${RED}${FAILED_CHECKS}${NC}"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ ALL CHECKS PASSED - READY FOR DEPLOYMENT${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}✗ DEPLOYMENT BLOCKED - FIX FAILURES ABOVE${NC}"
        return 1
    fi
}

verify_environment_setup() {
    echo "📋 ENVIRONMENT SETUP"
    
    # Check environment variables
    if [ -z "${ELEVATEDIQ_ENV:-}" ]; then
        log_error "ELEVATEDIQ_ENV not set"
    else
        log_success "ELEVATEDIQ_ENV = ${ELEVATEDIQ_ENV}"
    fi
    
    # Check required tools
    for tool in docker docker-compose terraform git; do
        if command -v $tool &> /dev/null; then
            log_success "$tool installed"
        else
            log_error "$tool not found"
        fi
    done
    
    # Check git status
    if [ -z "$(git status --porcelain)" ]; then
        log_success "Git working directory clean"
    else
        log_warning "Git working directory has uncommitted changes"
    fi
}

verify_security() {
    echo ""
    echo "🔒 SECURITY VERIFICATION"
    
    # Check no hardcoded secrets
    if grep -r "password\|secret\|api_key\|token" services/node-modules --include="*.js" --include="*.ts" 2>/dev/null | grep -E "=\s*['\"]" | head -5 &>/dev/null; then
        log_error "Potential hardcoded secrets found in code"
    else
        log_success "No obvious hardcoded secrets detected"
    fi
    
    # Check .env files not in git
    if [ -f ".env" ] || [ -f ".env.local" ] || [ -f ".env.production" ]; then
        log_error ".env files found (should be in Secret Manager)"
    else
        log_success "No .env files in repository"
    fi
    
    # Check SSL certificates
    if [ -f "infrastructure/certs/tls.crt" ]; then
        expiry=$(openssl x509 -enddate -noout -in infrastructure/certs/tls.crt 2>/dev/null | cut -d= -f2)
        expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || echo 0)
        now_epoch=$(date +%s)
        days_until_expiry=$(( ($expiry_epoch - $now_epoch) / 86400 ))
        
        if [ $days_until_expiry -gt 30 ]; then
            log_success "TLS certificate valid for $days_until_expiry more days"
        else
            log_error "TLS certificate expiring in $days_until_expiry days (must be >30)"
        fi
    fi
}

verify_infrastructure() {
    echo ""
    echo "🏗️  INFRASTRUCTURE VERIFICATION"
    
    # Check Docker
    if docker ps &>/dev/null; then
        log_success "Docker daemon running"
    else
        log_error "Docker daemon not accessible"
    fi
    
    # Check services can be built
    if docker-compose config -f infrastructure/docker/news-feed.yml &>/dev/null; then
        log_success "docker-compose configuration valid"
    else
        log_error "docker-compose configuration invalid"
    fi
    
    # Check Terraform
    if cd infrastructure/terraform && terraform validate &>/dev/null; then
        log_success "Terraform configuration valid"
        cd - &>/dev/null
    else
        log_error "Terraform configuration invalid"
        cd - &>/dev/null
    fi
}

verify_applications() {
    echo ""
    echo "📱 APPLICATION VERIFICATION"
    
    # Check frontend build
    if [ -f "services/frontend/package.json" ]; then
        if npm run build --prefix services/frontend --dry-run &>/dev/null; then
            log_success "Frontend build configuration valid"
        else
            log_warning "Frontend build needs npm install"
        fi
    fi
    
    # Check backend binary
    if [ -f "services/news-feed-engine/bin/news-feed-engine" ]; then
        log_success "Backend binary exists"
    else
        log_warning "Backend binary not built (will build on deploy)"
    fi
}

verify_data() {
    echo ""
    echo "💾 DATA VERIFICATION"
    
    # Check database schema files
    if [ -d "services/news-feed-engine/migrations" ]; then
        count=$(find services/news-feed-engine/migrations -name "*.sql" | wc -l)
        log_success "$count database migrations found"
    else
        log_warning "Database migrations directory not found"
    fi
}

verify_performance() {
    echo ""
    echo "⚡ PERFORMANCE BASELINE"
    
    # Frontend bundle size check
    if [ -d "services/frontend/dist" ]; then
        size=$(du -sh services/frontend/dist | cut -f1)
        log_info "Frontend bundle size: $size"
    fi
    
    # Check for performance bottlenecks
    if grep -r "sleep\|delay\|timeout" services/news-feed-engine/internal --include="*.go" 2>/dev/null | head -3; then
        log_warning "Found potential performance issues (hardcoded delays)"
    fi
}

# Run verification
main
exit $?
