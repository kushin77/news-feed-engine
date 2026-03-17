#!/bin/bash
# ELEVATEDIQ STAGING ENVIRONMENT
# Pre-production testing and validation

# Environment
export ELEVATEDIQ_ENV="staging"
export ELEVATEDIQ_DEBUG="false"

# Services Ports (standard)
export ELEVATEDIQ_NEWS_FEED_ENGINE_PORT=8080
export ELEVATEDIQ_PROCESSOR_PORT=5000
export ELEVATEDIQ_FRONTEND_PORT=3000
export ELEVATEDIQ_CONTENT_DISTRIBUTOR_PORT=8081

# Database (Cloud SQL or managed PostgreSQL)
export ELEVATEDIQ_DATABASE_HOST="${ELEVATEDIQ_DATABASE_HOST:-postgres-staging.c.elevatediq.iam.gserviceaccount.com}"
export ELEVATEDIQ_DATABASE_PORT=5432
export ELEVATEDIQ_DATABASE_NAME="elevatediq_staging"
export ELEVATEDIQ_DATABASE_USER="elevatediq_staging_sa"
export ELEVATEDIQ_NEWS_FEED_ENGINE_DATABASE_URL="postgresql://${ELEVATEDIQ_DATABASE_USER}:${ELEVATEDIQ_DATABASE_PASSWORD}@${ELEVATEDIQ_DATABASE_HOST}:${ELEVATEDIQ_DATABASE_PORT}/${ELEVATEDIQ_DATABASE_NAME}?sslmode=require"

# Cache (managed Redis)
export ELEVATEDIQ_REDIS_HOST="${ELEVATEDIQ_REDIS_HOST:-redis-staging.c.elevatediq.internal}"
export ELEVATEDIQ_REDIS_PORT=6379

# API Base URLs (staging domain)
export ELEVATEDIQ_API_BASE_URL="https://api-staging.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_FRONTEND_ORIGIN="https://staging.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_ADMIN_PORTAL_URL="https://admin-staging.${ELEVATEDIQ_DOMAIN}"

# Logging
export ELEVATEDIQ_LOG_LEVEL="info"
export ELEVATEDIQ_LOG_FORMAT="json"

# Security (staging-level, but enforced)
export ELEVATEDIQ_CORS_ORIGINS="https://staging.${ELEVATEDIQ_DOMAIN},https://admin-staging.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_TLS_ENABLED="true"
export ELEVATEDIQ_TLS_MIN_VERSION="1.2"
export ELEVATEDIQ_RATE_LIMIT_ENABLED="true"
export ELEVATEDIQ_RATE_LIMIT_RPS=100  # 100 requests/sec for testing

# Feature Flags (match production config for final validation)
export ELEVATEDIQ_FEATURE_NEW_UI="true"
export ELEVATEDIQ_FEATURE_ML_PIPELINE="true"
export ELEVATEDIQ_FEATURE_SOCIAL_DISTRIBUTION="true"

# Monitoring
export ELEVATEDIQ_METRICS_ENABLED="true"
export ELEVATEDIQ_TRACING_ENABLED="true"
export ELEVATEDIQ_METRICS_SCRAPE_INTERVAL="30s"
export ELEVATEDIQ_TRACING_SAMPLE_RATE="0.1"  # 10% sampling for cost control

# External Services (real API keys from Secret Manager)
export ELEVATEDIQ_SECRET_MANAGER_TYPE="gcp"
export ELEVATEDIQ_GCP_PROJECT_ID="elevatediq-staging"
export ELEVATEDIQ_ANTHROPIC_API_KEY_SECRET="projects/elevatediq-staging/secrets/anthropic-api-key/versions/latest"
export ELEVATEDIQ_ELEVENLABS_API_KEY_SECRET="projects/elevatediq-staging/secrets/elevenlabs-api-key/versions/latest"
export ELEVATEDIQ_DID_API_KEY_SECRET="projects/elevatediq-staging/secrets/did-api-key/versions/latest"

# Backups
export ELEVATEDIQ_BACKUP_ENABLED="true"
export ELEVATEDIQ_BACKUP_SCHEDULE="0 2 * * *"  # 2 AM daily

# Auto-scaling
export ELEVATEDIQ_AUTOSCALE_ENABLED="true"
export ELEVATEDIQ_AUTOSCALE_MIN_REPLICAS=2
export ELEVATEDIQ_AUTOSCALE_MAX_REPLICAS=5
export ELEVATEDIQ_AUTOSCALE_TARGET_CPU=70

echo "✓ ElevatedIQ staging environment loaded"
