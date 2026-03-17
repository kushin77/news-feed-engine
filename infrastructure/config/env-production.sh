#!/bin/bash
# ELEVATEDIQ PRODUCTION ENVIRONMENT
# ⚠️  CRITICAL INFRASTRUCTURE - HANDLE WITH CARE
# All secrets fetched from GCP Secret Manager at runtime

# Environment
export ELEVATEDIQ_ENV="production"
export ELEVATEDIQ_DEBUG="false"
export ELEVATEDIQ_REQUIRE_AUTHENTICATION="true"
export ELEVATEDIQ_ENFORCE_HTTPS="true"

# Services Ports (standard, behind load balancer)
export ELEVATEDIQ_NEWS_FEED_ENGINE_PORT=8080
export ELEVATEDIQ_PROCESSOR_PORT=5000
export ELEVATEDIQ_FRONTEND_PORT=3000
export ELEVATEDIQ_CONTENT_DISTRIBUTOR_PORT=8081

# Database (managed multi-zone PostgreSQL with automatic failover)
export ELEVATEDIQ_DATABASE_HOST="${ELEVATEDIQ_DATABASE_HOST:-postgres-prod.us-central1.database.elevatediq.ai}"
export ELEVATEDIQ_DATABASE_PORT=5432
export ELEVATEDIQ_DATABASE_NAME="elevatediq_prod"
export ELEVATEDIQ_DATABASE_USER="elevatediq_prod_sa"
export ELEVATEDIQ_DATABASE_SSL_MODE="require"
export ELEVATEDIQ_NEWS_FEED_ENGINE_DATABASE_URL="postgresql://${ELEVATEDIQ_DATABASE_USER}:${ELEVATEDIQ_DATABASE_PASSWORD}@${ELEVATEDIQ_DATABASE_HOST}:${ELEVATEDIQ_DATABASE_PORT}/${ELEVATEDIQ_DATABASE_NAME}?sslmode=require&application_name=elevatediq-feed"
export ELEVATEDIQ_DATABASE_POOL_SIZE=50
export ELEVATEDIQ_DATABASE_MAX_IDLE_CONNECTIONS=10
export ELEVATEDIQ_DATABASE_CONNECTION_TIMEOUT=30

# Cache (managed Redis cluster with replication)
export ELEVATEDIQ_REDIS_HOST="${ELEVATEDIQ_REDIS_HOST:-redis-prod.us-central1.cache.elevatediq.ai}"
export ELEVATEDIQ_REDIS_PORT=6379
export ELEVATEDIQ_REDIS_SSL="true"
export ELEVATEDIQ_REDIS_REPLICA_HOST="${ELEVATEDIQ_REDIS_REPLICA_HOST:-redis-prod-replica.us-central1.cache.elevatediq.ai}"
export ELEVATEDIQ_REDIS_REPLICA_PORT=6379

# API Base URLs (production domain, behind CDN)
export ELEVATEDIQ_API_BASE_URL="https://api.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_FRONTEND_ORIGIN="https://${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_ADMIN_PORTAL_URL="https://admin.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_CDN_URL="https://cdn.${ELEVATEDIQ_DOMAIN}"

# Logging (centralized, immutable, audit trail)
export ELEVATEDIQ_LOG_LEVEL="info"
export ELEVATEDIQ_LOG_FORMAT="json"
export ELEVATEDIQ_LOG_DESTINATION="stackdriver"  # Google Cloud Logging
export ELEVATEDIQ_LOG_RETENTION_DAYS=90
export ELEVATEDIQ_AUDIT_LOG_ENABLED="true"
export ELEVATEDIQ_AUDIT_LOG_RETENTION_DAYS=365

# Security (maximum enforcement)
export ELEVATEDIQ_CORS_ORIGINS="https://${ELEVATEDIQ_DOMAIN},https://admin.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_CORS_METHODS="GET,POST,PUT,DELETE"
export ELEVATEDIQ_CORS_MAX_AGE=3600
export ELEVATEDIQ_TLS_ENABLED="true"
export ELEVATEDIQ_TLS_MIN_VERSION="1.3"
export ELEVATEDIQ_TLS_CERT_PATH="/secrets/tls/cert.pem"
export ELEVATEDIQ_TLS_KEY_PATH="/secrets/tls/key.pem"
export ELEVATEDIQ_CIPHERSUITES="TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256"
export ELEVATEDIQ_HSTS_ENABLED="true"
export ELEVATEDIQ_HSTS_MAX_AGE=31536000
export ELEVATEDIQ_HSTS_INCLUDE_SUBDOMAINS="true"
export ELEVATEDIQ_HSTS_PRELOAD="true"

# API Security
export ELEVATEDIQ_JWT_ALGORITHM="RS256"  # Asymmetric signing
export ELEVATEDIQ_JWT_ISSUER="https://auth.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_JWT_AUDIENCE="api.${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_JWT_EXPIRATION=3600  # 1 hour
export ELEVATEDIQ_JWT_REFRESH_EXPIRATION=2592000  # 30 days (via Secret Manager)
export ELEVATEDIQ_JWT_KEY_ROTATION_ENABLED="true"
export ELEVATEDIQ_JWT_KEY_ROTATION_INTERVAL=86400  # Daily

# Rate Limiting (DDoS protection)
export ELEVATEDIQ_RATE_LIMIT_ENABLED="true"
export ELEVATEDIQ_RATE_LIMIT_RPS_GLOBAL=10000  # Global 10k req/sec
export ELEVATEDIQ_RATE_LIMIT_RPS_PER_IP=100    # Per IP 100 req/sec
export ELEVATEDIQ_RATE_LIMIT_RPS_PER_USER=500  # Per authenticated user 500 req/sec
export ELEVATEDIQ_RATE_LIMIT_BURST_SIZE=50     # Allow bursts up to 50 requests
export ELEVATEDIQ_RATE_LIMIT_BACKEND="redis"   # Distributed rate limiting

# Encryption
export ELEVATEDIQ_ENCRYPTION_ENABLED="true"
export ELEVATEDIQ_ENCRYPTION_ALGORITHM="AES-256-GCM"
export ELEVATEDIQ_ENCRYPTION_KEY_ROTATION_DAYS=90

# Feature Flags (production-approved set)
export ELEVATEDIQ_FEATURE_NEW_UI="true"
export ELEVATEDIQ_FEATURE_ML_PIPELINE="true"
export ELEVATEDIQ_FEATURE_SOCIAL_DISTRIBUTION="true"
export ELEVATEDIQ_FEATURE_ANALYTICS="true"
export ELEVATEDIQ_FEATURE_PREMIUM_TIER="true"

# Monitoring & Observability
export ELEVATEDIQ_METRICS_ENABLED="true"
export ELEVATEDIQ_METRICS_SCRAPE_INTERVAL="15s"
export ELEVATEDIQ_TRACING_ENABLED="true"
export ELEVATEDIQ_TRACING_SAMPLE_RATE="0.01"  # 1% sampling for high-volume production
export ELEVATEDIQ_PROFILING_ENABLED="false"   # Disable continuous profiling in production
export ELEVATEDIQ_HEALTH_CHECK_INTERVAL=30
export ELEVATEDIQ_HEALTH_CHECK_TIMEOUT=5

# External Services (ALL from Secret Manager - NEVER inline)
export ELEVATEDIQ_SECRET_MANAGER_TYPE="gcp"
export ELEVATEDIQ_GCP_PROJECT_ID="elevatediq-prod"
export ELEVATEDIQ_GCP_KMS_KEY_RING="projects/elevatediq-prod/locations/us-central1/keyRings/elevatediq"
export ELEVATEDIQ_GCP_KMS_KEY="projects/elevatediq-prod/locations/us-central1/keyRings/elevatediq/cryptoKeys/application-key"
# Secrets are fetched at container startup via service account credentials
export ELEVATEDIQ_ANTHROPIC_API_KEY_SECRET="projects/elevatediq-prod/secrets/anthropic-api-key/versions/latest"
export ELEVATEDIQ_ELEVENLABS_API_KEY_SECRET="projects/elevatediq-prod/secrets/elevenlabs-api-key/versions/latest"
export ELEVATEDIQ_DID_API_KEY_SECRET="projects/elevatediq-prod/secrets/did-api-key/versions/latest"
export ELEVATEDIQ_DATABASE_PASSWORD_SECRET="projects/elevatediq-prod/secrets/db-password/versions/latest"
export ELEVATEDIQ_REDIS_PASSWORD_SECRET="projects/elevatediq-prod/secrets/redis-password/versions/latest"
export ELEVATEDIQ_JWT_PRIVATE_KEY_SECRET="projects/elevatediq-prod/secrets/jwt-private-key/versions/latest"
export ELEVATEDIQ_JWT_PUBLIC_KEY_SECRET="projects/elevatediq-prod/secrets/jwt-public-key/versions/latest"

# Backup & Disaster Recovery
export ELEVATEDIQ_BACKUP_ENABLED="true"
export ELEVATEDIQ_BACKUP_SCHEDULE="0 1 * * *"  # 1 AM UTC daily
export ELEVATEDIQ_BACKUP_RETENTION_DAYS=30
export ELEVATEDIQ_BACKUP_DESTINATION="gs://elevatediq-prod-backups"
export ELEVATEDIQ_BACKUP_ENCRYPTION="true"
export ELEVATEDIQ_BACKUP_VERIFY_ENABLED="true"  # Verify backup integrity daily
export ELEVATEDIQ_DISASTER_RECOVERY_RTO=1  # Recovery Time Objective: 1 hour
export ELEVATEDIQ_DISASTER_RECOVERY_RPO=15  # Recovery Point Objective: 15 minutes

# Auto-scaling & High Availability
export ELEVATEDIQ_AUTOSCALE_ENABLED="true"
export ELEVATEDIQ_AUTOSCALE_MIN_REPLICAS=3      # Minimum 3 for HA
export ELEVATEDIQ_AUTOSCALE_MAX_REPLICAS=20     # Scale to 20 for peak loads
export ELEVATEDIQ_AUTOSCALE_TARGET_CPU=70
export ELEVATEDIQ_AUTOSCALE_TARGET_MEMORY=75
export ELEVATEDIQ_AUTOSCALE_SCALE_UP_PERCENT=50  # Scale up 50% workload increase
export ELEVATEDIQ_AUTOSCALE_SCALE_DOWN_COOLDOWN=300  # 5 min cooldown

# Load Balancing
export ELEVATEDIQ_LOAD_BALANCER_TYPE="application"  # Layer 7 aware
export ELEVATEDIQ_LOAD_BALANCER_ALGORITHM="round_robin"
export ELEVATEDIQ_CIRCUIT_BREAKER_ENABLED="true"
export ELEVATEDIQ_CIRCUIT_BREAKER_THRESHOLD=5
export ELEVATEDIQ_CIRCUIT_BREAKER_TIMEOUT=60

# Geographic & Multi-Region
export ELEVATEDIQ_REGION="us-central1"
export ELEVATEDIQ_REGIONS="us-central1,us-east1,eu-west1"  # Multi-region for DR
export ELEVATEDIQ_GEO_REPLICATION_ENABLED="true"
export ELEVATEDIQ_GEO_FAILOVER_ENABLED="true"

# Compliance & Audit
export ELEVATEDIQ_PCI_DSS_COMPLIANCE="true"
export ELEVATEDIQ_GDPR_COMPLIANCE="true"
export ELEVATEDIQ_HIPAA_COMPLIANCE="false"  # Not applicable for this service
export ELEVATEDIQ_SOC2_COMPLIANCE="true"
export ELEVATEDIQ_AUDIT_ENABLED="true"
export ELEVATEDIQ_AUDIT_LOG_IMMUTABLE="true"

# Performance (production-tuned)
export ELEVATEDIQ_CONNECTION_POOL_SIZE=100
export ELEVATEDIQ_REQUEST_TIMEOUT=30
export ELEVATEDIQ_READ_TIMEOUT=30
export ELEVATEDIQ_WRITE_TIMEOUT=30
export ELEVATEDIQ_CACHE_TTL=3600  # 1 hour
export ELEVATEDIQ_QUERY_TIMEOUT=30000  # 30 seconds for database queries

# Alerts & On-Call
export ELEVATEDIQ_ALERT_EMAIL="alerts@${ELEVATEDIQ_DOMAIN}"
export ELEVATEDIQ_ALERT_PAGERDUTY_ENABLED="true"
export ELEVATEDIQ_ALERT_SLACK_ENABLED="true"
export ELEVATEDIQ_ON_CALL_TEAM="@elevatediq-platform"

echo "✓ ElevatedIQ production environment loaded"
echo "⚠️  PRODUCTION MODE: All secrets must be fetched from Secret Manager"
