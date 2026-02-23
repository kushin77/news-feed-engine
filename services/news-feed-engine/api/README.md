# ElevatedIQ News Feed Engine - API Documentation

This directory contains the OpenAPI 3.1.0 specification and interactive documentation for the News Feed Engine API.

## Quick Start

### View Documentation

```bash
# Start a local server
cd api
python3 -m http.server 8080

# Open in browser
# Swagger UI: http://dev.elevatediq.ai:8080/docs/swagger-ui.html
# ReDoc: http://dev.elevatediq.ai:8080/docs/redoc.html
# Combined: http://dev.elevatediq.ai:8080/docs/index.html
```bash

### Download OpenAPI Spec

```bash
curl -O http://dev.elevatediq.ai:8096/api/v1/openapi.yaml
```bash

## API Overview

### Endpoints Summary

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Health** | 2 | Health and readiness checks |
| **Content** | 6 | Content discovery and retrieval |
| **Creators** | 3 | Creator management |
| **Videos** | 3 | AI video summaries and transcripts |
| **AI** | 5 | Sentiment, entities, summarization |
| **Embeddings** | 3 | Vector search and similarity |
| **Analytics** | 4 | Content and engagement analytics |
| **Admin** | 5 | Configuration and ingestion |

### Total: 31 endpoints

## Authentication

Most endpoints are public. Admin endpoints require JWT Bearer authentication:

```bash
curl -H "Authorization: Bearer <token>" \
  https://dev.elevatediq.ai/api/gateway/news-feed/v1/admin/config
```bash

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `https://dev.elevatediq.ai/api/gateway/news-feed/v1` |
| Local | `http://dev.elevatediq.ai:8096/api/v1` |

Note: Production posture is frontend-only; APIs are not exposed on the production host at this time.

## Key Endpoints

### Content API

```bash
# List content
GET /content?page=1&limit=20&category=technology

# Search content (semantic)
GET /content/search?q=artificial+intelligence&limit=10

# Get trending
GET /content/trending?range=24h

# Get by category
GET /content/category/technology
```bash

### AI API

```bash
# Analyze content
POST /ai/analyze
{
  "content": "Your text here...",
  "analysis_types": ["sentiment", "entities", "topics"]
}

# Get recommendations
GET /ai/recommendations?user_id=abc&limit=10

# Generate summary
POST /ai/summarize
{
  "content": "Long text...",
  "max_length": 150,
  "style": "bullets"
}
```bash

### Embeddings API

```bash
# Generate embeddings
POST /embeddings/generate
{
  "texts": ["First text", "Second text"],
  "model": "text-embedding-ada-002"
}

# Semantic search
POST /embeddings/search
{
  "query": "machine learning applications",
  "limit": 10,
  "threshold": 0.7
}

# Find similar content
GET /embeddings/similar/{content_id}?limit=5
```bash

### Analytics API

```bash
# Content analytics
GET /analytics/content?range=7d&category=tech

# Trend analytics
GET /analytics/trends?range=24h

# Engagement analytics
GET /analytics/engagement?range=7d
```bash

## Response Formats

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 100,
    "total_pages": 5,
    "has_more": true
  }
}
```bash

### Error Response

```json
{
  "error": "not_found",
  "message": "Content with ID xyz not found",
  "code": "CONTENT_NOT_FOUND"
}
```bash

## Rate Limits

| Tier | Rate Limit | Burst |
|------|-----------|-------|
| Free | 100 req/min | 20 |
| Pro | 1000 req/min | 100 |
| Enterprise | Unlimited | Unlimited |

## SDKs

### Python

```python
from elevatediq import NewsFeedClient

client = NewsFeedClient(api_key="your-key")

# Search content
results = client.content.search("AI news", limit=10)

# Generate summary
summary = client.ai.summarize(content_id="abc123")
```bash

### TypeScript

```typescript
import { NewsFeedClient } from '@elevatediq/news-feed-sdk';

const client = new NewsFeedClient({ apiKey: 'your-key' });

// Get trending
const trending = await client.content.trending({ range: '24h' });

// Semantic search
const results = await client.embeddings.search({
  query: 'machine learning',
  limit: 10
});
```bash

## Webhooks

Register webhooks for real-time notifications:

```bash
POST /admin/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["content.created", "video.completed"],
  "secret": "your-secret"
}
```bash

### Event Types

- `content.created` - New content ingested
- `content.updated` - Content metadata updated
- `video.queued` - Video generation started
- `video.completed` - Video generation complete
- `video.failed` - Video generation failed

## Files

```

api/
├── openapi.yaml          # OpenAPI 3.1.0 specification
├── README.md             # This file
└── docs/
    ├── index.html        # Combined documentation portal
    ├── swagger-ui.html   # Swagger UI viewer
    └── redoc.html        # ReDoc viewer

```bash

## Validation

```bash
# Validate OpenAPI spec
npx @apidevtools/swagger-cli validate api/openapi.yaml

# Generate client SDKs
npx openapi-generator-cli generate \
  -i api/openapi.yaml \
  -g python \
  -o sdk/python
```bash

## Changelog

### v1.0.0 (2024-11-26)

- Initial API release
- 31 endpoints across 9 categories
- AI analysis, embeddings, and analytics APIs
- Multi-tenant white-label support
- Semantic search with vector embeddings
