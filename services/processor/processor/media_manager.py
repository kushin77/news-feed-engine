"""
ElevatedIQ News Feed Engine - Media Manager Integration
Unified media asset management with AI-powered recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

logger = structlog.get_logger(__name__)


class AssetType(Enum):
    """Types of media assets"""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    TEMPLATE = "template"


class UsageRightsType(Enum):
    """Types of usage rights"""

    OWNED = "owned"
    LICENSED = "licensed"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RESTRICTED = "restricted"


@dataclass
class AssetURLs:
    """URLs for different versions of an asset"""

    original: str
    cdn: str
    thumbnails: Dict[str, str] = field(default_factory=dict)
    optimized: Dict[str, str] = field(default_factory=dict)
    transcoded: Dict[str, str] = field(default_factory=dict)


@dataclass
class AIAssetAnalysis:
    """AI-generated analysis of a media asset"""

    objects: List[Dict[str, Any]] = field(default_factory=list)
    scenes: List[str] = field(default_factory=list)
    colors: Dict[str, Any] = field(default_factory=dict)
    text: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)
    brand_safety_score: float = 1.0
    content_rating: str = "G"
    auto_tags: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None


@dataclass
class UsageRights:
    """Usage rights information for an asset"""

    type: UsageRightsType = UsageRightsType.OWNED
    license_name: Optional[str] = None
    attribution_required: bool = False
    attribution_text: Optional[str] = None
    expires_at: Optional[datetime] = None
    allowed_platforms: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)


@dataclass
class AssetPerformance:
    """Performance metrics for an asset"""

    usage_count: int = 0
    avg_engagement_rate: float = 0.0
    best_performing_platform: Optional[str] = None
    last_used: Optional[datetime] = None


@dataclass
class MediaAsset:
    """Unified media asset representation"""

    id: str
    tenant_id: str
    type: AssetType
    source_platform: str
    urls: AssetURLs
    filename: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # For video/audio
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    ai_analysis: Optional[AIAssetAnalysis] = None
    usage_rights: Optional[UsageRights] = None
    performance: Optional[AssetPerformance] = None
    custom_tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendedAsset:
    """Asset with recommendation context"""

    asset: MediaAsset
    relevance_score: float
    usage_suggestion: str
    placement_recommendation: str


class MediaManagerClient:
    """
    Client for Media Manager API integration
    """

    def __init__(self, base_url: str, api_key: str, tenant_id: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.tenant_id = tenant_id
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Tenant-ID": self.tenant_id,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def get_asset(self, asset_id: str) -> Optional[MediaAsset]:
        """Get a single asset by ID"""
        try:
            response = await self._client.get(f"/api/v1/assets/{asset_id}")
            response.raise_for_status()
            return self._parse_asset(response.json())
        except Exception as e:
            logger.error("Failed to get asset", asset_id=asset_id, error=str(e))
            return None

    async def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[MediaAsset], int]:
        """List assets with filtering"""
        params = {"limit": limit, "offset": offset}
        if asset_type:
            params["type"] = asset_type.value
        if tags:
            params["tags"] = ",".join(tags)

        try:
            response = await self._client.get("/api/v1/assets", params=params)
            response.raise_for_status()
            data = response.json()
            assets = [self._parse_asset(a) for a in data.get("items", [])]
            total = data.get("total", len(assets))
            return assets, total
        except Exception as e:
            logger.error("Failed to list assets", error=str(e))
            return [], 0

    async def semantic_search(
        self,
        query: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        asset_type: Optional[AssetType] = None,
        limit: int = 20,
    ) -> List[MediaAsset]:
        """
        Semantic search for assets using natural language or embeddings
        """
        payload = {"limit": limit}
        if query:
            payload["query"] = query
        if embedding:
            payload["embedding"] = embedding
        if asset_type:
            payload["type"] = asset_type.value

        try:
            response = await self._client.post(
                "/api/v1/assets/search/semantic", json=payload
            )
            response.raise_for_status()
            data = response.json()
            return [self._parse_asset(a) for a in data.get("items", [])]
        except Exception as e:
            logger.error("Semantic search failed", error=str(e))
            return []

    async def upload_asset(
        self,
        file_data: bytes,
        filename: str,
        asset_type: AssetType,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[MediaAsset]:
        """Upload a new asset"""
        try:
            files = {"file": (filename, file_data)}
            data = {"type": asset_type.value}
            if tags:
                data["tags"] = ",".join(tags)
            if metadata:
                data["metadata"] = str(metadata)

            response = await self._client.post(
                "/api/v1/assets/upload", files=files, data=data
            )
            response.raise_for_status()
            return self._parse_asset(response.json())
        except Exception as e:
            logger.error("Asset upload failed", filename=filename, error=str(e))
            return None

    async def analyze_asset(self, asset_id: str) -> Optional[AIAssetAnalysis]:
        """Trigger AI analysis for an asset"""
        try:
            response = await self._client.post(f"/api/v1/assets/{asset_id}/analyze")
            response.raise_for_status()
            data = response.json()
            return AIAssetAnalysis(
                objects=data.get("objects", []),
                scenes=data.get("scenes", []),
                colors=data.get("colors", {}),
                text=data.get("text", []),
                faces=data.get("faces", []),
                brand_safety_score=data.get("brand_safety_score", 1.0),
                content_rating=data.get("content_rating", "G"),
                auto_tags=data.get("auto_tags", []),
                embeddings=data.get("embeddings"),
            )
        except Exception as e:
            logger.error("Asset analysis failed", asset_id=asset_id, error=str(e))
            return None

    def _parse_asset(self, data: Dict[str, Any]) -> MediaAsset:
        """Parse API response into MediaAsset"""
        urls_data = data.get("urls", {})
        urls = AssetURLs(
            original=urls_data.get("original", ""),
            cdn=urls_data.get("cdn", ""),
            thumbnails=urls_data.get("thumbnails", {}),
            optimized=urls_data.get("optimized", {}),
            transcoded=urls_data.get("transcoded", {}),
        )

        ai_data = data.get("ai_analysis")
        ai_analysis = None
        if ai_data:
            ai_analysis = AIAssetAnalysis(
                objects=ai_data.get("objects", []),
                scenes=ai_data.get("scenes", []),
                colors=ai_data.get("colors", {}),
                text=ai_data.get("text", []),
                faces=ai_data.get("faces", []),
                brand_safety_score=ai_data.get("brand_safety_score", 1.0),
                content_rating=ai_data.get("content_rating", "G"),
                auto_tags=ai_data.get("auto_tags", []),
                embeddings=ai_data.get("embeddings"),
            )

        return MediaAsset(
            id=data.get("id", ""),
            tenant_id=data.get("tenant_id", ""),
            type=AssetType(data.get("type", "image")),
            source_platform=data.get("source_platform", "upload"),
            urls=urls,
            filename=data.get("filename", ""),
            file_size=data.get("file_size", 0),
            mime_type=data.get("mime_type", ""),
            width=data.get("width"),
            height=data.get("height"),
            duration=data.get("duration"),
            ai_analysis=ai_analysis,
            custom_tags=data.get("custom_tags", []),
            metadata=data.get("metadata", {}),
        )


class IntelligentAssetRecommender:
    """
    AI-powered asset recommendation for content creation
    """

    USAGE_CATEGORIES = {
        "thumbnail": ["high_contrast", "face_present", "text_overlay"],
        "b_roll": ["action", "scene", "ambient"],
        "intro": ["branded", "dynamic", "attention_grabbing"],
        "outro": ["cta", "branded", "end_screen"],
        "background": ["subtle", "complementary", "non_distracting"],
    }

    def __init__(self, media_client: MediaManagerClient):
        self.client = media_client
        self.embedding_cache: Dict[str, List[float]] = {}

    async def recommend_assets(
        self,
        content_text: str,
        content_category: str,
        asset_type: Optional[AssetType] = None,
        usage_purpose: Optional[str] = None,
        limit: int = 20,
    ) -> List[RecommendedAsset]:
        """
        Smart asset recommendations based on content context
        """
        logger.info(
            "Generating asset recommendations",
            category=content_category,
            purpose=usage_purpose,
        )

        # Semantic search for matching assets
        candidates = await self.client.semantic_search(
            query=content_text, asset_type=asset_type, limit=limit * 3
        )

        if not candidates:
            logger.warning("No candidates found for recommendation")
            return []

        # Score and rank candidates
        scored_assets = []
        for asset in candidates:
            score = self._calculate_recommendation_score(
                content_text=content_text,
                content_category=content_category,
                asset=asset,
                usage_purpose=usage_purpose,
            )
            scored_assets.append((asset, score))

        # Sort by score
        scored_assets.sort(key=lambda x: x[1], reverse=True)

        # Build recommendations
        recommendations = []
        for asset, score in scored_assets[:limit]:
            recommendation = RecommendedAsset(
                asset=asset,
                relevance_score=score,
                usage_suggestion=self._generate_usage_suggestion(asset, usage_purpose),
                placement_recommendation=self._suggest_placement(
                    asset, content_category
                ),
            )
            recommendations.append(recommendation)

        logger.info(
            "Recommendations generated",
            count=len(recommendations),
            top_score=recommendations[0].relevance_score if recommendations else 0,
        )

        return recommendations

    def _calculate_recommendation_score(
        self,
        content_text: str,
        content_category: str,
        asset: MediaAsset,
        usage_purpose: Optional[str],
    ) -> float:
        """
        Multi-factor scoring algorithm for asset relevance
        """
        weights = {
            "semantic_similarity": 0.30,
            "category_match": 0.20,
            "brand_safety": 0.15,
            "quality": 0.15,
            "freshness": 0.10,
            "performance": 0.10,
        }

        scores = {}

        # Semantic similarity (placeholder - use actual embedding comparison)
        scores["semantic_similarity"] = self._semantic_similarity_score(
            content_text, asset
        )

        # Category match
        scores["category_match"] = self._category_match_score(content_category, asset)

        # Brand safety
        if asset.ai_analysis:
            scores["brand_safety"] = asset.ai_analysis.brand_safety_score
        else:
            scores["brand_safety"] = 0.8

        # Quality score (based on resolution, duration, etc.)
        scores["quality"] = self._quality_score(asset)

        # Freshness
        scores["freshness"] = self._freshness_score(asset)

        # Performance history
        scores["performance"] = self._performance_score(asset)

        # Calculate weighted sum
        total_score = sum(
            scores.get(factor, 0.5) * weight for factor, weight in weights.items()
        )

        return min(max(total_score, 0.0), 1.0)

    def _semantic_similarity_score(self, content_text: str, asset: MediaAsset) -> float:
        """Calculate semantic similarity between content and asset"""
        # Placeholder - in production, compare embeddings
        if asset.ai_analysis and asset.ai_analysis.auto_tags:
            content_words = set(content_text.lower().split())
            tag_words = set(tag.lower() for tag in asset.ai_analysis.auto_tags)
            overlap = len(content_words & tag_words)
            return min(overlap / 10, 1.0)
        return 0.5

    def _category_match_score(self, content_category: str, asset: MediaAsset) -> float:
        """Score how well asset matches content category"""
        if asset.ai_analysis and asset.ai_analysis.auto_tags:
            category_keywords = {
                "technology": ["tech", "computer", "digital", "code"],
                "business": ["office", "meeting", "professional"],
                "entertainment": ["fun", "entertainment", "show"],
                "news": ["news", "report", "breaking"],
            }

            keywords = category_keywords.get(content_category.lower(), [])
            tags = [t.lower() for t in asset.ai_analysis.auto_tags]

            if any(kw in tags for kw in keywords):
                return 0.9
        return 0.5

    def _quality_score(self, asset: MediaAsset) -> float:
        """Score asset quality based on technical attributes"""
        score = 0.5

        if asset.type == AssetType.IMAGE:
            if asset.width and asset.height:
                # Prefer higher resolution
                resolution = asset.width * asset.height
                if resolution >= 2073600:  # 1080p
                    score = 0.9
                elif resolution >= 921600:  # 720p
                    score = 0.7

        elif asset.type == AssetType.VIDEO:
            if asset.width and asset.height:
                if asset.width >= 1920:
                    score = 0.9
                elif asset.width >= 1280:
                    score = 0.7

        return score

    def _freshness_score(self, asset: MediaAsset) -> float:
        """Score based on how recently the asset was created"""
        if not asset.created_at:
            return 0.5

        days_old = (datetime.now() - asset.created_at).days

        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        elif days_old <= 365:
            return 0.4

        return 0.3

    def _performance_score(self, asset: MediaAsset) -> float:
        """Score based on historical performance"""
        if asset.performance:
            # Normalize engagement rate
            engagement = asset.performance.avg_engagement_rate
            return min(engagement * 10, 1.0)
        return 0.5

    def _generate_usage_suggestion(
        self, asset: MediaAsset, usage_purpose: Optional[str]
    ) -> str:
        """Generate usage suggestion for asset"""
        if asset.type == AssetType.IMAGE:
            return "Use as thumbnail or B-roll still image"
        elif asset.type == AssetType.VIDEO:
            if asset.duration and asset.duration < 10:
                return "Ideal for intro/outro or transition clip"
            return "Use as B-roll footage or main content segment"
        elif asset.type == AssetType.AUDIO:
            return "Use as background music or sound effect"

        return "General purpose asset"

    def _suggest_placement(self, asset: MediaAsset, content_category: str) -> str:
        """Suggest where to place the asset in content"""
        if asset.type == AssetType.IMAGE:
            return "thumbnail, social_preview, article_header"
        elif asset.type == AssetType.VIDEO:
            return "intro_sequence, b_roll_cut, visual_break"
        elif asset.type == AssetType.AUDIO:
            return "background_music, transition_sound, intro_music"

        return "general"


class CDNManager:
    """
    Manages CDN uploads and optimizations
    """

    OPTIMIZATION_CONFIGS = {
        "thumbnail": {
            "formats": ["webp", "avif", "jpg"],
            "sizes": [(320, 180), (480, 270), (640, 360), (1280, 720)],
        },
        "video": {
            "resolutions": ["360p", "480p", "720p", "1080p"],
            "formats": ["mp4", "webm"],
            "codecs": ["h264", "vp9"],
        },
        "image": {
            "formats": ["webp", "avif", "jpg", "png"],
            "sizes": [(400, 400), (800, 800), (1200, 1200), (2000, 2000)],
        },
    }

    def __init__(self, cdn_base_url: str, cdn_api_key: str):
        self.cdn_base_url = cdn_base_url
        self.cdn_api_key = cdn_api_key

    async def upload_with_optimizations(
        self, asset_data: bytes, filename: str, asset_type: AssetType
    ) -> AssetURLs:
        """
        Upload asset and generate optimized variants
        """
        # Placeholder - implement actual CDN upload
        base_path = f"assets/{asset_type.value}/{filename}"

        return AssetURLs(
            original=f"{self.cdn_base_url}/{base_path}",
            cdn=f"{self.cdn_base_url}/cdn/{base_path}",
            thumbnails={
                "small": f"{self.cdn_base_url}/thumb/small/{base_path}",
                "medium": f"{self.cdn_base_url}/thumb/medium/{base_path}",
                "large": f"{self.cdn_base_url}/thumb/large/{base_path}",
            },
            optimized={
                "webp": f"{self.cdn_base_url}/opt/webp/{base_path}",
                "avif": f"{self.cdn_base_url}/opt/avif/{base_path}",
            },
            transcoded={},
        )


class MediaManagerIntegration:
    """
    Main integration class for Media Manager
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        tenant_id: str,
        cdn_base_url: str,
        cdn_api_key: str,
    ):
        self.client = MediaManagerClient(base_url, api_key, tenant_id)
        self.recommender = IntelligentAssetRecommender(self.client)
        self.cdn_manager = CDNManager(cdn_base_url, cdn_api_key)
        logger.info("MediaManagerIntegration initialized")

    async def sync_asset(
        self,
        file_data: bytes,
        filename: str,
        asset_type: AssetType,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[MediaAsset]:
        """
        Full sync workflow: upload, optimize, analyze, store
        """
        logger.info("Starting asset sync", filename=filename, type=asset_type.value)

        async with self.client:
            # 1. Upload to CDN with optimizations
            _cdn_urls = await self.cdn_manager.upload_with_optimizations(
                file_data, filename, asset_type
            )  # CDN URLs stored in CDN, returned for reference

            # 2. Upload to Media Manager
            asset = await self.client.upload_asset(
                file_data, filename, asset_type, tags, metadata
            )

            if not asset:
                logger.error("Asset upload failed", filename=filename)
                return None

            # 3. Run AI analysis
            analysis = await self.client.analyze_asset(asset.id)
            if analysis:
                asset.ai_analysis = analysis

            logger.info("Asset sync complete", asset_id=asset.id, filename=filename)

            return asset

    async def get_recommendations(
        self,
        content_text: str,
        content_category: str,
        asset_type: Optional[AssetType] = None,
        limit: int = 10,
    ) -> List[RecommendedAsset]:
        """
        Get asset recommendations for content
        """
        async with self.client:
            return await self.recommender.recommend_assets(
                content_text=content_text,
                content_category=content_category,
                asset_type=asset_type,
                limit=limit,
            )

    async def semantic_search(
        self, query: str, asset_type: Optional[AssetType] = None, limit: int = 20
    ) -> List[MediaAsset]:
        """
        Semantic search for assets
        """
        async with self.client:
            return await self.client.semantic_search(
                query=query, asset_type=asset_type, limit=limit
            )
