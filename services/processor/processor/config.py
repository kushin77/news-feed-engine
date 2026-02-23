"""
ElevatedIQ News Feed Processor - Elite Configuration Module
Comprehensive configuration with GCP Secret Manager integration

Enhanced with support for:
- AI/ML Services (Claude, OpenAI, ElevenLabs, D-ID)
- Video Generation Pipeline
- Media Manager Integration
- Social Platform APIs
- Trend Data Sources
- Infrastructure Services
"""

import logging
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


def utc_now() -> datetime:
    """Return timezone-aware UTC datetime (replacement for deprecated datetime.now(timezone.utc))."""
    return datetime.now(timezone.utc)


logger = logging.getLogger(__name__)


# =============================================================================
# Core Settings Class
# =============================================================================


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment
    environment: str = Field(default="development", alias="ELEVATEDIQ_ENVIRONMENT")
    log_level: str = Field(default="info", alias="ELEVATEDIQ_LOG_LEVEL")
    debug: bool = Field(default=False, alias="DEBUG")

    # ==========================================================================
    # Database Configuration
    # ==========================================================================
    postgres_dsn: str = Field(
        default=(
            "postgresql://postgres:postgres@" "elevatediq-postgres:5432/news_feed"
        ),
        alias="POSTGRES_DSN",
    )
    postgres_host: str = Field(default="elevatediq-postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="news_feed", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default=None, alias="POSTGRES_PASSWORD")
    postgres_ssl: str = Field(default="require", alias="POSTGRES_SSL")

    redis_url: str = Field(default="redis://elevatediq-redis:6379/1", alias="REDIS_URL")
    mongo_uri: str = Field(
        default="mongodb://elevatediq-mongodb02:27017/news_feed", alias="MONGO_URI"
    )

    # ==========================================================================
    # Kafka Configuration
    # ==========================================================================
    kafka_bootstrap_servers: str = Field(
        default="elevatediq-kafka:9092", alias="KAFKA_BOOTSTRAP_SERVERS"
    )
    kafka_consumer_group: str = Field(
        default="news-feed-processor", alias="KAFKA_CONSUMER_GROUP"
    )
    kafka_input_topic: str = Field(
        default="news-feed-raw-content", alias="KAFKA_INPUT_TOPIC"
    )
    kafka_output_topic: str = Field(
        default="news-feed-processed-content", alias="KAFKA_OUTPUT_TOPIC"
    )
    kafka_video_topic: str = Field(
        default="news-feed-video-jobs", alias="KAFKA_VIDEO_TOPIC"
    )
    kafka_analytics_topic: str = Field(
        default="news-feed-analytics-events", alias="KAFKA_ANALYTICS_TOPIC"
    )

    # ==========================================================================
    # AI/ML Services
    # ==========================================================================
    # Anthropic Claude
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022", alias="CLAUDE_MODEL"
    )
    claude_max_tokens: int = Field(default=4096, alias="CLAUDE_MAX_TOKENS")

    # OpenAI (Embeddings)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    embedding_model: str = Field(
        default="text-embedding-3-small", alias="EMBEDDING_MODEL"
    )

    # ==========================================================================
    # Video Generation Services
    # ==========================================================================
    # ElevenLabs TTS
    elevenlabs_api_key: Optional[str] = Field(default=None, alias="ELEVENLABS_API_KEY")
    elevenlabs_base_url: str = Field(
        default="https://api.elevenlabs.io/v1", alias="ELEVENLABS_BASE_URL"
    )
    elevenlabs_default_voice: str = Field(
        default="professional", alias="ELEVENLABS_DEFAULT_VOICE"
    )
    elevenlabs_stability: float = Field(default=0.5, alias="ELEVENLABS_STABILITY")
    elevenlabs_similarity_boost: float = Field(
        default=0.75, alias="ELEVENLABS_SIMILARITY_BOOST"
    )

    # D-ID Avatar
    did_api_key: Optional[str] = Field(default=None, alias="DID_API_KEY")
    did_base_url: str = Field(default="https://api.d-id.com", alias="DID_BASE_URL")
    did_default_avatar: str = Field(
        default="professional_anchor", alias="DID_DEFAULT_AVATAR"
    )
    did_poll_interval: int = Field(default=5, alias="DID_POLL_INTERVAL")
    did_timeout: int = Field(default=300, alias="DID_TIMEOUT")

    # Runway ML
    runway_api_key: Optional[str] = Field(default=None, alias="RUNWAY_API_KEY")

    # Heygen
    heygen_api_key: Optional[str] = Field(default=None, alias="HEYGEN_API_KEY")

    # ==========================================================================
    # Media Manager Integration
    # ==========================================================================
    media_manager_url: str = Field(
        default="http://media-manager:8080", alias="MEDIA_MANAGER_URL"
    )
    media_manager_api_key: Optional[str] = Field(
        default=None, alias="MEDIA_MANAGER_API_KEY"
    )
    cdn_base_url: str = Field(default="https://cdn.elevatediq.ai", alias="CDN_BASE_URL")
    cdn_api_key: Optional[str] = Field(default=None, alias="CDN_API_KEY")
    media_storage_provider: str = Field(default="gcs", alias="MEDIA_STORAGE_PROVIDER")
    media_bucket: str = Field(default="elevatediq-media", alias="MEDIA_BUCKET")

    # ==========================================================================
    # Social Platform APIs
    # ==========================================================================
    # YouTube
    youtube_api_key: Optional[str] = Field(default=None, alias="YOUTUBE_API_KEY")
    youtube_client_id: Optional[str] = Field(default=None, alias="YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[str] = Field(
        default=None, alias="YOUTUBE_CLIENT_SECRET"
    )
    youtube_redirect_uri: str = Field(
        default="https://api.elevatediq.ai/oauth/youtube/callback",
        alias="YOUTUBE_REDIRECT_URI",
    )

    # Twitter/X
    twitter_api_key: Optional[str] = Field(default=None, alias="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, alias="TWITTER_API_SECRET")
    twitter_bearer_token: Optional[str] = Field(
        default=None, alias="TWITTER_BEARER_TOKEN"
    )
    twitter_access_token: Optional[str] = Field(
        default=None, alias="TWITTER_ACCESS_TOKEN"
    )
    twitter_access_secret: Optional[str] = Field(
        default=None, alias="TWITTER_ACCESS_SECRET"
    )
    twitter_client_id: Optional[str] = Field(default=None, alias="TWITTER_CLIENT_ID")
    twitter_client_secret: Optional[str] = Field(
        default=None, alias="TWITTER_CLIENT_SECRET"
    )

    # TikTok
    tiktok_client_key: Optional[str] = Field(default=None, alias="TIKTOK_CLIENT_KEY")
    tiktok_client_secret: Optional[str] = Field(
        default=None, alias="TIKTOK_CLIENT_SECRET"
    )
    tiktok_redirect_uri: str = Field(
        default="https://api.elevatediq.ai/oauth/tiktok/callback",
        alias="TIKTOK_REDIRECT_URI",
    )

    # LinkedIn
    linkedin_client_id: Optional[str] = Field(default=None, alias="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(
        default=None, alias="LINKEDIN_CLIENT_SECRET"
    )
    linkedin_redirect_uri: str = Field(
        default="https://api.elevatediq.ai/oauth/linkedin/callback",
        alias="LINKEDIN_REDIRECT_URI",
    )

    # Instagram
    instagram_app_id: Optional[str] = Field(default=None, alias="INSTAGRAM_APP_ID")
    instagram_app_secret: Optional[str] = Field(
        default=None, alias="INSTAGRAM_APP_SECRET"
    )
    instagram_access_token: Optional[str] = Field(
        default=None, alias="INSTAGRAM_ACCESS_TOKEN"
    )

    # Facebook
    facebook_app_id: Optional[str] = Field(default=None, alias="FACEBOOK_APP_ID")
    facebook_app_secret: Optional[str] = Field(
        default=None, alias="FACEBOOK_APP_SECRET"
    )
    facebook_access_token: Optional[str] = Field(
        default=None, alias="FACEBOOK_ACCESS_TOKEN"
    )

    # Snapchat
    snapchat_client_id: Optional[str] = Field(default=None, alias="SNAPCHAT_CLIENT_ID")
    snapchat_client_secret: Optional[str] = Field(
        default=None, alias="SNAPCHAT_CLIENT_SECRET"
    )

    # Pinterest
    pinterest_app_id: Optional[str] = Field(default=None, alias="PINTEREST_APP_ID")
    pinterest_app_secret: Optional[str] = Field(
        default=None, alias="PINTEREST_APP_SECRET"
    )

    # Threads
    threads_app_id: Optional[str] = Field(default=None, alias="THREADS_APP_ID")
    threads_app_secret: Optional[str] = Field(default=None, alias="THREADS_APP_SECRET")

    # ==========================================================================
    # Trend Data Sources
    # ==========================================================================
    # Reddit
    reddit_client_id: Optional[str] = Field(default=None, alias="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(
        default=None, alias="REDDIT_CLIENT_SECRET"
    )
    reddit_user_agent: str = Field(default="ElevatedIQ/1.0", alias="REDDIT_USER_AGENT")

    # NewsAPI
    newsapi_api_key: Optional[str] = Field(default=None, alias="NEWSAPI_API_KEY")

    # ==========================================================================
    # Processing Settings
    # ==========================================================================
    batch_size: int = Field(default=10, alias="BATCH_SIZE")
    max_workers: int = Field(default=4, alias="MAX_WORKERS")

    # ==========================================================================
    # GCP Settings
    # ==========================================================================
    gcp_project_id: str = Field(default="elevatediq-production", alias="GCP_PROJECT_ID")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

    # ==========================================================================
    # Voice ID Mappings
    # ==========================================================================
    @property
    def elevenlabs_voices(self) -> Dict[str, str]:
        """ElevenLabs voice ID mappings."""
        return {
            "news_anchor_male": "pNInz6obpgDQGcFmaJgB",
            "news_anchor_female": "21m00Tcm4TlvDq8ikWAM",
            "professional": "EXAVITQu4vr4xnSDxMaL",
            "casual": "MF3mGyEYCl7XYWbV9V6O",
            "enthusiastic": "jBpfuIE2acCO8z3wKNLl",
        }

    @property
    def did_avatars(self) -> Dict[str, str]:
        """D-ID avatar ID mappings."""
        return {
            "professional_anchor": "amy-jcvszISHVb",
            "casual_presenter": "josh-MNu4zHfHyE",
            "tech_expert": "sara-BLVsyNPLKZ",
            "news_reporter": "anna-KHlzN8TvMc",
        }

    # ==========================================================================
    # Validation Methods
    # ==========================================================================
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return any issues."""
        issues = {
            "critical": [],
            "warning": [],
            "info": [],
        }

        # Critical: AI services
        if not self.anthropic_api_key:
            issues["critical"].append("ANTHROPIC_API_KEY not configured")

        # Warning: Video generation
        if not self.elevenlabs_api_key:
            issues["warning"].append("ELEVENLABS_API_KEY not configured - TTS disabled")
        if not self.did_api_key:
            issues["warning"].append(
                "DID_API_KEY not configured - avatar videos disabled"
            )

        # Warning: Media Manager
        if not self.media_manager_api_key:
            issues["warning"].append("MEDIA_MANAGER_API_KEY not configured")

        # Info: Social platforms
        if not self.youtube_api_key:
            issues["info"].append("YouTube API not configured")
        if not self.twitter_bearer_token:
            issues["info"].append("Twitter API not configured")
        if not self.tiktok_client_key:
            issues["info"].append("TikTok API not configured")
        if not self.linkedin_client_id:
            issues["info"].append("LinkedIn API not configured")

        return issues

    def get_masked_dict(self) -> Dict[str, Any]:
        """Get config as dict with masked secrets for logging."""

        def mask(value: Optional[str]) -> str:
            if not value:
                return "<not set>"
            if len(value) <= 8:
                return "*" * len(value)
            return value[:4] + "*" * (len(value) - 8) + value[-4:]

        return {
            "environment": self.environment,
            "debug": self.debug,
            "anthropic_api_key": mask(self.anthropic_api_key),
            "elevenlabs_api_key": mask(self.elevenlabs_api_key),
            "did_api_key": mask(self.did_api_key),
            "media_manager_url": self.media_manager_url,
            "youtube_api_key": mask(self.youtube_api_key),
            "twitter_bearer_token": mask(self.twitter_bearer_token),
        }


# =============================================================================
# GCP Secret Manager Integration
# =============================================================================


class GCPSecretManager:
    """Manages secrets from Google Cloud Secret Manager."""

    _instance = None
    _client = None
    _cache: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self):
        if self._client is None:
            try:
                from google.cloud import secretmanager

                self._client = secretmanager.SecretManagerServiceClient()
            except ImportError:
                logger.warning("google-cloud-secret-manager not installed")
                return None
            except Exception as e:
                logger.warning(f"Failed to initialize GCP Secret Manager: {e}")
                return None
        return self._client

    def get_secret(self, secret_id: str, project_id: str = None) -> Optional[str]:
        """Retrieve a secret from GCP Secret Manager with caching."""
        cache_key = f"{project_id}:{secret_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.client is None:
            return None

        try:
            settings = get_settings()
            project = project_id or settings.gcp_project_id
            secret_path = f"projects/{project}/secrets/{secret_id}/versions/latest"

            response = self.client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            self._cache[cache_key] = secret_value
            return secret_value
        except Exception as e:
            logger.warning(f"Failed to retrieve secret {secret_id}: {e}")
            return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def load_secret_from_gcp(secret_id: str) -> Optional[str]:
    """Load a secret from GCP Secret Manager"""
    return GCPSecretManager().get_secret(secret_id)


def get_api_key(key_name: str) -> Optional[str]:
    """Get API key from environment or GCP Secret Manager"""
    settings = get_settings()

    # Extended key mappings for all services
    key_mapping = {
        # AI Services
        "anthropic": ("anthropic_api_key", "news-feed-claude-api-key"),
        "openai": ("openai_api_key", "news-feed-openai-api-key"),
        # Video Generation
        "elevenlabs": ("elevenlabs_api_key", "news-feed-elevenlabs-api-key"),
        "did": ("did_api_key", "news-feed-did-api-key"),
        "runway": ("runway_api_key", "news-feed-runway-api-key"),
        "heygen": ("heygen_api_key", "news-feed-heygen-api-key"),
        # Media Manager
        "media_manager": ("media_manager_api_key", "news-feed-media-manager-api-key"),
        "cdn": ("cdn_api_key", "news-feed-cdn-api-key"),
        # Social Platforms
        "youtube": ("youtube_api_key", "news-feed-youtube-api-key"),
        "youtube_client_id": ("youtube_client_id", "news-feed-youtube-client-id"),
        "youtube_client_secret": (
            "youtube_client_secret",
            "news-feed-youtube-client-secret",
        ),
        "twitter": ("twitter_api_key", "news-feed-twitter-api-key"),
        "twitter_secret": ("twitter_api_secret", "news-feed-twitter-api-secret"),
        "twitter_bearer": ("twitter_bearer_token", "news-feed-twitter-bearer-token"),
        "tiktok": ("tiktok_client_key", "news-feed-tiktok-client-key"),
        "tiktok_secret": ("tiktok_client_secret", "news-feed-tiktok-client-secret"),
        "linkedin": ("linkedin_client_id", "news-feed-linkedin-client-id"),
        "linkedin_secret": (
            "linkedin_client_secret",
            "news-feed-linkedin-client-secret",
        ),
        "instagram": ("instagram_app_id", "news-feed-instagram-app-id"),
        "instagram_secret": ("instagram_app_secret", "news-feed-instagram-app-secret"),
        "facebook": ("facebook_app_id", "news-feed-facebook-app-id"),
        "facebook_secret": ("facebook_app_secret", "news-feed-facebook-app-secret"),
        # Trend Sources
        "reddit": ("reddit_client_id", "news-feed-reddit-client-id"),
        "reddit_secret": ("reddit_client_secret", "news-feed-reddit-client-secret"),
        "newsapi": ("newsapi_api_key", "news-feed-newsapi-api-key"),
    }

    if key_name not in key_mapping:
        return None

    attr_name, gcp_secret_id = key_mapping[key_name]

    # First try environment variable
    value = getattr(settings, attr_name, None)
    if value:
        return value

    # Fall back to GCP Secret Manager in production
    if settings.environment == "production":
        return load_secret_from_gcp(gcp_secret_id)

    return None


# =============================================================================
# Convenience Functions
# =============================================================================


def get_elevenlabs_config() -> Dict[str, Any]:
    """Get ElevenLabs configuration."""
    settings = get_settings()
    return {
        "api_key": get_api_key("elevenlabs") or "",
        "base_url": settings.elevenlabs_base_url,
        "default_voice": settings.elevenlabs_default_voice,
        "voices": settings.elevenlabs_voices,
        "stability": settings.elevenlabs_stability,
        "similarity_boost": settings.elevenlabs_similarity_boost,
    }


def get_did_config() -> Dict[str, Any]:
    """Get D-ID configuration."""
    settings = get_settings()
    return {
        "api_key": get_api_key("did") or "",
        "base_url": settings.did_base_url,
        "default_avatar": settings.did_default_avatar,
        "avatars": settings.did_avatars,
        "poll_interval": settings.did_poll_interval,
        "timeout": settings.did_timeout,
    }


def get_media_manager_config() -> Dict[str, Any]:
    """Get Media Manager configuration."""
    settings = get_settings()
    return {
        "base_url": settings.media_manager_url,
        "api_key": get_api_key("media_manager") or "",
        "cdn_base_url": settings.cdn_base_url,
        "cdn_api_key": get_api_key("cdn") or "",
        "storage_provider": settings.media_storage_provider,
        "storage_bucket": settings.media_bucket,
    }


def get_youtube_config() -> Dict[str, Any]:
    """Get YouTube configuration."""
    settings = get_settings()
    return {
        "api_key": get_api_key("youtube") or "",
        "client_id": get_api_key("youtube_client_id") or "",
        "client_secret": get_api_key("youtube_client_secret") or "",
        "redirect_uri": settings.youtube_redirect_uri,
    }


def get_twitter_config() -> Dict[str, Any]:
    """Get Twitter configuration."""
    settings = get_settings()
    return {
        "api_key": get_api_key("twitter") or "",
        "api_secret": get_api_key("twitter_secret") or "",
        "bearer_token": get_api_key("twitter_bearer") or "",
        "access_token": settings.twitter_access_token or "",
        "access_secret": settings.twitter_access_secret or "",
        "client_id": settings.twitter_client_id or "",
        "client_secret": settings.twitter_client_secret or "",
    }


def get_kafka_config() -> Dict[str, Any]:
    """Get Kafka configuration."""
    settings = get_settings()
    return {
        "bootstrap_servers": settings.kafka_bootstrap_servers,
        "consumer_group": settings.kafka_consumer_group,
        "topics": {
            "input": settings.kafka_input_topic,
            "output": settings.kafka_output_topic,
            "video": settings.kafka_video_topic,
            "analytics": settings.kafka_analytics_topic,
        },
    }


# Global settings singleton for convenience imports
settings = get_settings()
