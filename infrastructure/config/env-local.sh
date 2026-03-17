#!/bin/bash
# ELEVATEDIQ LOCAL DEVELOPMENT ENVIRONMENT
# For local development, testing, and debugging

# Environment
export ELEVATEDIQ_ENV="development"
export ELEVATEDIQ_DEBUG="${ELEVATEDIQ_DEBUG:-true}"

# Services Ports
export ELEVATEDIQ_NEWS_FEED_ENGINE_PORT=8080
export ELEVATEDIQ_PROCESSOR_PORT=5000
export ELEVATEDIQ_FRONTEND_PORT=3000
export ELEVATEDIQ_CONTENT_DISTRIBUTOR_PORT=8081
export ELEVATEDIQ_PROMETHEUS_PORT=9090
export ELEVATEDIQ_GRAFANA_PORT=3001
export ELEVATEDIQ_ADMIN_PORTAL_PORT=8082

# Database (local PostgreSQL)
export ELEVATEDIQ_DATABASE_HOST="localhost"
export ELEVATEDIQ_DATABASE_PORT=5432
export ELEVATEDIQ_DATABASE_NAME="elevatediq_dev"
export ELEVATEDIQ_DATABASE_USER="elevatediq_dev"
export ELEVATEDIQ_NEWS_FEED_ENGINE_DATABASE_URL="postgresql://${ELEVATEDIQ_DATABASE_USER}:${ELEVATEDIQ_DATABASE_PASSWORD}@${ELEVATEDIQ_DATABASE_HOST}:${ELEVATEDIQ_DATABASE_PORT}/${ELEVATEDIQ_DATABASE_NAME}"

# Cache (local Redis)
export ELEVATEDIQ_REDIS_HOST="localhost"
export ELEVATEDIQ_REDIS_PORT=6379
export ELEVATEDIQ_REDIS_PASSWORD=""

# API Base URLs (local)
export ELEVATEDIQ_API_BASE_URL="http://localhost:${ELEVATEDIQ_NEWS_FEED_ENGINE_PORT}"
export ELEVATEDIQ_FRONTEND_ORIGIN="http://localhost:${ELEVATEDIQ_FRONTEND_PORT}"

# Logging
export ELEVATEDIQ_LOG_LEVEL="debug"
export ELEVATEDIQ_LOG_FORMAT="text"  # Human-readable for development

# Security (permissive for local dev)
export ELEVATEDIQ_JWT_SECRET="dev-secret-do-not-use-in-production"
export ELEVATEDIQ_CORS_ORIGINS="*"
export ELEVATEDIQ_TLS_ENABLED="false"
export ELEVATEDIQ_RATE_LIMIT_ENABLED="false"

# Feature Flags (all enabled for local testing)
export ELEVATEDIQ_FEATURE_NEW_UI="true"
export ELEVATEDIQ_FEATURE_ML_PIPELINE="true"
export ELEVATEDIQ_FEATURE_SOCIAL_DISTRIBUTION="true"

# Monitoring (disabled for local dev to reduce noise)
export ELEVATEDIQ_METRICS_ENABLED="true"
export ELEVATEDIQ_TRACING_ENABLED="false"
export ELEVATEDIQ_PROFILING_ENABLED="true"

# External Services (stub/mock for local dev)
export ELEVATEDIQ_ANTHROPIC_API_KEY="${ELEVATEDIQ_ANTHROPIC_API_KEY:-sk-test-key-for-local-dev}"
export ELEVATEDIQ_ELEVENLABS_API_KEY="${ELEVATEDIQ_ELEVENLABS_API_KEY:-test-key-for-local-dev}"
export ELEVATEDIQ_DID_API_KEY="${ELEVATEDIQ_DID_API_KEY:-test-key-for-local-dev}"
export ELEVATEDIQ_SECRET_MANAGER_TYPE="local"  # Use local .env instead of GCP for dev

echo "✓ ElevatedIQ local development environment loaded"
