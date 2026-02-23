# News Feed Engine - Complete API Reference

**API Version**: 1.0  
**Base URL**: `https://api.dev.elevatediq.ai/v1`  
**Documentation**: https://github.com/kushin77/news-feed-engine/docs  
**GitHub**: https://github.com/kushin77/news-feed-engine

---

## 📚 API Overview

The News Feed Engine provides a comprehensive REST API for:
- Content aggregation from 50+ news sources
- AI-powered article analysis using Claude
- Multi-platform social media publishing
- Video generation with voice-over and avatars
- Real-time metrics and monitoring

---

## 🔐 Authentication

All API requests require authentication via Bearer token or API key.

### Bearer Token (OAuth 2.0)
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key
```bash
Authorization: Bearer sk-news-feed-engine-...
# Or via header
X-API-Key: sk-news-feed-engine-...
```

### Getting Credentials
1. Generate token: `POST /auth/tokens`
2. Scope: `read:feed`, `write:feed`, `read:articles`, `write:articles`
3. Expires: 24 hours
4. Rotate: Automatically after 24 hours

---

## 📋 Endpoints

### News Feeds

#### List All Feeds
```http
GET /feeds
```

Query Parameters:
- `limit` (int, default: 10) - Results per page
- `offset` (int, default: 0) - Pagination offset
- `category` (string) - Filter by category (tech, business, sports, etc.)
- `language` (string) - Language code (en, es, fr, etc.)
- `sort` (string) - Sort order: recent, popular, trending

Response (200 OK):
```json
{
  "feeds": [
    {
      "id": "feed-123",
      "name": "TechCrunch",
      "url": "https://techcrunch.com/feed/",
      "category": "technology",
      "language": "en",
      "articles_count": 1234,
      "last_updated": "2026-02-23T18:30:00Z",
      "status": "active",
      "error_rate": 0.01
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 10,
    "offset": 0,
    "pages": 15
  }
}
```

Error Responses:
- `401 Unauthorized` - Invalid or missing authentication
- `403 Forbidden` - Insufficient permissions
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

#### Get Feed Details
```http
GET /feeds/{feed_id}
```

Path Parameters:
- `feed_id` (string, required) - Feed identifier

Response (200 OK):
```json
{
  "id": "feed-123",
  "name": "TechCrunch",
  "description": "Technology news and insights",
  "url": "https://techcrunch.com/feed/",
  "category": "technology",
  "language": "en",
  "articles_count": 1234,
  "last_article": "2026-02-23T18:29:00Z",
  "last_updated": "2026-02-23T18:30:00Z",
  "status": "active",
  "metadata": {
    "source_type": "rss",
    "update_frequency": "hourly",
    "error_rate": 0.01,
    "avg_articles_per_day": 15
  }
}
```

---

### Articles

#### List Articles
```http
GET /articles
```

Query Parameters:
- `limit` (int, default: 20, max: 100)
- `offset` (int, default: 0)
- `search` (string) - Full-text search query
- `feed_id` (string) - Filter by feed
- `category` (string) - Filter by category
- `from_date` (datetime) - ISO 8601 format: `2026-02-01T00:00:00Z`
- `to_date` (datetime) - ISO 8601 format
- `sort` (string) - recent, popular, trending, relevance
- `status` (string) - published, draft, scheduled, archived
- `has_video` (boolean) - Only articles with video

Example Request:
```bash
curl -X GET 'https://api.dev.elevatediq.ai/v1/articles?limit=20&search=AI&sort=trending' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

Response (200 OK):
```json
{
  "articles": [
    {
      "id": "article-456",
      "title": "AI Breakthrough in Content Analysis",
      "description": "New advances in machine learning for content understanding",
      "url": "https://techcrunch.com/article-456",
      "content": "Full article text...",
      "author": "John Doe",
      "published_at": "2026-02-23T15:30:00Z",
      "feed_id": "feed-123",
      "feed_name": "TechCrunch",
      "category": "technology",
      "image_url": "https://example.com/image.jpg",
      "image_alt": "AI visualization",
      "language": "en",
      "word_count": 1500,
      "reading_time_minutes": 7,
      "status": "published",
      "analysis": {
        "sentiment": "positive",
        "sentiment_score": 0.82,
        "topics": ["artificial-intelligence", "machine-learning", "nlp"],
        "entities": ["Google", "OpenAI", "DeepMind"],
        "quality_score": 0.91,
        "is_trending": true,
        "trend_rank": 3
      },
      "social_metrics": {
        "shares": 1234,
        "engagement": 5678,
        "reach": 45000
      },
      "video": {
        "url": "https://video.dev.elevatediq.ai/v123",
        "duration_seconds": 120,
        "thumbnail": "https://video.dev.elevatediq.ai/v123/thumb.jpg",
        "status": "published"
      }
    }
  ],
  "pagination": {
    "total": 5000,
    "limit": 20,
    "offset": 0,
    "pages": 250
  }
}
```

---

#### Get Article Details
```http
GET /articles/{article_id}
```

Response (200 OK):
```json
{
  "id": "article-456",
  "title": "AI Breakthrough in Content Analysis",
  "description": "Short summary...",
  "url": "https://source.com/article",
  "content": "Full article HTML content...",
  "metadata": {
    "author": "John Doe",
    "published_at": "2026-02-23T15:30:00Z",
    "updated_at": "2026-02-23T18:00:00Z",
    "word_count": 1500,
    "reading_time": 7
  },
  "analysis": {
    "sentiment": "positive",
    "topics": ["ai", "ml"],
    "quality_score": 0.91
  },
  "videos": [
    {
      "id": "video-789",
      "title": "AI Breakthrough Explained",
      "url": "https://video.dev.elevatediq.ai/v789",
      "thumbnail": "https://video.dev.elevatediq.ai/v789/thumb.jpg",
      "duration": 120,
      "generated_at": "2026-02-23T16:45:00Z",
      "status": "published",
      "social_posts": {
        "twitter": { "url": "https://twitter.com/...", "posted_at": "2026-02-23T17:00:00Z" },
        "linkedin": { "url": "https://linkedin.com/...", "posted_at": "2026-02-23T17:05:00Z" },
        "facebook": { "status": "published" }
      }
    }
  ]
}
```

---

#### Analyze Article
```http
POST /articles/{article_id}/analyze
```

Request Body:
```json
{
  "analyze_sentiment": true,
  "generate_summary": true,
  "extract_entities": true,
  "detect_topics": true,
  "generate_tags": true,
  "assess_quality": true
}
```

Response (200 OK):
```json
{
  "id": "article-456",
  "analysis": {
    "sentiment": {
      "overall": "positive",
      "score": 0.82,
      "confidence": 0.95,
      "breakdown": {
        "positive": 0.82,
        "neutral": 0.12,
        "negative": 0.06
      }
    },
    "summary": "AI and machine learning technologies have reached a new milestone...",
    "entities": [
      {
        "text": "Google",
        "type": "organization",
        "relevance": 0.95
      }
    ],
    "topics": [
      {
        "name": "artificial-intelligence",
        "confidence": 0.98,
        "relevance": 0.95
      }
    ],
    "tags": ["AI", "ML", "Technology", "Breakthrough"],
    "quality_score": 0.91,
    "quality_details": {
      "structure": 0.9,
      "grammar": 0.92,
      "factuality": 0.88,
      "originality": 0.92,
      "engagement": 0.90
    }
  }
}
```

---

### Publishing

#### Publish to Social Media
```http
POST /articles/{article_id}/publish
```

Request Body:
```json
{
  "platforms": ["twitter", "linkedin", "facebook"],
  "with_video": true,
  "custom_message": "Optional custom message for posts",
  "scheduling": {
    "type": "immediate",
    "datetime": "2026-02-24T09:00:00Z"
  },
  "hashtags": ["#AI", "#TechNews"],
  "mention_accounts": {
    "twitter": ["@TechCrunch"],
    "linkedin": ["company-id-123"]
  }
}
```

Response (202 Accepted):
```json
{
  "id": "publish-job-123",
  "article_id": "article-456",
  "status": "processing",
  "platforms": [
    {
      "platform": "twitter",
      "status": "queued",
      "post_url": null,
      "scheduled_for": "2026-02-24T09:00:00Z"
    },
    {
      "platform": "linkedin",
      "status": "processing",
      "post_url": null
    }
  ],
  "video": {
    "generation_status": "in_progress",
    "duration_seconds": 120,
    "avatar_style": "professional"
  },
  "created_at": "2026-02-23T18:35:00Z",
  "estimated_completion": "2026-02-23T18:45:00Z"
}
```

---

#### Get Publishing Job Status
```http
GET /publish/{job_id}
```

Response (200 OK):
```json
{
  "id": "publish-job-123",
  "article_id": "article-456",
  "status": "completed",
  "progress": 100,
  "platforms": [
    {
      "platform": "twitter",
      "status": "published",
      "post_url": "https://twitter.com/kushin77/status/1234567890",
      "engagement": {
        "likes": 156,
        "retweets": 45,
        "replies": 12
      }
    },
    {
      "platform": "linkedin",
      "status": "published",
      "post_url": "https://www.linkedin.com/feed/update/...",
      "engagement": {
        "likes": 234,
        "comments": 18,
        "shares": 23
      }
    }
  ],
  "video": {
    "id": "video-789",
    "status": "published",
    "url": "https://video.dev.elevatediq.ai/v789",
    "duration": 120,
    "view_count": 3456
  },
  "completed_at": "2026-02-23T18:42:00Z"
}
```

---

### Health & Monitoring

#### Service Health
```http
GET /health
```

Response (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-23T18:40:00Z",
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "queue": "healthy",
    "external_apis": {
      "claude": "healthy",
      "elevenlabs": "healthy",
      "did": "healthy"
    }
  },
  "metrics": {
    "uptime_seconds": 864000,
    "requests_per_second": 250,
    "error_rate": 0.001,
    "avg_response_time_ms": 145
  }
}
```

---

#### Metrics
```http
GET /metrics
```

Response (200 OK):
```json
{
  "timestamp": "2026-02-23T18:40:00Z",
  "global": {
    "total_articles": 125000,
    "total_videos": 15000,
    "total_posts": 450000,
    "feeds_active": 145,
    "feeds_paused": 5
  },
  "daily": {
    "articles_ingested": 1200,
    "articles_analyzed": 980,
    "articles_published": 450,
    "videos_generated": 120,
    "social_posts": 1800
  },
  "performance": {
    "avg_ingestion_time_ms": 250,
    "avg_analysis_time_ms": 3000,
    "avg_video_generation_time_ms": 45000,
    "avg_publishing_time_ms": 5000
  },
  "quality": {
    "avg_sentiment_score": 0.68,
    "avg_quality_score": 0.87,
    "trending_articles": 42,
    "high_quality_percentage": 78
  }
}
```

---

## ⚙️ Rate Limiting

All API endpoints are rate limited to prevent abuse.

### Limits
- **Default**: 1000 requests/hour per API key
- **Premium**: 10000 requests/hour
- **Enterprise**: Custom limits

### Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
X-RateLimit-Reset: 1645128000
```

When limit exceeded:
```http
HTTP/1.1 429 Too Many Requests

{
  "error": "rate_limit_exceeded",
  "message": "1000 requests per hour limit exceeded",
  "retry_after": 3600
}
```

---

##  Error Handling

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily down |

### Error Response Format
```json
{
  "error": "article_not_found",
  "message": "The requested article could not be found",
  "error_id": "err-123-abc",
  "timestamp": "2026-02-23T18:40:00Z",
  "request_id": "req-456-def",
  "documentation": "https://docs.example.com/errors/article_not_found"
}
```

---

## 🚀 Code Examples

### Python
```python
import requests
from datetime import datetime, timedelta

API_KEY = "sk-news-feed-engine-..."
BASE_URL = "https://api.dev.elevatediq.ai/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Get trending articles
response = requests.get(
    f"{BASE_URL}/articles",
    params={
        "limit": 10,
        "sort": "trending",
        "category": "technology"
    },
    headers=headers
)

articles = response.json()["articles"]

# Analyze first article
article = articles[0]
analysis = requests.post(
    f"{BASE_URL}/articles/{article['id']}/analyze",
    json={"generate_summary": True},
    headers=headers
).json()

print(f"Sentiment: {analysis['analysis']['sentiment']['overall']}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_KEY = "sk-news-feed-engine-...";
const BASE_URL = "https://api.dev.elevatediq.ai/v1";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  }
});

// List articles
async function getTrendingArticles() {
  const response = await client.get('/articles', {
    params: {
      limit: 10,
      sort: 'trending',
      category: 'technology'
    }
  });
  return response.data.articles;
}

// Publish article
async function publishArticle(articleId) {
  const response = await client.post(
    `/articles/${articleId}/publish`,
    {
      platforms: ['twitter', 'linkedin'],
      with_video: true
    }
  );
  return response.data;
}

getTrendingArticles().then(console.log);
```

### Go
```go
package main

import (
  "fmt"
  "io"
  "net/http"
)

func main() {
  client := &http.Client{}
  
  req, _ := http.NewRequest("GET", 
    "https://api.dev.elevatediq.ai/v1/articles?limit=10&sort=trending",
    nil)
  req.Header.Set("Authorization", "Bearer sk-news-feed-engine-...")
  
  resp, _ := client.Do(req)
  defer resp.Body.Close()
  
  body, _ := io.ReadAll(resp.Body)
  fmt.Println(string(body))
}
```

---

## 📚 Additional Resources

- [API Changelog](./CHANGELOG.md)
- [Webhooks Guide](./WEBHOOKS.md)
- [SDK Documentation](./SDK.md)
- [Postman Collection](./postman-collection.json)
- [GraphQL API](./GRAPHQL.md)

---

**API Version**: 1.0  
**Last Updated**: February 23, 2026  
**Support**: api-support@elevatediq.ai
