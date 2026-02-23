# 📰 News Feed Engine - Your Content Growth Machine

## Stop manually curating content. AI finds trending topics, creates videos, and publishes to 12 platforms—while you sleep

News Feed Engine is your autonomous content factory: it discovers viral-worthy content, predicts performance, generates professional videos, and distributes everywhere your audience lives.

**Status**: ✅ Elite AI Enhancements Complete  
**Port**: 8082  

---

## What It Does For You

News Feed Engine eliminates content creation bottlenecks. From discovery to distribution, every step is automated with AI—so you can focus on strategy instead of manual publishing.

**Real-World Impact**:

- **10x Content Output**: Publish 50+ pieces/day (vs 5 manually)
- **Trend Surfing**: Catch viral topics 24 hours before competitors
- **Video Automation**: Professional videos created in 5 minutes (not 5 hours)
- **Multi-Platform Reach**: Publish to YouTube, Twitter, LinkedIn, TikTok in one click
- **Predictive Intelligence**: AI scores content before publishing (no more flops)
- **White-Label Ready**: Deploy for clients with custom branding

---

## Capabilities

- **Multi-Platform Ingestion**: YouTube, Twitter/X, Reddit, RSS feeds, TikTok, LinkedIn
- **AI-Powered Analysis**: Content categorization, sentiment analysis, quality scoring using Claude AI
- **Semantic Search**: Vector embeddings with pgvector for intelligent content discovery
- **Predictive Content Engine**: AI-powered performance prediction and trend surfing
- **Autonomous Video Production**: End-to-end video generation with ElevenLabs + D-ID
- **Media Manager Integration**: Unified asset library with intelligent recommendations
- **Cross-Platform Publishing**: Automated distribution to 12+ platforms
- **🆕 Autonomous AI Agents**: 5 specialized agents for full pipeline automation
- **🆕 Real-Time Trend Sources**: 6 trend data sources with aggregation
- **🆕 Analytics Pipeline**: Kafka streaming + Prometheus metrics + Grafana
- **🆕 OAuth Manager**: 8 platform OAuth providers with encrypted token storage
- **White-Label Support**: Multi-tenant configuration for branded deployments

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ElevatedIQ Platform                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │
│  │   YouTube   │    │  Twitter/X  │    │        RSS Feeds        │  │
│  │     API     │    │     API     │    │    (Tech, News, etc.)   │  │
│  └──────┬──────┘    └──────┬──────┘    └───────────┬─────────────┘  │
│         │                  │                        │                 │
│         └──────────────────┼────────────────────────┘                 │
│                            ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    News Feed Engine (Go)                         │ │
│  │  • Content Ingestion    • API Endpoints    • Webhook Handlers   │ │
│  └───────────────────────────────┬─────────────────────────────────┘ │
│                                  │                                    │
│                    ┌─────────────┼─────────────┐                     │
│                    ▼             ▼             ▼                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐   │
│  │  Kafka    │ │ PostgreSQL│ │   Redis   │ │     MongoDB       │   │
│  │  Topics   │ │ + pgvector│ │   Cache   │ │  (Raw Content)    │   │
│  └─────┬─────┘ └───────────┘ └───────────┘ └───────────────────┘   │
│        │                                                             │
│        ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                  ML Processor (Python)                           │ │
│  │  • Claude Analysis   • Embeddings   • Categorization            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                Video Generator (Background)                      │ │
│  │  • ElevenLabs TTS   • D-ID Avatar   • Video Assembly            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```bash

## Quick Start

### Prerequisites

- Go 1.24+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15 with pgvector extension
- Apache Kafka (or use Strimzi on Kubernetes)
- GCP account for Secret Manager (production)

### Local Development

1. **Clone and navigate to the service:**

   ```bash
   cd services/news-feed-engine
```bash

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
```bash

3. **Start dependencies:**

   ```bash
   docker-compose -f docker-compose.news-feed.yml up -d \
     elevatediq-postgres elevatediq-redis elevatediq-mongodb
```bash

4. **Run database migrations:**

   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d news_feed \
     -f migrations/001_initial_schema.sql \
     -f migrations/002_semantic_search_functions.sql
```bash

5. **Start the Go service:**

   ```bash
   go run ./cmd/news-feed
```bash

6. **Start the Python processor (in another terminal):**

   ```bash
   cd processor
   pip install -r requirements.txt
   python -m processor.main
```bash

### Docker Compose

```bash
# Start all services
docker-compose -f ../../docker-compose.yml \
  -f docker-compose.news-feed.yml up -d

# View logs
docker-compose logs -f elevatediq-news-feed-engine
```bash

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/api/v1/content` | List content (paginated) |
| GET | `/api/v1/content/{id}` | Get content by ID |
| GET | `/api/v1/content/category/{category}` | Filter by category |
| GET | `/api/v1/content/geo/{classification}` | Filter by geography |
| GET | `/api/v1/content/trending` | Trending content |
| GET | `/api/v1/content/search?q=query` | Semantic search |
| GET | `/api/v1/creators` | List creators |
| GET | `/api/v1/creators/{id}` | Get creator details |
| GET | `/api/v1/videos` | List video summaries |
| GET | `/api/v1/videos/{id}` | Get video details |

### Admin Endpoints (requires JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/admin/content/ingest` | Trigger ingestion |
| POST | `/api/v1/admin/videos/generate` | Generate video |
| GET/PUT | `/api/v1/admin/config` | Service configuration |
| GET/PUT | `/api/v1/admin/config/sources` | Content sources |
| GET/PUT | `/api/v1/admin/config/templates` | Video templates |
| GET | `/api/v1/admin/analytics/overview` | Analytics dashboard |
| GET/PUT | `/api/v1/admin/whitelabel` | White-label config |

## Configuration

### Environment Variables

```bash
# Server
PORT=8080
ELEVATEDIQ_ENVIRONMENT=development

# Database
POSTGRES_DSN=postgres://postgres:postgres@dev.elevatediq.ai:5432/news_feed
MONGO_URI=mongodb://dev.elevatediq.ai:27017/news_feed
REDIS_URL=redis://dev.elevatediq.ai:6379/0

# Kafka
KAFKA_BROKERS=dev.elevatediq.ai:9092
KAFKA_CONSUMER_GROUP=news-feed-engine

# API Keys (use GCP Secret Manager in production)
YOUTUBE_API_KEY=your-key
TWITTER_API_KEY=your-key
CLAUDE_API_KEY=your-key
ELEVENLABS_API_KEY=your-key

# White-label
ENABLE_WHITE_LABEL=true
DEFAULT_TENANT_ID=elevatediq
```bash

### GCP Secret Manager (Production)

All sensitive API keys should be stored in GCP Secret Manager with the `news-feed-*` prefix:

- `news-feed-youtube-api-key`
- `news-feed-twitter-api-key`
- `news-feed-claude-api-key`
- `news-feed-elevenlabs-api-key`
- `news-feed-jwt-secret`

See `config/gcp-secrets.yaml` for the complete list.

## Multi-Tenant White-Label

The system supports multiple tenants with customizable:

- **Branding**: Logo, colors, fonts, custom CSS
- **Content Sources**: Per-tenant source configuration
- **Video Templates**: Custom voice/avatar settings
- **Enabled Features**: Platforms, categories, video generation

Access tenant-specific content using the `X-Tenant-ID` header or subdomain routing.

## Kafka Topics

| Topic | Purpose | Retention |
|-------|---------|-----------|
| `news-feed-raw-content` | Ingested raw content | 7 days |
| `news-feed-processed-content` | AI-analyzed content | 30 days |
| `news-feed-video-jobs` | Video generation queue | 1 day |
| `news-feed-analytics-events` | User interaction events | 30 days |
| `news-feed-dlq` | Failed messages | 7 days |

## Database Schema

### Core Tables

- `tenant_configs` - White-label tenant configuration
- `creators` - Content creator profiles
- `content` - Aggregated content with embeddings
- `video_summaries` - Generated video metadata
- `content_sources` - Configurable ingestion sources
- `video_templates` - Video generation templates
- `content_analytics` - Daily engagement metrics

See `migrations/001_initial_schema.sql` for complete schema.

## AI Analysis Pipeline

1. **Content Ingestion**: Raw content from platforms
2. **Claude Analysis**: Summarization, categorization, sentiment
3. **Embedding Generation**: OpenAI text-embedding-ada-002
4. **Quality Scoring**: Automated quality and credibility assessment
5. **Geo Classification**: Local/regional/national/global tagging

## Video Generation Pipeline

1. **Script Generation**: Claude creates narration script
2. **Voice Synthesis**: ElevenLabs TTS with configurable voices
3. **Avatar Generation**: D-ID talking head (optional)
4. **Video Assembly**: FFmpeg composite with graphics
5. **Storage**: GCS/S3 with CDN distribution

## Monitoring

### Prometheus Metrics

- `news_feed_messages_processed_total` - Processed message count
- `news_feed_processing_seconds` - Processing latency
- `news_feed_ai_analysis_seconds` - AI analysis latency
- `news_feed_embedding_seconds` - Embedding generation latency

### Health Endpoints

- `/health` - Basic liveness check
- `/ready` - Full readiness with dependency checks
- `/metrics` - Prometheus metrics

## Development

### Running Tests

```bash
# Go tests
go test -v ./...

# Python tests
cd processor && pytest tests/ -v
```bash

### Linting

```bash
# Go
golangci-lint run

# Python
ruff check processor/
mypy processor/
```bash

### Building

```bash
# Go binary
CGO_ENABLED=0 go build -o news-feed-engine ./cmd/news-feed

# Docker images
docker build -t elevatediq/news-feed-engine .
docker build -t elevatediq/news-feed-processor ./processor
```bash

## Deployment

### Kubernetes

```bash
# Apply Kafka topics
kubectl apply -f config/kafka-topics.yaml

# Deploy services
kubectl apply -f k8s/
```bash

### CI/CD

GitHub Actions workflow at `.github/workflows/news-feed-engine.yml`:

1. Build and test Go service
2. Build and test Python processor
3. Validate database migrations
4. Build and push Docker images
5. Deploy to staging/production

---

## 🤖 Elite AI Components

### AI Agents System

Five autonomous agents working in concert:

```python
from processor import AgentOrchestrator

# Start full autonomous pipeline
orchestrator = AgentOrchestrator()
await orchestrator.start_pipeline()
```bash

| Agent | Role |
|-------|------|
| `ContentCuratorAgent` | Discovers and curates trending content |
| `VideoProducerAgent` | Automates video production pipeline |
| `DistributorAgent` | Optimizes multi-platform distribution |
| `AnalystAgent` | Analyzes performance and provides insights |
| `EngagementAgent` | Manages audience engagement |

### Trend Sources

Real-time trend detection from 6 sources:

```python
from processor import TrendAggregator

aggregator = TrendAggregator()
trends = await aggregator.aggregate_all(categories=['technology', 'ai'])
```bash

Sources: Google Trends, Twitter/X, Reddit, YouTube, NewsAPI, TikTok

### Analytics Pipeline

Kafka-based event streaming with Prometheus metrics:

```python
from processor import AnalyticsPipeline, generate_grafana_dashboard

pipeline = AnalyticsPipeline()
await pipeline.start()

# Generate Grafana dashboard config
dashboard = generate_grafana_dashboard()
```bash

### OAuth Manager

Secure OAuth 2.0 for all platforms:

```python
from processor import OAuthManager

oauth = OAuthManager()
auth_url = await oauth.start_oauth_flow('youtube')
# After callback...
tokens = await oauth.handle_callback('youtube', code, state)
```bash

Platforms: YouTube, TikTok, LinkedIn, Instagram, Twitter, Facebook, Pinterest, Snapchat

---

## 📚 Documentation

- [Elite AI Enhancements](./docs/ELITE_AI_ENHANCEMENTS.md) - Strategic roadmap
- [Implementation Complete](./docs/IMPLEMENTATION_COMPLETE.md) - Component details
- [API Reference](./api/openapi.yaml) - REST API docs

## License

Proprietary - ElevatedIQ Platform Team

## Support

- **Documentation**: `/docs/news-feed/`
- **API Reference**: `/api/openapi.yaml`
- **Issues**: GitHub Issues with `news-feed` label
