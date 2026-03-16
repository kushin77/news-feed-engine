"""ElevatedIQ News Feed Processor Core Module - Elite AI Enhanced"""

__version__ = "2.0.0"
__author__ = "ElevatedIQ AI Team"

from typing import Any  # noqa: F401

# Core analyzer module (required)
from .analyzer import ContentAnalyzer, VideoScriptGenerator

# Configuration (required)
try:
    from .config import Settings, get_api_key, get_settings
except ImportError:
    pass

# Database (optional - may not be needed for tests)
try:
    from .database import DatabaseClient
except (ImportError, ModuleNotFoundError):
    pass

# Embeddings (optional)
try:
    from .embeddings import EmbeddingGenerator
except (ImportError, ModuleNotFoundError):
    pass

# Media Manager (optional)
try:
    from .media_manager import (
        AIAssetAnalysis,
        AssetType,
        IntelligentAssetRecommender,
        MediaAsset,
        MediaManagerClient,
        MediaManagerIntegration,
        RecommendedAsset,
    )
except (ImportError, ModuleNotFoundError):
    pass

# Elite AI Enhancement Modules (optional - skip on import error)
try:
    from .predictive_engine import (
        AudienceMatcher,
        ContentPrediction,
        PredictiveContentEngine,
        TrendForecaster,
        TrendOpportunity,
        TrendSurfingEngine,
        ViralityModel,
    )
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .publishing_orchestrator import (
        CrossPlatformAnalytics,
        HashtagOptimizer,
        Platform,
        PublishingOrchestrator,
        PublishResult,
        PublishStatus,
        ScheduledPost,
        TimingOptimizer,
    )
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .video_factory import (
        DIDClient,
        ElevenLabsClient,
        LiveVideoGenerator,
        VideoAspectRatio,
        VideoAsset,
        VideoFactory,
        VideoScript,
        VideoScriptGenerator as AdvancedVideoScriptGenerator,
        VideoStyle,
    )
except (ImportError, ModuleNotFoundError):
    pass

# Platform Publishers (optional)
try:
    from .platform_publishers import (
        MultiPlatformPublisher,
        FacebookPublisher,
        InstagramPublisher,
        PinterestPublisher,
        SnapchatPublisher,
        ThreadsPublisher,
    )
except (ImportError, ModuleNotFoundError):
    pass

# AI Agents
try:
    from .ai_agents import (
        AgentMessageBus,
        AgentOrchestrator,
        AnalystAgent,
        ContentCuratorAgent,
        DistributorAgent,
        EngagementAgent,
        VideoProducerAgent,
        create_agent_system,
    )
except ImportError:
    pass

# Trend Sources
try:
    from .trend_sources import (
        GoogleTrendsSource,
        NewsAPISource,
        RedditTrendsSource,
        TikTokTrendsSource,
        TrendAggregator,
        TwitterTrendsSource,
        YouTubeTrendsSource,
        create_trend_aggregator,
    )
except ImportError:
    pass

# Analytics Pipeline
try:
    from .analytics_pipeline import (
        AnalyticsPipeline,
        AnalyticsProcessor,
        EventConsumer,
        EventProducer,
        EventType,
        MetricsExporter,
        PipelineEvent,
        create_analytics_pipeline,
        generate_grafana_dashboard,
    )
except ImportError:
    pass

# OAuth Manager
try:
    from .oauth_manager import (
        FacebookOAuthProvider,
        InstagramOAuthProvider,
        LinkedInOAuthProvider,
        OAuthManager,
        OAuthToken,
        PinterestOAuthProvider,
        SnapchatOAuthProvider,
        TikTokOAuthProvider,
        TwitterOAuthProvider,
        YouTubeOAuthProvider,
        create_oauth_manager,
    )
except ImportError:
    pass

__all__ = [
    # Version
    "__version__",
    # Core modules
    "ContentAnalyzer",
    "VideoScriptGenerator",
    "Settings",
    "get_settings",
    "get_api_key",
    "DatabaseClient",
    "EmbeddingGenerator",
    # "NewsProcessor",  # Commented to avoid import issues
    # "main",  # Commented to avoid import issues
    # Predictive Engine
    "PredictiveContentEngine",
    "TrendForecaster",
    "TrendSurfingEngine",
    "ViralityModel",
    "AudienceMatcher",
    "ContentPrediction",
    "TrendOpportunity",
    # Media Manager Integration
    "MediaManagerIntegration",
    "MediaManagerClient",
    "IntelligentAssetRecommender",
    "MediaAsset",
    "AssetType",
    "AIAssetAnalysis",
    "RecommendedAsset",
    # Video Factory
    "VideoFactory",
    "AdvancedVideoScriptGenerator",
    "ElevenLabsClient",
    "DIDClient",
    "LiveVideoGenerator",
    "VideoAsset",
    "VideoScript",
    "VideoStyle",
    "VideoAspectRatio",
    # Publishing Orchestrator
    "PublishingOrchestrator",
    "ScheduledPost",
    "PublishResult",
    "Platform",
    "PublishStatus",
    "HashtagOptimizer",
    "TimingOptimizer",
    "CrossPlatformAnalytics",
    # Platform Publishers
    "InstagramPublisher",
    "FacebookPublisher",
    "SnapchatPublisher",
    "PinterestPublisher",
    "ThreadsPublisher",
    "MultiPlatformPublisher",
    # AI Agents
    "AgentOrchestrator",
    "ContentCuratorAgent",
    "VideoProducerAgent",
    "DistributorAgent",
    "AnalystAgent",
    "EngagementAgent",
    "AgentMessageBus",
    "create_agent_system",
    # Trend Sources
    "TrendAggregator",
    "GoogleTrendsSource",
    "TwitterTrendsSource",
    "RedditTrendsSource",
    "YouTubeTrendsSource",
    "NewsAPISource",
    "TikTokTrendsSource",
    "create_trend_aggregator",
    # Analytics Pipeline
    "AnalyticsPipeline",
    "EventProducer",
    "EventConsumer",
    "MetricsExporter",
    "AnalyticsProcessor",
    "EventType",
    "PipelineEvent",
    "create_analytics_pipeline",
    "generate_grafana_dashboard",
    # OAuth Manager
    "OAuthManager",
    "OAuthToken",
    "YouTubeOAuthProvider",
    "TikTokOAuthProvider",
    "LinkedInOAuthProvider",
    "InstagramOAuthProvider",
    "TwitterOAuthProvider",
    "FacebookOAuthProvider",
    "PinterestOAuthProvider",
    "SnapchatOAuthProvider",
    "create_oauth_manager",
]
