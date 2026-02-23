#!/usr/bin/env bash
#
# ElevatedIQ News Feed Engine - Environment Validation Script
# Validates required environment variables and configurations
#
# Usage: ./scripts/validate-env.sh
#
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "$1"; }
log_ok() { log "${GREEN}✓${NC} $1"; }
log_warn() { log "${YELLOW}⚠${NC} $1"; }
log_fail() { log "${RED}✗${NC} $1"; }

ERRORS=0
WARNINGS=0

check_required() {
    local var_name="$1"
    local description="$2"

    if [[ -z "${!var_name:-}" ]]; then
        log_fail "Missing required: $var_name - $description"
        ((ERRORS++))
    else
        log_ok "$var_name is set"
    fi
}

check_optional() {
    local var_name="$1"
    local description="$2"

    if [[ -z "${!var_name:-}" ]]; then
        log_warn "Missing optional: $var_name - $description"
        ((WARNINGS++))
    else
        log_ok "$var_name is set"
    fi
}

check_url() {
    local var_name="$1"
    local description="$2"

    local value="${!var_name:-}"
    if [[ -z "$value" ]]; then
        log_fail "Missing URL: $var_name - $description"
        ((ERRORS++))
    elif [[ ! "$value" =~ ^https?:// ]]; then
        log_warn "$var_name should start with http:// or https://"
        ((WARNINGS++))
    else
        log_ok "$var_name is valid URL"
    fi
}

log "ElevatedIQ News Feed Engine - Environment Validation"
log "====================================================="
log ""

# Database Configuration
log "Database Configuration:"
check_required "POSTGRES_DSN" "PostgreSQL connection string"
check_optional "MONGO_URI" "MongoDB connection URI"
check_required "REDIS_URL" "Redis connection URL"
log ""

# Kafka Configuration
log "Kafka Configuration:"
check_optional "KAFKA_BROKERS" "Kafka bootstrap servers"
check_optional "KAFKA_CONSUMER_GROUP" "Kafka consumer group"
log ""

# API Keys (Production)
log "API Keys:"
check_optional "YOUTUBE_API_KEY" "YouTube Data API key"
check_optional "TWITTER_BEARER_TOKEN" "Twitter API bearer token"
check_optional "CLAUDE_API_KEY" "Anthropic Claude API key"
check_optional "OPENAI_API_KEY" "OpenAI API key"
check_optional "ELEVENLABS_API_KEY" "ElevenLabs TTS API key"
check_optional "DID_API_KEY" "D-ID video generation API key"
log ""

# Security
log "Security Configuration:"
check_required "JWT_SECRET" "JWT signing secret"
check_optional "TOKEN_ENCRYPTION_KEY" "OAuth token encryption key"
log ""

# GCP
log "GCP Configuration:"
check_optional "GCP_PROJECT_ID" "GCP project for Secret Manager"
check_optional "GOOGLE_APPLICATION_CREDENTIALS" "GCP service account key path"
log ""

# CORS
log "CORS Configuration:"
check_optional "CORS_ALLOWED_ORIGINS" "Allowed CORS origins"
log ""

log ""
log "====================================================="
if [[ $ERRORS -gt 0 ]]; then
    log_fail "$ERRORS error(s), $WARNINGS warning(s)"
    log ""
    log "Fix the required variables before starting the service."
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    log_warn "0 errors, $WARNINGS warning(s)"
    log ""
    log "Some optional features may not work correctly."
    exit 0
else
    log_ok "All checks passed!"
    exit 0
fi
