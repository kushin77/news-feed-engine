"""
ElevatedIQ News Feed Processor - Database Client Module
Handles PostgreSQL database operations for content storage
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

logger = structlog.get_logger(__name__)


class DatabaseClient:
    """Async PostgreSQL client for content operations"""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        """Establish database connection pool"""
        try:
            self.pool = AsyncConnectionPool(
                self.dsn, min_size=2, max_size=10, kwargs={"row_factory": dict_row}
            )
            await self.pool.open()
            logger.info("Database connection pool established")
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))
            raise

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        async with self.pool.connection() as conn:
            yield conn

    async def update_content(self, content_id: str, data: Dict[str, Any]) -> bool:
        """
        Update content with processing results

        Args:
            content_id: UUID of the content to update
            data: Processed content data

        Returns:
            True if update successful
        """
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    # Build embedding vector string for pgvector
                    embedding_str = None
                    if data.get("embedding"):
                        emb_vals = ",".join(str(x) for x in data["embedding"])
                        embedding_str = f"[{emb_vals}]"

                    await cur.execute(
                        """
                        UPDATE content SET
                            processing_status = %(status)s,
                            processed_at = %(processed_at)s,
                            summary = %(summary)s,
                            category = %(category)s,
                            tags = %(tags)s,
                            sentiment = %(sentiment)s,
                            quality_score = %(quality_score)s,
                            geo_classification =
                                %(geo_classification)s::geo_classification,
                            ai_analysis = %(ai_analysis)s,
                            updated_at = NOW()
                        WHERE id = %(id)s
                        """,
                        {
                            "id": content_id,
                            "status": data.get("processing_status", "completed"),
                            "processed_at": data.get(
                                "processed_at", datetime.now(timezone.utc)
                            ),
                            "summary": data.get("summary"),
                            "category": data.get("category"),
                            "tags": data.get("tags", []),
                            "sentiment": data.get("sentiment", 0.0),
                            "quality_score": data.get("quality_score", 0.5),
                            "geo_classification": data.get(
                                "geo_classification", "global"
                            ),
                            "ai_analysis": json.dumps(data.get("ai_analysis", {})),
                        },
                    )

                    await conn.commit()

                    logger.info(
                        "Content updated",
                        content_id=content_id,
                        status=data.get("processing_status"),
                    )

                    return True

        except Exception as e:
            logger.error(
                "Failed to update content", content_id=content_id, error=str(e)
            )
            return False

    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT * FROM content WHERE id = %s
                        """,
                        (content_id,),
                    )
                    return await cur.fetchone()
        except Exception as e:
            logger.error("Failed to get content", content_id=content_id, error=str(e))
            return None

    async def get_pending_content(
        self, tenant_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get content pending processing"""
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT * FROM content
                        WHERE tenant_id = %s
                          AND processing_status = 'pending'
                        ORDER BY created_at ASC
                        LIMIT %s
                        """,
                        (tenant_id, limit),
                    )
                    return await cur.fetchall()
        except Exception as e:
            logger.error("Failed to get pending content", error=str(e))
            return []

    async def insert_content(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Insert new content

        Args:
            data: Content data to insert

        Returns:
            UUID of inserted content, or None on error
        """
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO content (
                            tenant_id, creator_id, platform,
                            platform_content_id, content_type, title,
                            description, original_url, thumbnail_url,
                            category, tags, geo_classification,
                            source_location, published_at,
                            raw_content, metadata
                        ) VALUES (
                            %(tenant_id)s, %(creator_id)s,
                            %(platform)s::platform_type,
                            %(platform_content_id)s,
                            %(content_type)s::content_type,
                            %(title)s, %(description)s, %(original_url)s,
                            %(thumbnail_url)s, %(category)s, %(tags)s,
                            %(geo_classification)s::geo_classification,
                            %(source_location)s, %(published_at)s,
                            %(raw_content)s, %(metadata)s
                        )
                        ON CONFLICT (
                            tenant_id, platform, platform_content_id
                        ) DO UPDATE SET
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            thumbnail_url = EXCLUDED.thumbnail_url,
                            raw_content = EXCLUDED.raw_content,
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                        RETURNING id
                        """,
                        {
                            "tenant_id": data.get("tenant_id", "elevatediq"),
                            "creator_id": data.get("creator_id"),
                            "platform": data.get("platform", "internal"),
                            "platform_content_id": data["platform_content_id"],
                            "content_type": data.get("content_type", "article"),
                            "title": data["title"],
                            "description": data.get("description"),
                            "original_url": data["original_url"],
                            "thumbnail_url": data.get("thumbnail_url"),
                            "category": data.get("category"),
                            "tags": data.get("tags", []),
                            "geo_classification": data.get(
                                "geo_classification", "global"
                            ),
                            "source_location": data.get("source_location"),
                            "published_at": data.get(
                                "published_at", datetime.now(timezone.utc)
                            ),
                            "raw_content": json.dumps(data.get("raw_content", {})),
                            "metadata": json.dumps(data.get("metadata", {})),
                        },
                    )

                    result = await cur.fetchone()
                    await conn.commit()

                    if result:
                        return str(result["id"])
                    return None

        except Exception as e:
            logger.error("Failed to insert content", error=str(e))
            return None

    async def update_video_summary(self, video_id: str, data: Dict[str, Any]) -> bool:
        """Update video summary status and data"""
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        UPDATE video_summaries SET
                            status = %(status)s::processing_status,
                            video_url = %(video_url)s,
                            thumbnail_url = %(thumbnail_url)s,
                            duration = %(duration)s,
                            file_size = %(file_size)s,
                            generated_at = %(generated_at)s,
                            generation_time = %(generation_time)s,
                            error_message = %(error_message)s,
                            metadata = %(metadata)s,
                            updated_at = NOW()
                        WHERE id = %(id)s
                        """,
                        {
                            "id": video_id,
                            "status": data.get("status", "completed"),
                            "video_url": data.get("video_url"),
                            "thumbnail_url": data.get("thumbnail_url"),
                            "duration": data.get("duration", 0),
                            "file_size": data.get("file_size", 0),
                            "generated_at": data.get("generated_at"),
                            "generation_time": data.get("generation_time", 0),
                            "error_message": data.get("error_message"),
                            "metadata": json.dumps(data.get("metadata", {})),
                        },
                    )

                    await conn.commit()
                    return True

        except Exception as e:
            logger.error(
                "Failed to update video summary", video_id=video_id, error=str(e)
            )
            return False

    async def get_tenant_config(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant configuration"""
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT * FROM tenant_configs
                        WHERE tenant_id = %s AND active = true
                        """,
                        (tenant_id,),
                    )
                    return await cur.fetchone()
        except Exception as e:
            logger.error(
                "Failed to get tenant config", tenant_id=tenant_id, error=str(e)
            )
            return None

    async def get_active_sources(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get active content sources for a tenant"""
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT * FROM content_sources
                        WHERE tenant_id = %s AND active = true
                        ORDER BY priority ASC
                        """,
                        (tenant_id,),
                    )
                    return await cur.fetchall()
        except Exception as e:
            logger.error(
                "Failed to get content sources", tenant_id=tenant_id, error=str(e)
            )
            return []
