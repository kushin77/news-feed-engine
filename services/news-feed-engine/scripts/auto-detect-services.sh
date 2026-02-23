#!/usr/bin/env bash
#
# ElevatedIQ News Feed Engine - Service Discovery Script
# Auto-detects running services and their health endpoints
#
# Usage: ./scripts/auto-detect-services.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "$1"; }

# Service discovery configuration
declare -A SERVICE_PORTS=(
    ["news-feed-engine"]=8084
    ["news-feed-processor"]=8085
    ["news-feed-admin"]=8086
    ["kafka"]=9092
    ["kafka-ui"]=8089
    ["postgres"]=5432
    ["redis"]=6379
    ["prometheus"]=9090
    ["grafana"]=3000
    ["jaeger"]=16686
    ["alertmanager"]=9093
    ["otel-collector"]=4317
)

declare -A SERVICE_HEALTHCHECKS=(
    ["news-feed-engine"]="/health"
    ["news-feed-processor"]="/health"
    ["news-feed-admin"]="/health"
    ["prometheus"]="/-/healthy"
    ["grafana"]="/api/health"
    ["jaeger"]="/"
    ["alertmanager"]="/-/healthy"
)

# Docker network to inspect
DOCKER_NETWORK="${DOCKER_NETWORK:-elevatediq-net}"

log "${CYAN}ElevatedIQ News Feed Engine - Service Discovery${NC}"
log "================================================="
log ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log "${RED}Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Function to check if a port is listening
check_port() {
    local host="$1"
    local port="$2"
    timeout 2 bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null && return 0 || return 1
}

# Function to discover Docker containers
discover_docker_containers() {
    log "${BLUE}Discovering Docker containers...${NC}"
    log ""

    if docker network inspect "$DOCKER_NETWORK" &>/dev/null; then
        log "Network: ${GREEN}$DOCKER_NETWORK${NC}"
        log ""

        # Get containers in the network
        containers=$(docker network inspect "$DOCKER_NETWORK" -f '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null || echo "")

        if [[ -n "$containers" ]]; then
            log "Containers in network:"
            for container in $containers; do
                status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
                ip=$(docker inspect --format="{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" "$container" 2>/dev/null || echo "N/A")

                if [[ "$status" == "running" ]]; then
                    log "  ${GREEN}●${NC} $container (IP: $ip)"
                else
                    log "  ${RED}○${NC} $container ($status)"
                fi
            done
        else
            log "${YELLOW}No containers found in $DOCKER_NETWORK${NC}"
        fi
    else
        log "${YELLOW}Network $DOCKER_NETWORK does not exist${NC}"
    fi
}

# Function to check service health
check_service_health() {
    local name="$1"
    local port="$2"
    local health_path="${SERVICE_HEALTHCHECKS[$name]:-}"

    if check_port "127.0.0.1" "$port"; then
        if [[ -n "$health_path" ]]; then
            http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$port$health_path" 2>/dev/null || echo "000")
            if [[ "$http_code" == "200" ]]; then
                log "  ${GREEN}●${NC} $name (port $port) - healthy"
            else
                log "  ${YELLOW}●${NC} $name (port $port) - port open, health: $http_code"
            fi
        else
            log "  ${GREEN}●${NC} $name (port $port) - listening"
        fi
        return 0
    else
        log "  ${RED}○${NC} $name (port $port) - not responding"
        return 1
    fi
}

# Function to scan known services
scan_services() {
    log ""
    log "${BLUE}Scanning service ports...${NC}"
    log ""

    local running=0
    local stopped=0

    for service in "${!SERVICE_PORTS[@]}"; do
        port="${SERVICE_PORTS[$service]}"
        if check_service_health "$service" "$port"; then
            ((running++))
        else
            ((stopped++))
        fi
    done

    log ""
    log "Summary: ${GREEN}$running running${NC}, ${RED}$stopped not responding${NC}"
}

# Function to check external access via Traefik
check_external_access() {
    log ""
    log "${BLUE}Checking external access via Traefik...${NC}"
    log ""

    local base_url="${NEWS_FEED_BASE_URL:-https://dev.elevatediq.ai}"

    endpoints=(
        "/news|News Feed Frontend"
        "/news-api/health|News Feed API"
        "/news-admin|News Admin Panel"
    )

    for endpoint in "${endpoints[@]}"; do
        path=$(echo "$endpoint" | cut -d'|' -f1)
        name=$(echo "$endpoint" | cut -d'|' -f2)

        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$base_url$path" 2>/dev/null || echo "000")

        if [[ "$http_code" == "200" ]] || [[ "$http_code" == "301" ]] || [[ "$http_code" == "302" ]]; then
            log "  ${GREEN}●${NC} $name ($path) - OK ($http_code)"
        elif [[ "$http_code" == "401" ]] || [[ "$http_code" == "403" ]]; then
            log "  ${YELLOW}●${NC} $name ($path) - Auth required ($http_code)"
        else
            log "  ${RED}○${NC} $name ($path) - $http_code"
        fi
    done
}

# Function to generate service report
generate_report() {
    local report_file="$PROJECT_ROOT/service-status.json"

    log ""
    log "${BLUE}Generating service report...${NC}"

    cat > "$report_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "project": "news-feed-engine",
  "network": "$DOCKER_NETWORK",
  "services": {
EOF

    local first=true
    for service in "${!SERVICE_PORTS[@]}"; do
        port="${SERVICE_PORTS[$service]}"
        if check_port "127.0.0.1" "$port" 2>/dev/null; then
            status="running"
        else
            status="stopped"
        fi

        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$report_file"
        fi

        echo -n "    \"$service\": { \"port\": $port, \"status\": \"$status\" }" >> "$report_file"
    done

    cat >> "$report_file" << EOF

  }
}
EOF

    log "Report saved to: $report_file"
}

# Main execution
discover_docker_containers
scan_services
check_external_access
generate_report

log ""
log "${CYAN}Service discovery complete!${NC}"
