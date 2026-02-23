#!/usr/bin/env bash
#
# ElevatedIQ News Feed Engine - Health Check Script
# Validates all news-feed-engine services are running and healthy
#
# Usage: ./scripts/check-services.sh [--verbose]
#
set -euo pipefail

VERBOSE=${1:-}
BASE_URL="${NEWS_FEED_BASE_URL:-https://dev.elevatediq.ai}"
TIMEOUT=10

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "$1"; }
log_ok() { log "${GREEN}✓${NC} $1"; }
log_warn() { log "${YELLOW}⚠${NC} $1"; }
log_fail() { log "${RED}✗${NC} $1"; }

check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    if [[ "$VERBOSE" == "--verbose" ]]; then
        log "Checking $name at $url..."
    fi

    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$TIMEOUT" "$url" 2>/dev/null || echo "000")

    if [[ "$response" == "$expected_code" ]]; then
        log_ok "$name ($url) - HTTP $response"
        return 0
    else
        log_fail "$name ($url) - HTTP $response (expected $expected_code)"
        return 1
    fi
}

log "ElevatedIQ News Feed Engine - Health Check"
log "============================================"
log "Base URL: $BASE_URL"
log ""

FAILED=0

# Core API endpoints
log "Core API Endpoints:"
check_endpoint "Health" "$BASE_URL/news/api/health" || ((FAILED++))
check_endpoint "Ready" "$BASE_URL/news/api/ready" || ((FAILED++))
check_endpoint "Content List" "$BASE_URL/news/api/v1/content" || ((FAILED++))
check_endpoint "Trending" "$BASE_URL/news/api/v1/content/trending" || ((FAILED++))
check_endpoint "Creators" "$BASE_URL/news/api/v1/creators" || ((FAILED++))
check_endpoint "Videos" "$BASE_URL/news/api/v1/videos" || ((FAILED++))
log ""

# Monitoring endpoints
log "Monitoring Endpoints:"
check_endpoint "Prometheus" "$BASE_URL/news/prometheus/-/healthy" || ((FAILED++))
check_endpoint "Grafana" "$BASE_URL/news/grafana/api/health" || ((FAILED++))
check_endpoint "Metrics" "$BASE_URL/news/api/metrics" || ((FAILED++))
log ""

# Docker container checks (if running locally)
if command -v docker &> /dev/null; then
    log "Container Status:"
    for container in elevatediq-news-feed-engine elevatediq-news-feed-processor elevatediq-kafka elevatediq-prometheus elevatediq-grafana; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
            if [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]; then
                log_ok "$container (running, $health)"
            else
                log_warn "$container (running, $health)"
            fi
        else
            log_fail "$container (not running)"
            ((FAILED++))
        fi
    done
fi

log ""
if [[ $FAILED -eq 0 ]]; then
    log_ok "All checks passed!"
    exit 0
else
    log_fail "$FAILED check(s) failed"
    exit 1
fi
