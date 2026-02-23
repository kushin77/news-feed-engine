# 🚀 Elite AI Quick Start Guide

## Get the ElevatedIQ News Feed Engine running in 5 minutes

---

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Go 1.24+ (optional)
- API Keys (Claude, ElevenLabs, D-ID)

---

## 1. Clone & Navigate

```bash
cd services/news-feed-engine
```bash

## 2. Environment Setup

```bash
# Copy environment template
cp config/.env.example .env

# Edit with your API keys
nano .env  # or vim .env
```bash

### Required API Keys

| Service | Required | Get Key |
|---------|----------|---------|
| Claude (Anthropic) | ✅ | <https://console.anthropic.com> |
| ElevenLabs | ✅ | <https://elevenlabs.io> |
| D-ID | ✅ | <https://d-id.com> |
| OpenAI | Optional | <https://platform.openai.com> |

## 3. Start Infrastructure

```bash
# Start all services
docker-compose -f docker-compose.news-feed.yml up -d

# Verify services are running
docker-compose -f docker-compose.news-feed.yml ps
```bash

## 4. Run Migrations

```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d news_feed \
  -f migrations/001_initial_schema.sql
```bash

## 5. Start the Service

### Option A: Docker (Recommended)

```bash
docker-compose -f docker-compose.news-feed.yml up -d \
  elevatediq-news-feed-engine elevatediq-news-feed-processor
```bash

### Option B: Local Development

```bash
# Terminal 1: Go service
go run ./cmd/news-feed

# Terminal 2: Python processor
cd processor
source venv/bin/activate
python -m processor.main
```bash

---

## 6. Verify Installation

```bash
# Check health
curl https://dev.elevatediq.ai/news-feed/health

# Expected response:
# {"status": "healthy", "version": "2.0.0"}
```bash

---

## 7. Access Dashboards

| Service | URL |
|---------|-----|
| News Feed API | <https://dev.elevatediq.ai/news-feed> |
| Prometheus | <https://dev.elevatediq.ai/prometheus> |
| Grafana | <https://dev.elevatediq.ai/grafana> |

---

## 8. First Content Pipeline

```python
from processor import AgentOrchestrator, TrendAggregator

# Initialize
orchestrator = AgentOrchestrator()
aggregator = TrendAggregator()

# Get trends
trends = await aggregator.aggregate_all(categories=['technology'])

# Start autonomous pipeline
await orchestrator.start_pipeline()
```bash

---

## Troubleshooting

### Kafka Connection Issues

```bash
# Check Kafka is running
docker logs elevatediq-kafka

# Restart if needed
docker-compose -f docker-compose.news-feed.yml restart elevatediq-kafka
```bash

### Missing Python Dependencies

```bash
cd processor
pip install -r requirements.txt
```bash

### Database Connection Issues

```bash
# Check PostgreSQL is ready
docker exec elevatediq-postgres pg_isready
```bash

---

## Next Steps

1. 📊 Configure Grafana dashboards
2. 🔐 Set up OAuth for publishing platforms
3. 🎬 Test video generation pipeline
4. 📈 Monitor metrics in Prometheus

---

**Full documentation**: [IMPLEMENTATION_COMPLETE.md](./docs/IMPLEMENTATION_COMPLETE.md)
