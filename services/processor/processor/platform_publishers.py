"""
Extended Platform Publishers for News Feed Engine

Implements publishers for:
- Instagram (Graph API)
- Facebook (Graph API)
- Snapchat (Marketing API)
- Pinterest (API)
- Threads (via Instagram)

Author: ElevatedIQ AI Team
Version: 1.0.0
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

from .config import get_api_key, get_settings, utc_now

logger = logging.getLogger(__name__)


# =============================================================================
# Base Classes
# =============================================================================


class PublishStatus(Enum):
    """Publishing status enum."""

    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class PublishResult:
    """Result of a publishing operation."""

    success: bool
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    published_at: Optional[datetime] = None


@dataclass
class VideoMetadata:
    """Video metadata for publishing."""

    title: str
    description: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    privacy: str = "public"
    scheduled_at: Optional[datetime] = None


class BasePlatformPublisher(ABC):
    """Base class for all platform publishers."""

    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300)
            )
        return self._session

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    @abstractmethod
    async def publish(self, metadata: VideoMetadata) -> PublishResult:
        """Publish content to the platform."""
        pass

    @abstractmethod
    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get metrics for a published post."""
        pass

    async def validate_credentials(self) -> bool:
        """Validate platform credentials."""
        return True

    def format_caption(self, metadata: VideoMetadata, max_length: int = 2200) -> str:
        """Format caption with hashtags and mentions."""
        caption = f"{metadata.title}\n\n{metadata.description}"

        if metadata.hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in metadata.hashtags)
            if len(caption) + len(hashtag_str) + 2 <= max_length:
                caption += f"\n\n{hashtag_str}"

        if metadata.mentions:
            mention_str = " ".join(f"@{m}" for m in metadata.mentions)
            if len(caption) + len(mention_str) + 2 <= max_length:
                caption += f"\n\n{mention_str}"

        return caption[:max_length]


# =============================================================================
# Instagram Publisher
# =============================================================================


class InstagramPublisher(BasePlatformPublisher):
    """Instagram publisher using Graph API."""

    def __init__(self):
        super().__init__("instagram")
        self.base_url = "https://graph.facebook.com/v18.0"

    async def publish(self, metadata: VideoMetadata) -> PublishResult:
        """Publish video to Instagram Reels."""
        try:
            access_token = (
                get_api_key("instagram") or self.settings.instagram_access_token
            )
            if not access_token:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Instagram access token not configured",
                )

            session = await self.get_session()

            # Step 1: Create media container
            container_id = await self._create_media_container(
                session, access_token, metadata
            )

            if not container_id:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Failed to create media container",
                )

            # Step 2: Wait for media to be ready
            if not await self._wait_for_media_ready(
                session, access_token, container_id
            ):
                return PublishResult(
                    success=False, platform=self.name, error="Media processing timeout"
                )

            # Step 3: Publish the media
            result = await self._publish_media(session, access_token, container_id)

            if result:
                return PublishResult(
                    success=True,
                    platform=self.name,
                    post_id=result.get("id"),
                    post_url=f"https://www.instagram.com/reel/{result.get('id')}/",
                    published_at=utc_now(),
                )

            return PublishResult(
                success=False, platform=self.name, error="Failed to publish media"
            )

        except Exception as e:
            logger.error(f"Instagram publish error: {e}")
            return PublishResult(success=False, platform=self.name, error=str(e))

    async def _create_media_container(
        self, session: aiohttp.ClientSession, access_token: str, metadata: VideoMetadata
    ) -> Optional[str]:
        """Create Instagram media container for Reels."""
        ig_user_id = await self._get_instagram_user_id(session, access_token)
        if not ig_user_id:
            return None

        caption = self.format_caption(metadata, max_length=2200)

        payload = {
            "media_type": "REELS",
            "video_url": metadata.video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": access_token,
        }

        if metadata.thumbnail_url:
            payload["thumb_offset"] = 0  # Use first frame

        if metadata.location:
            payload["location_id"] = metadata.location.get("id")

        async with session.post(
            f"{self.base_url}/{ig_user_id}/media", data=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("id")
            else:
                error = await response.text()
                logger.error(f"Instagram container creation failed: {error}")
                return None

    async def _wait_for_media_ready(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        container_id: str,
        timeout: int = 300,
        poll_interval: int = 10,
    ) -> bool:
        """Wait for media container to be ready."""
        start_time = utc_now()

        while (utc_now() - start_time).total_seconds() < timeout:
            async with session.get(
                f"{self.base_url}/{container_id}",
                params={"fields": "status_code", "access_token": access_token},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status_code")

                    if status == "FINISHED":
                        return True
                    elif status == "ERROR":
                        logger.error("Instagram media processing failed")
                        return False

            await asyncio.sleep(poll_interval)

        return False

    async def _publish_media(
        self, session: aiohttp.ClientSession, access_token: str, container_id: str
    ) -> Optional[Dict[str, Any]]:
        """Publish the media container."""
        ig_user_id = await self._get_instagram_user_id(session, access_token)
        if not ig_user_id:
            return None

        async with session.post(
            f"{self.base_url}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": access_token},
        ) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def _get_instagram_user_id(
        self, session: aiohttp.ClientSession, access_token: str
    ) -> Optional[str]:
        """Get Instagram Business Account ID."""
        async with session.get(
            f"{self.base_url}/me/accounts", params={"access_token": access_token}
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("data"):
                    page = data["data"][0]
                    # Get Instagram account connected to the page
                    async with session.get(
                        f"{self.base_url}/{page['id']}",
                        params={
                            "fields": "instagram_business_account",
                            "access_token": access_token,
                        },
                    ) as ig_response:
                        if ig_response.status == 200:
                            ig_data = await ig_response.json()
                            return ig_data.get("instagram_business_account", {}).get(
                                "id"
                            )
        return None

    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram post metrics."""
        access_token = get_api_key("instagram") or self.settings.instagram_access_token
        if not access_token:
            return {}

        session = await self.get_session()

        async with session.get(
            f"{self.base_url}/{post_id}/insights",
            params={
                "metric": "engagement,impressions,reach,saved,video_views",
                "access_token": access_token,
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    m["name"]: m["values"][0]["value"] for m in data.get("data", [])
                }
        return {}


# =============================================================================
# Facebook Publisher
# =============================================================================


class FacebookPublisher(BasePlatformPublisher):
    """Facebook publisher using Graph API."""

    def __init__(self):
        super().__init__("facebook")
        self.base_url = "https://graph.facebook.com/v18.0"

    async def publish(self, metadata: VideoMetadata) -> PublishResult:
        """Publish video to Facebook page."""
        try:
            access_token = (
                get_api_key("facebook") or self.settings.facebook_access_token
            )
            if not access_token:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Facebook access token not configured",
                )

            session = await self.get_session()
            page_id = await self._get_page_id(session, access_token)

            if not page_id:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Could not get Facebook page ID",
                )

            caption = self.format_caption(metadata, max_length=63206)

            # Upload video
            payload = {
                "file_url": metadata.video_url,
                "title": metadata.title,
                "description": caption,
                "access_token": access_token,
            }

            if metadata.thumbnail_url:
                payload["thumb"] = metadata.thumbnail_url

            if metadata.scheduled_at:
                payload["scheduled_publish_time"] = int(
                    metadata.scheduled_at.timestamp()
                )
                payload["published"] = False

            async with session.post(
                f"{self.base_url}/{page_id}/videos", data=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    video_id = data.get("id")

                    return PublishResult(
                        success=True,
                        platform=self.name,
                        post_id=video_id,
                        post_url=f"https://www.facebook.com/{page_id}/videos/{video_id}",
                        published_at=utc_now(),
                    )
                else:
                    error = await response.text()
                    return PublishResult(
                        success=False,
                        platform=self.name,
                        error=f"Facebook upload failed: {error}",
                    )

        except Exception as e:
            logger.error(f"Facebook publish error: {e}")
            return PublishResult(success=False, platform=self.name, error=str(e))

    async def _get_page_id(
        self, session: aiohttp.ClientSession, access_token: str
    ) -> Optional[str]:
        """Get Facebook page ID."""
        async with session.get(
            f"{self.base_url}/me/accounts", params={"access_token": access_token}
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("data"):
                    return data["data"][0]["id"]
        return None

    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook video metrics."""
        access_token = get_api_key("facebook") or self.settings.facebook_access_token
        if not access_token:
            return {}

        session = await self.get_session()

        async with session.get(
            f"{self.base_url}/{post_id}/insights",
            params={
                "metric": "post_video_views,post_video_avg_time_watched,post_video_complete_views,post_engaged_users,post_reactions_by_type_total",
                "access_token": access_token,
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    m["name"]: m["values"][0]["value"] for m in data.get("data", [])
                }
        return {}


# =============================================================================
# Snapchat Publisher
# =============================================================================


class SnapchatPublisher(BasePlatformPublisher):
    """Snapchat publisher using Marketing API."""

    def __init__(self):
        super().__init__("snapchat")
        self.base_url = "https://adsapi.snapchat.com/v1"

    async def publish(self, metadata: VideoMetadata) -> PublishResult:
        """Publish to Snapchat Spotlight."""
        try:
            access_token = get_api_key("snapchat")
            if not access_token:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Snapchat access token not configured",
                )

            session = await self.get_session()

            # Snapchat requires uploading media first
            media_id = await self._upload_media(session, access_token, metadata)

            if not media_id:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Failed to upload media to Snapchat",
                )

            # Create Spotlight submission
            result = await self._create_spotlight_submission(
                session, access_token, media_id, metadata
            )

            if result:
                return PublishResult(
                    success=True,
                    platform=self.name,
                    post_id=result.get("id"),
                    published_at=utc_now(),
                )

            return PublishResult(
                success=False,
                platform=self.name,
                error="Failed to create Spotlight submission",
            )

        except Exception as e:
            logger.error(f"Snapchat publish error: {e}")
            return PublishResult(success=False, platform=self.name, error=str(e))

    async def _upload_media(
        self, session: aiohttp.ClientSession, access_token: str, metadata: VideoMetadata
    ) -> Optional[str]:
        """Upload media to Snapchat."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Create media entry
        async with session.post(
            f"{self.base_url}/media",
            headers=headers,
            json={
                "media": [
                    {
                        "name": metadata.title,
                        "type": "VIDEO",
                        "ad_account_id": self.settings.snapchat_client_id,
                    }
                ]
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("media", [{}])[0].get("id")
        return None

    async def _create_spotlight_submission(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        media_id: str,
        metadata: VideoMetadata,
    ) -> Optional[Dict[str, Any]]:
        """Create Snapchat Spotlight submission."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        caption = self.format_caption(metadata, max_length=250)

        async with session.post(
            f"{self.base_url}/spotlight/submit",
            headers=headers,
            json={
                "media_id": media_id,
                "caption": caption,
                "topics": metadata.hashtags[:5],  # Max 5 topics
            },
        ) as response:
            if response.status == 200:
                return await response.json()
        return None

    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Snapchat metrics (limited availability)."""
        # Snapchat metrics are limited for Spotlight
        return {}


# =============================================================================
# Pinterest Publisher
# =============================================================================


class PinterestPublisher(BasePlatformPublisher):
    """Pinterest publisher using API v5."""

    def __init__(self):
        super().__init__("pinterest")
        self.base_url = "https://api.pinterest.com/v5"

    async def publish(self, metadata: VideoMetadata) -> PublishResult:
        """Publish video pin to Pinterest."""
        try:
            access_token = get_api_key("pinterest")
            if not access_token:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Pinterest access token not configured",
                )

            session = await self.get_session()

            # Get default board
            board_id = await self._get_board_id(session, access_token)
            if not board_id:
                return PublishResult(
                    success=False, platform=self.name, error="No Pinterest board found"
                )

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            description = self.format_caption(metadata, max_length=500)

            # Create video pin
            async with session.post(
                f"{self.base_url}/pins",
                headers=headers,
                json={
                    "board_id": board_id,
                    "title": metadata.title[:100],
                    "description": description,
                    "media_source": {
                        "source_type": "video_id",
                        "video_id": await self._upload_video(
                            session, access_token, metadata
                        ),
                    },
                    "alt_text": metadata.description[:500],
                },
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    pin_id = data.get("id")

                    return PublishResult(
                        success=True,
                        platform=self.name,
                        post_id=pin_id,
                        post_url=f"https://www.pinterest.com/pin/{pin_id}/",
                        published_at=utc_now(),
                    )
                else:
                    error = await response.text()
                    return PublishResult(
                        success=False,
                        platform=self.name,
                        error=f"Pinterest publish failed: {error}",
                    )

        except Exception as e:
            logger.error(f"Pinterest publish error: {e}")
            return PublishResult(success=False, platform=self.name, error=str(e))

    async def _get_board_id(
        self, session: aiohttp.ClientSession, access_token: str
    ) -> Optional[str]:
        """Get Pinterest board ID."""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with session.get(f"{self.base_url}/boards", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                items = data.get("items", [])
                if items:
                    return items[0]["id"]
        return None

    async def _upload_video(
        self, session: aiohttp.ClientSession, access_token: str, metadata: VideoMetadata
    ) -> Optional[str]:
        """Upload video to Pinterest media library."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Register video upload
        async with session.post(
            f"{self.base_url}/media",
            headers=headers,
            json={"media_type": "video", "title": metadata.title},
        ) as response:
            if response.status == 200:
                data = await response.json()
                media_id = data.get("media_id")

                # Upload to the provided URL
                upload_url = data.get("upload_url")
                if upload_url:
                    async with session.post(
                        upload_url, data={"video_url": metadata.video_url}
                    ) as upload_response:
                        if upload_response.status == 200:
                            return media_id
        return None

    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Pinterest pin metrics."""
        access_token = get_api_key("pinterest")
        if not access_token:
            return {}

        session = await self.get_session()
        headers = {"Authorization": f"Bearer {access_token}"}

        async with session.get(
            f"{self.base_url}/pins/{post_id}/analytics",
            headers=headers,
            params={
                "metric_types": "IMPRESSION,SAVE,PIN_CLICK,OUTBOUND_CLICK,VIDEO_START,VIDEO_10S_VIEW"
            },
        ) as response:
            if response.status == 200:
                return await response.json()
        return {}


# =============================================================================
# Threads Publisher
# =============================================================================


class ThreadsPublisher(BasePlatformPublisher):
    """Threads publisher (via Instagram API)."""

    def __init__(self):
        super().__init__("threads")
        self.base_url = "https://graph.threads.net/v1.0"

    async def publish(self, metadata: VideoMetadata) -> PublishResult:
        """Publish to Threads."""
        try:
            access_token = get_api_key("threads") or self.settings.threads_access_token
            if not access_token:
                # Fallback to Instagram token
                access_token = (
                    get_api_key("instagram") or self.settings.instagram_access_token
                )

            if not access_token:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Threads/Instagram access token not configured",
                )

            session = await self.get_session()

            # Get Threads user ID
            user_id = await self._get_threads_user_id(session, access_token)
            if not user_id:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Could not get Threads user ID",
                )

            # Create media container
            container_id = await self._create_container(
                session, access_token, user_id, metadata
            )

            if not container_id:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    error="Failed to create Threads container",
                )

            # Publish the container
            result = await self._publish_container(
                session, access_token, user_id, container_id
            )

            if result:
                return PublishResult(
                    success=True,
                    platform=self.name,
                    post_id=result.get("id"),
                    post_url=f"https://www.threads.net/t/{result.get('id')}",
                    published_at=utc_now(),
                )

            return PublishResult(
                success=False, platform=self.name, error="Failed to publish to Threads"
            )

        except Exception as e:
            logger.error(f"Threads publish error: {e}")
            return PublishResult(success=False, platform=self.name, error=str(e))

    async def _get_threads_user_id(
        self, session: aiohttp.ClientSession, access_token: str
    ) -> Optional[str]:
        """Get Threads user ID."""
        async with session.get(
            f"{self.base_url}/me", params={"access_token": access_token}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("id")
        return None

    async def _create_container(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        user_id: str,
        metadata: VideoMetadata,
    ) -> Optional[str]:
        """Create Threads media container."""
        caption = self.format_caption(metadata, max_length=500)

        async with session.post(
            f"{self.base_url}/{user_id}/threads",
            data={
                "media_type": "VIDEO",
                "video_url": metadata.video_url,
                "text": caption,
                "access_token": access_token,
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("id")
        return None

    async def _publish_container(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        user_id: str,
        container_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Publish the Threads container."""
        async with session.post(
            f"{self.base_url}/{user_id}/threads_publish",
            data={"creation_id": container_id, "access_token": access_token},
        ) as response:
            if response.status == 200:
                return await response.json()
        return None

    async def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Threads post metrics."""
        access_token = get_api_key("threads") or self.settings.threads_access_token
        if not access_token:
            access_token = (
                get_api_key("instagram") or self.settings.instagram_access_token
            )

        if not access_token:
            return {}

        session = await self.get_session()

        async with session.get(
            f"{self.base_url}/{post_id}/insights",
            params={
                "metric": "views,likes,replies,reposts,quotes",
                "access_token": access_token,
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    m["name"]: m["values"][0]["value"] for m in data.get("data", [])
                }
        return {}


# =============================================================================
# Publisher Factory
# =============================================================================


class PublisherFactory:
    """Factory for creating platform publishers."""

    _publishers: Dict[str, type] = {
        "instagram": InstagramPublisher,
        "facebook": FacebookPublisher,
        "snapchat": SnapchatPublisher,
        "pinterest": PinterestPublisher,
        "threads": ThreadsPublisher,
    }

    @classmethod
    def get_publisher(cls, platform: str) -> Optional[BasePlatformPublisher]:
        """Get a publisher instance for the specified platform."""
        publisher_class = cls._publishers.get(platform.lower())
        if publisher_class:
            return publisher_class()
        return None

    @classmethod
    def get_all_publishers(cls) -> List[BasePlatformPublisher]:
        """Get instances of all available publishers."""
        return [pub() for pub in cls._publishers.values()]

    @classmethod
    def register_publisher(cls, platform: str, publisher_class: type):
        """Register a new publisher class."""
        cls._publishers[platform.lower()] = publisher_class


# =============================================================================
# Multi-Platform Publisher
# =============================================================================


class MultiPlatformPublisher:
    """Publish to multiple platforms simultaneously."""

    def __init__(self):
        self.factory = PublisherFactory()

    async def publish_to_all(
        self, metadata: VideoMetadata, platforms: Optional[List[str]] = None
    ) -> Dict[str, PublishResult]:
        """Publish to all specified platforms."""
        if platforms is None:
            platforms = ["instagram", "facebook", "pinterest", "threads"]

        results = {}
        tasks = []

        for platform in platforms:
            publisher = self.factory.get_publisher(platform)
            if publisher:
                tasks.append(self._publish_with_name(publisher, metadata, platform))

        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            for platform, result in zip(platforms, task_results):
                if isinstance(result, Exception):
                    results[platform] = PublishResult(
                        success=False, platform=platform, error=str(result)
                    )
                else:
                    results[platform] = result

        return results

    async def _publish_with_name(
        self, publisher: BasePlatformPublisher, metadata: VideoMetadata, platform: str
    ) -> PublishResult:
        """Publish and return result with platform name."""
        try:
            return await publisher.publish(metadata)
        finally:
            await publisher.close()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Base classes
    "BasePlatformPublisher",
    "PublishStatus",
    "PublishResult",
    "VideoMetadata",
    # Publishers
    "InstagramPublisher",
    "FacebookPublisher",
    "SnapchatPublisher",
    "PinterestPublisher",
    "ThreadsPublisher",
    # Factory and multi-platform
    "PublisherFactory",
    "MultiPlatformPublisher",
]
