# Elite AI News Feed Engine - API Reference

## Overview

The ElevatedIQ News Feed Engine is an enterprise-grade, AI-powered content automation platform. This document provides comprehensive API documentation for all modules.

---

## Table of Contents

1. [Configuration Module](#configuration-module)
2. [Predictive Engine](#predictive-engine)
3. [AI Agents](#ai-agents)
4. [Video Factory](#video-factory)
5. [Trend Sources](#trend-sources)
6. [Publishing Orchestrator](#publishing-orchestrator)
7. [Analytics Pipeline](#analytics-pipeline)
8. [OAuth Manager](#oauth-manager)
9. [Media Manager](#media-manager)
10. [Platform Publishers](#platform-publishers)

---

## Configuration Module

**Module:** `processor.config`

### Settings

Centralized configuration management using Pydantic BaseSettings.

```python
from processor.config import get_settings, utc_now, Settings

# Get singleton settings instance
settings = get_settings()

# Access configuration values
print(settings.environment)  # 'development' | 'staging' | 'production'
print(settings.postgres_dsn)
print(settings.kafka_bootstrap_servers)

# Get current UTC timestamp
current_time = utc_now()
```bash

#### Key Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `environment` | str | Runtime environment |
| `postgres_dsn` | str | PostgreSQL connection string |
| `redis_url` | str | Redis connection URL |
| `kafka_bootstrap_servers` | str | Kafka broker addresses |
| `openai_api_key` | str | OpenAI API key |
| `anthropic_api_key` | str | Anthropic Claude API key |
| `elevenlabs_api_key` | str | ElevenLabs voice API key |
| `did_api_key` | str | D-ID video generation API key |

---

## Predictive Engine

**Module:** `processor.predictive_engine`

### TrendSurfingEngine

Combines multiple predictive models for intelligent content optimization.

```python
from processor.predictive_engine import TrendSurfingEngine, TrendForecaster, ViralityModel

# Initialize the engine
engine = TrendSurfingEngine()

# Predict content performance
prediction = engine.predict_performance({
    "title": "AI Revolution 2024",
    "category": "technology",
    "tags": ["ai", "tech", "future"]
})

# Get trend forecasts
forecaster = TrendForecaster()
forecast = forecaster.forecast_trend("artificial intelligence", days=7)
```bash

### ViralityModel

Predicts viral potential of content.

```python
from processor.predictive_engine import ViralityModel

model = ViralityModel()
score = model.score({
    "title": "Breaking: Major Discovery",
    "engagement_history": [],
    "platform": "youtube"
})
print(f"Virality Score: {score}")  # 0.0 - 1.0
```bash

### AudienceMatcher

Matches content to target audience segments.

```python
from processor.predictive_engine import AudienceMatcher

matcher = AudienceMatcher()
segments = matcher.match_audience({
    "content_type": "tech_news",
    "topics": ["AI", "machine learning"]
})
```bash

---

## AI Agents

**Module:** `processor.ai_agents`

### Agent System Architecture

The AI agent system uses a multi-agent orchestration pattern with 5 specialized agents:

1. **AnalystAgent** - Market and trend analysis
2. **ContentCuratorAgent** - Content selection and curation
3. **VideoProducerAgent** - Video script and production
4. **DistributorAgent** - Multi-platform distribution
5. **EngagementAgent** - Audience engagement optimization

### AgentOrchestrator

Coordinates all agents for autonomous content creation.

```python
from processor.ai_agents import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Start autonomous processing
await orchestrator.start()

# Stop processing
await orchestrator.stop()
```bash

### AgentMessage

Communication between agents.

```python
from processor.ai_agents import AgentMessage, MessageType

message = AgentMessage(
    id="msg-001",
    sender="analyst",
    recipient="curator",
    message_type=MessageType.TASK,
    payload={"trend_data": {...}},
    priority=5
)
```bash

### AgentDecision

Record agent decisions for auditing.

```python
from processor.ai_agents import AgentDecision

decision = AgentDecision(
    decision_id="dec-001",
    agent_name="content_curator",
    decision_type="content_approval",
    input_data={"content_id": "123"},
    reasoning="High trend score and audience match",
    action="approve",
    confidence=0.92
)
```bash

---

## Video Factory

**Module:** `processor.video_factory`

### VideoScript

Structured video script generation.

```python
from processor.video_factory import VideoScript

script = VideoScript(
    title="AI Breaking News",
    hook="The future is here...",
    body="In today's segment, we explore...",
    call_to_action="Subscribe for daily updates!"
)

# Access script properties
print(script.estimated_duration)  # seconds
print(script.total_words)
```bash

### VideoScriptGenerator

AI-powered script generation.

```python
from processor.video_factory import VideoScriptGenerator

generator = VideoScriptGenerator()

script = await generator.generate(
    topic="Latest AI Developments",
    platform="youtube",
    target_duration=60
)
```bash

### VideoFactory

Complete video production pipeline.

```python
from processor.video_factory import VideoFactory

factory = VideoFactory()

video = await factory.create_video(
    script=script,
    voice_style="professional",
    avatar="news_anchor"
)
```bash

### ElevenLabsClient

Voice synthesis integration.

```python
from processor.video_factory import ElevenLabsClient

client = ElevenLabsClient()

audio = await client.synthesize(
    text="Welcome to today's news.",
    voice_id="professional_anchor"
)
```bash

### DIDClient

AI avatar video generation.

```python
from processor.video_factory import DIDClient

client = DIDClient()

video = await client.generate_video(
    script="Today's top story...",
    avatar="professional_anchor"
)
```bash

---

## Trend Sources

**Module:** `processor.trend_sources`

### TrendItem

Standardized trend data structure.

```python
from processor.trend_sources import TrendItem

trend = TrendItem(
    id="trend-001",
    name="AI Technology",
    source="google",
    score=0.85,
    volume=150000,
    growth_rate=0.25,
    category="technology"
)
```bash

### TrendAggregator

Aggregates trends from multiple sources.

```python
from processor.trend_sources import TrendAggregator

aggregator = TrendAggregator()

# Fetch trends from all sources
trends = await aggregator.fetch_all_trends()

# Get top trends
top_trends = await aggregator.get_top_trends(limit=10)
```bash

### Trend Sources

Available trend sources:

- `GoogleTrendsSource` - Google Trends API
- `TwitterTrendsSource` - Twitter/X trending topics
- `RedditTrendsSource` - Reddit popular posts
- `TikTokTrendsSource` - TikTok trending hashtags
- `YouTubeTrendsSource` - YouTube trending videos
- `NewsAPISource` - NewsAPI headlines

```python
from processor.trend_sources import GoogleTrendsSource

source = GoogleTrendsSource()
trends = await source.fetch_trends(region="US")
```bash

---

## Publishing Orchestrator

**Module:** `processor.publishing_orchestrator`

### Platform Enum

Supported publishing platforms.

```python
from processor.publishing_orchestrator import Platform

# Available platforms
Platform.YOUTUBE
Platform.YOUTUBE_SHORTS
Platform.TIKTOK
Platform.INSTAGRAM_REELS
Platform.INSTAGRAM_FEED
Platform.INSTAGRAM_STORIES
Platform.FACEBOOK
Platform.FACEBOOK_REELS
Platform.LINKEDIN
Platform.LINKEDIN_VIDEO
Platform.TWITTER
Platform.THREADS
Platform.SNAPCHAT
Platform.PINTEREST
```bash

### PublishingOrchestrator

Coordinates multi-platform publishing.

```python
from processor.publishing_orchestrator import PublishingOrchestrator, Platform

orchestrator = PublishingOrchestrator()

result = await orchestrator.publish(
    content={"video": video_data, "title": "Breaking News"},
    platforms=[Platform.YOUTUBE, Platform.TIKTOK],
    schedule_time=None  # None for immediate publish
)
```bash

### PublishResult

Publishing result data.

```python
from processor.publishing_orchestrator import PublishResult, Platform

result = PublishResult(
    platform=Platform.YOUTUBE,
    success=True,
    post_id="abc123",
    url="https://youtube.com/watch?v=abc123"
)
```bash

### TimingOptimizer

Optimize publishing times for maximum engagement.

```python
from processor.publishing_orchestrator import TimingOptimizer, Platform

optimizer = TimingOptimizer()

optimal_times = optimizer.get_optimal_times(
    platform=Platform.YOUTUBE,
    content={"category": "tech"},
    num_times=3
)
```bash

### HashtagOptimizer

Generate optimized hashtags.

```python
from processor.publishing_orchestrator import HashtagOptimizer, Platform

optimizer = HashtagOptimizer()

hashtags = await optimizer.optimize_hashtags(
    content={"title": "AI News", "tags": ["ai"]},
    platform=Platform.INSTAGRAM_REELS,
    max_hashtags=30
)
```bash

### RateLimiter

Platform-aware rate limiting.

```python
from processor.publishing_orchestrator import RateLimiter

limiter = RateLimiter()

if await limiter.can_publish(Platform.YOUTUBE):
    await publish_video()
    await limiter.record_publish(Platform.YOUTUBE)
```bash

---

## Analytics Pipeline

**Module:** `processor.analytics_pipeline`

### EventType Enum

Analytics event types.

```python
from processor.analytics_pipeline import EventType

EventType.CONTENT_CREATED
EventType.VIDEO_PRODUCED
EventType.PUBLISH_SUCCESS
EventType.PUBLISH_FAILED
EventType.ENGAGEMENT_UPDATE
EventType.TREND_DETECTED
```bash

### PipelineEvent

Analytics event data.

```python
from processor.analytics_pipeline import PipelineEvent, EventType
from processor.config import utc_now

event = PipelineEvent(
    event_id="evt-001",
    event_type=EventType.CONTENT_CREATED,
    timestamp=utc_now(),
    source="content_curator",
    data={"content_id": "123", "type": "video"}
)

# Serialize event
event_dict = event.to_dict()
event_json = event.to_json()
```bash

### AnalyticsPipeline

Event processing pipeline.

```python
from processor.analytics_pipeline import AnalyticsPipeline

pipeline = AnalyticsPipeline()

# Start pipeline
await pipeline.start()

# Process event
await pipeline.process_event(event)

# Stop pipeline
await pipeline.stop()
```bash

### MetricsExporter

Prometheus metrics export.

```python
from processor.analytics_pipeline import MetricsExporter

exporter = MetricsExporter()

# Record metric
exporter.record_publish_success("youtube")
exporter.record_publish_latency("tiktok", 1.5)
```bash

---

## OAuth Manager

**Module:** `processor.oauth_manager`

### OAuthToken

OAuth token data structure.

```python
from processor.oauth_manager import OAuthToken
from processor.config import utc_now

token = OAuthToken(
    access_token="abc123",
    token_type="Bearer",
    expires_in=3600,
    refresh_token="xyz789",
    platform="youtube",
    created_at=utc_now()
)

# Check if token expired
if token.is_expired:
    token = await refresh_token(token)

# Convert to dict
token_dict = token.to_dict()
```bash

### OAuthState

OAuth flow state management.

```python
from processor.oauth_manager import OAuthState

state = OAuthState(
    state="random_state_string",
    platform="youtube",
    redirect_uri="https://api.example.com/callback"
)
```bash

### OAuthManager

Manages OAuth flows for all platforms.

```python
from processor.oauth_manager import OAuthManager

manager = OAuthManager()

# Generate auth URL
auth_url = await manager.get_auth_url("youtube", user_id="user-001")

# Handle callback
token = await manager.handle_callback("youtube", code="auth_code")

# Refresh token
new_token = await manager.refresh_token("youtube", user_id="user-001")
```bash

### Token Storage

Token storage implementations.

```python
from processor.oauth_manager import InMemoryTokenStorage, EncryptedTokenStorage

# In-memory (development)
storage = InMemoryTokenStorage()

# Encrypted (production)
storage = EncryptedTokenStorage(encryption_key="...")

# Store token
await storage.save_token(user_id, platform, token)

# Get token
token = await storage.get_token(user_id, platform)

# Delete token
await storage.delete_token(user_id, platform)
```bash

---

## Media Manager

**Module:** `processor.media_manager`

### AssetType Enum

Media asset types.

```python
from processor.media_manager import AssetType

AssetType.VIDEO
AssetType.IMAGE
AssetType.AUDIO
AssetType.DOCUMENT
```bash

### MediaAsset

Media asset data structure.

```python
from processor.media_manager import MediaAsset, AssetType, AssetURLs

urls = AssetURLs(
    original="https://storage.example.com/video.mp4",
    cdn="https://cdn.example.com/video.mp4",
    thumbnails={"small": "https://cdn.example.com/thumb.jpg"},
    optimized={"720p": "https://cdn.example.com/video_720.mp4"},
    transcoded={"webm": "https://cdn.example.com/video.webm"}
)

asset = MediaAsset(
    id="asset-001",
    tenant_id="tenant-001",
    type=AssetType.VIDEO,
    source_platform="youtube",
    urls=urls,
    filename="video.mp4",
    file_size=10485760,
    mime_type="video/mp4",
    width=1920,
    height=1080,
    duration=60.0
)
```bash

### CDNManager

Content delivery network integration.

```python
from processor.media_manager import CDNManager

cdn = CDNManager()

# Upload to CDN
cdn_url = await cdn.upload(asset_data, content_type="video/mp4")

# Get signed URL
signed_url = await cdn.get_signed_url(asset_id, expiry=3600)
```bash

### MediaManagerClient

Complete media management.

```python
from processor.media_manager import MediaManagerClient

client = MediaManagerClient()

# Upload asset
asset = await client.upload(
    file_data=video_bytes,
    filename="video.mp4",
    content_type="video/mp4"
)

# Get asset
asset = await client.get_asset(asset_id)

# Delete asset
await client.delete_asset(asset_id)
```bash

---

## Platform Publishers

**Module:** `processor.platform_publishers`

Platform-specific publishing implementations.

### YouTubePublisher

```python
from processor.platform_publishers import YouTubePublisher

publisher = YouTubePublisher()

result = await publisher.publish(
    video_path="/path/to/video.mp4",
    title="Breaking News",
    description="Today's top story...",
    tags=["news", "breaking"]
)
```bash

### TikTokPublisher

```python
from processor.platform_publishers import TikTokPublisher

publisher = TikTokPublisher()

result = await publisher.publish(
    video_path="/path/to/video.mp4",
    caption="Check this out! #fyp #viral"
)
```bash

### InstagramPublisher

```python
from processor.platform_publishers import InstagramPublisher

publisher = InstagramPublisher()

result = await publisher.publish_reel(
    video_path="/path/to/video.mp4",
    caption="Watch now!",
    cover_timestamp=5
)
```bash

---

## Error Handling

All modules use structured error handling:

```python
from processor.exceptions import (
    ProcessorError,
    ConfigurationError,
    PublishingError,
    VideoGenerationError,
    OAuthError,
    TrendFetchError
)

try:
    result = await orchestrator.publish(content, platforms)
except PublishingError as e:
    logger.error(f"Publishing failed: {e.platform} - {e.message}")
except ProcessorError as e:
    logger.error(f"General error: {e}")
```bash

---

## Best Practices

### 1. Use Async/Await

All I/O operations are async:

```python
# Correct
results = await asyncio.gather(
    fetch_google_trends(),
    fetch_twitter_trends(),
    fetch_reddit_trends()
)

# Incorrect
results = [
    fetch_google_trends(),  # Returns coroutine, not data!
    ...
]
```bash

### 2. Configuration Management

Always use `get_settings()` for configuration:

```python
from processor.config import get_settings

settings = get_settings()
api_key = settings.openai_api_key  # ✓ Correct

# Don't hardcode values
api_key = "sk-..."  # ✗ Wrong
```bash

### 3. Timezone Aware Timestamps

Always use `utc_now()` for timestamps:

```python
from processor.config import utc_now

timestamp = utc_now()  # ✓ Correct, timezone-aware

from datetime import datetime
timestamp = datetime.now()  # ✗ Wrong, naive datetime
```bash

### 4. Rate Limiting

Always respect platform rate limits:

```python
from processor.publishing_orchestrator import RateLimiter

limiter = RateLimiter()
if await limiter.can_publish(platform):
    await publish()
else:
    await schedule_for_later()
```bash

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-11-26 | Initial Elite AI release |

---

## Support

For issues and questions, contact the ElevatedIQ team.
