# 🚀 Deployment & Operations Guide

**Version**: 1.0  
**Last Updated**: February 23, 2026  
**Maintained By**: ElevatedIQ DevOps Team

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Troubleshooting](#troubleshooting)
8. [Disaster Recovery](#disaster-recovery)

---

## 🎯 Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone repository
git clone https://github.com/kushin77/news-feed-engine.git
cd news-feed-engine

# 2. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 3. Run with Docker Compose
docker-compose -f docker-compose.local.yml up -d

# 4. Verify services
curl http://localhost:8080/health
curl http://localhost:8081/health  # Processor
curl http://localhost:3000/health  # Frontend

# 5. View logs
docker-compose -f docker-compose.local.yml logs -f news-feed-engine
```

Done! ✅

---

## 💻 Local Development

### Prerequisites
- Go 1.21+
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Setup

```bash
# 1. Install dependencies
cd services/news-feed-engine
go mod download
cd ../processor
pip install -r requirements.txt
cd ../frontend
npm install

# 2. Set up database
createdb news_feed_dev
psql news_feed_dev < services/news-feed-engine/migrations/001_init.sql

# 3. Set up Redis
redis-server

# 4. Configure environment
export DATABASE_URL="postgresql://user:password@localhost:5432/news_feed_dev"
export REDIS_URL="redis://localhost:6379/0"
export CLAUDE_API_KEY="sk-ant-..."
export PORT=8080

# 5. Run services
# Terminal 1: News Feed Engine
cd services/news-feed-engine
go run ./cmd/news-feed/main.go

# Terminal 2: Python Processor
cd services/processor
python processor/processor.py

# Terminal 3: Frontend
cd services/frontend
npm start
```

### Testing

```bash
# Run unit tests
cd services/news-feed-engine
go test -v -race ./...

# Run with coverage
go test -cover ./...

# Python tests
cd ../processor
pytest tests/ -v --cov=processor

# Integration tests
pytest tests/integration/ -v

# JavaScript tests
cd ../frontend
npm test
```

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Development stack
docker-compose -f docker-compose.local.yml up -d

# Testing stack
docker-compose -f docker-compose.test.yml up -d

# Load testing stack
docker-compose -f docker-compose.load-test.yml up -d

# Production-like stack
docker-compose -f docker-compose.prod.yml up -d
```

### Building Custom Images

```bash
# Build news-feed-engine
docker build -t news-feed-engine:custom \
  -f services/news-feed-engine/Dockerfile \
  services/news-feed-engine

# Build processor
docker build -t processor:custom \
  -f services/processor/Dockerfile \
  services/processor

# Build frontend
docker build -t frontend:custom \
  -f services/frontend/Dockerfile \
  services/frontend

# Push to registry
docker tag news-feed-engine:custom gcr.io/elevatediq/news-feed-engine:latest
docker push gcr.io/elevatediq/news-feed-engine:latest
```

### Healthchecks

```bash
# Check service health
curl http://localhost:8080/health
curl http://localhost:8081/health

# Check metrics
curl http://localhost:8080/metrics

# Check logs
docker-compose logs -f news-feed-engine
docker-compose logs news-feed-engine --tail 100
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Install Helm (optional but recommended)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Connect to cluster
kubectl config use-context dev-elevatediq-ai

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Deploying

```bash
# 1. Create namespace
kubectl create namespace news-feed

# 2. Create secrets
kubectl create secret generic news-feed-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=redis-url="redis://..." \
  --from-literal=claude-api-key="sk-ant-..." \
  --from-literal=elevenlabs-api-key="..." \
  -n news-feed

# 3. Apply ConfigMaps
kubectl apply -f k8s/configmap.yaml -n news-feed

# 4. Deploy services
kubectl apply -f k8s/postgres-statefulset.yaml -n news-feed
kubectl apply -f k8s/redis-deployment.yaml -n news-feed
kubectl apply -f k8s/news-feed-engine-deployment.yaml -n news-feed
kubectl apply -f k8s/processor-deployment.yaml -n news-feed
kubectl apply -f k8s/frontend-deployment.yaml -n news-feed

# 5. Verify deployment
kubectl rollout status deployment/news-feed-engine -n news-feed
kubectl get pods -n news-feed
kubectl get svc -n news-feed
```

### Scaling

```bash
# Scale deployments
kubectl scale deployment news-feed-engine --replicas=5 -n news-feed
kubectl scale deployment processor --replicas=3 -n news-feed

# View Horizontal Pod Autoscaler
kubectl get hpa -n news-feed

# Manual scaling via HPA
kubectl autoscale deployment news-feed-engine \
  --min=2 --max=10 \
  --cpu-percent=80 \
  -n news-feed
```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/news-feed-engine \
  news-feed-engine=gcr.io/elevatediq/news-feed-engine:v1.1.0 \
  -n news-feed

# Check rollout progress
kubectl rollout status deployment/news-feed-engine -n news-feed

# Rollback if needed
kubectl rollout undo deployment/news-feed-engine -n news-feed
```

---

## 🏢 Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing (>85% coverage)
- [ ] Security scan complete (Snyk, Trivy)
- [ ] Load testing passed
- [ ] Database migration tested
- [ ] API documentation updated
- [ ] Monitoring dashboards created
- [ ] Alerts configured
- [ ] Runbooks documented
- [ ] Team trained on procedures

### Deployment Steps

```bash
# 1. Tag release
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# 2. Create GitHub release with notes
gh release create v1.0.0 --notes "Release notes here"

# 3. CI/CD automatically builds and pushes images
# (GitHub Actions workflow: build-push.yml)

# 4. Verify image in registry
docker pull gcr.io/elevatediq/news-feed-engine:v1.0.0
docker inspect gcr.io/elevatediq/news-feed-engine:v1.0.0

# 5. Deploy to staging first
kubectl apply -f k8s/ --namespace=staging

# 6. Run smoke tests
./tests/smoke-tests.sh staging

# 7. Deploy to production
kubectl apply -f k8s/ --namespace=production

# 8. Verify production
./tests/smoke-tests.sh production

# 9. Monitor metrics
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Visit http://localhost:9090
```

### Canary Deployment (Optional)

```bash
# Deploy 10% of traffic to new version
kubectl patch service news-feed-engine -n production \
  -p '{"spec":{"selector":{"version":"v1.0.0"}}}'

# Monitor metrics for 1 hour
# If good, gradually increase to 50%, then 100%
```

---

## 📊 Monitoring & Alerts

### Prometheus

```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Query metrics
# http://localhost:9090/
# Search: up{job="news-feed-engine"}

# Common queries:
# - Rate of errors: rate(http_requests_total{status=~"5.."}[5m])
# - P95 latency: histogram_quantile(0.95, http_request_duration_seconds_bucket)
# - Memory usage: process_resident_memory_bytes
```

### Grafana

```bash
# Port forward Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# Access: http://localhost:3000
# Login: admin / admin (change password!)

# Import dashboards:
# - k8s/grafana/news-feed-engine.json
# - k8s/grafana/system-metrics.json
```

### Alerts

Key alerts to monitor:

1. **Service Availability**
   - ServiceDown - Service not responding
   - HighErrorRate - Error rate >1%

2. **Performance**
   - HighLatency - P95 latency >1s
   - HighCPUUsage - CPU >85%
   - HighMemoryUsage - Memory >90%

3. **External APIs**
   - ClaudeAPIFailure - Claude API down
   - ElevenLabsAPIFailure - TTS API down
   - SocialMediaAPIFailure - Cannot publish articles

4. **Database**
   - DatabaseConnectionFailure
   - SlowQueryAlert - Query time >5s
   - HighConnectionCount - >90% of pool

### Alert Notifications

```yaml
# Configure notification channels in Grafana:
# - Slack: #alerts channel
# - Email: ops@elevatediq.ai
# - PagerDuty: On-call rotation

# Slack webhook setup
https://api.slack.com/apps/YOUR_APP_ID/incoming-webhooks

# Test alert
kubectl port-forward alertmanager 9093:9093 -n monitoring
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
kubectl logs deployment/news-feed-engine -n production

# Check events
kubectl describe deployment news-feed-engine -n production

# Common causes:
# - Image not found: Verify image registry and tag
# - Secrets missing: Check secrets created properly
# - Port in use: Check port availability
# - Memory limit: Increase resource limits
```

### High Latency

```bash
# Check slow queries
kubectl exec -it postgres-0 -n production -- psql news_feed -c \
  "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check Redis performance
kubectl exec -it redis-0 -n production -- redis-cli INFO stats

# Optimize database indexes
kubectl apply -f k8s/postgres-indexes.yaml -n production
```

### Disk Space Issues

```bash
# Check disk usage
kubectl exec pod/postgres-0 -n production -- df -h

# Expand PersistentVolume
kubectl patch pvc postgres-data -n production \
  -p '{"spec":{"resources":{"requests":{"storage":"500Gi"}}}}'

# Verify expansion
kubectl get pvc -n production
```

### Memory Leaks

```bash
# Monitor memory over time
kubectl top pod -n production --containers

# Check for goroutine leaks (Go)
curl http://pod-ip:8080/debug/pprof/goroutine | head -20

# Profile CPU usage
go tool pprof http://pod-ip:8080/debug/pprof/profile?seconds=30
```

---

## 🆘 Disaster Recovery

### Database Backup & Restore

```bash
# Daily backup (automatic via CronJob)
kubectl apply -f k8s/backup-cronjob.yaml -n production

# Manual backup
kubectl exec postgres-0 -n production -- \
  pg_dump news_feed > backup-$(date +%Y%m%d).sql

# Restore from backup
kubectl cp backup-20260223.sql postgres-0:/tmp/
kubectl exec postgres-0 -n production -- \
  psql news_feed < /tmp/backup-20260223.sql
```

### Service Recovery

```bash
# If service crashes, Kubernetes auto-restarts
kubectl get events -n production --sort-by='.lastTimestamp'

# Manual recovery
kubectl rollout restart deployment/news-feed-engine -n production

# Check recovery progress
kubectl rollout status deployment/news-feed-engine -n production
```

### Data Recovery

```bash
# Restore with point-in-time recovery (PITR)
# PostgreSQL WAL archiving must be enabled

# Restore to specific time
RESTORE_TIME="2026-02-23 15:00:00"
pg_restore --time-target="$RESTORE_TIME" backup.sql
```

---

## 📞 Support & Escalation

### On-Call Rotation

- **Primary**: DevOps engineer
- **Secondary**: Senior backend engineer
- **Escalation**: Engineering manager

### Incident Contact

- **Slack**: #incidents channel
- **Email**: incidents@elevatediq.ai
- **Phone**: +1-555-NEWS-ENG (for critical issues)

### RTO/RPO Targets

- **RTO** (Recovery Time Objective): 15 minutes
- **RPO** (Recovery Point Objective): 5 minutes
- **Max downtime per month**: 99.95% availability

---

## 📚 Related Documentation

- [API Reference](./API_REFERENCE.md)
- [Configuration Guide](./CONFIGURATION.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Security Guide](./SECURITY.md)

---

**Questions?** Email: ops@elevatediq.ai
