"""
ElevatedIQ News Feed Engine - Integration Tests
Tests for Kafka, PostgreSQL, and Redis integration
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any

import pytest


# Skip integration tests if dependencies not available
pytest_plugins: list[str] = []
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION_TESTS", "true").lower() == "true"


@pytest.fixture
def sample_content_message() -> Dict[str, Any]:
    """Sample content message for testing"""
    return {
        "id": "test-content-123",
        "platform": "youtube",
        "title": "AI News: Latest Developments in Machine Learning",
        "description": "A comprehensive overview of recent AI breakthroughs",
        "creator_id": "creator-456",
        "source_url": "https://youtube.com/watch?v=test123",
        "raw_content": {
            "transcript": "Today we discuss the latest AI developments...",
            "duration": 600,
            "view_count": 10000,
        },
        "metadata": {
            "channel_name": "Tech News Daily",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "tags": ["AI", "Machine Learning", "Technology"],
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def processed_content_sample() -> Dict[str, Any]:
    """Sample processed content"""
    return {
        "id": "test-content-123",
        "platform": "youtube",
        "title": "AI News: Latest Developments in Machine Learning",
        "processing_status": "completed",
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "summary": "This video covers recent AI developments...",
        "category": "technology",
        "tags": ["AI", "machine learning", "tech news"],
        "sentiment": 0.7,
        "quality_score": 0.85,
        "geo_classification": "global",
        "ai_analysis": {
            "key_points": [
                "New AI models announced",
                "Performance improvements",
                "Industry applications",
            ],
            "entities": [
                {"name": "OpenAI", "type": "organization"},
                {"name": "GPT-5", "type": "product"},
            ],
            "topics": ["artificial intelligence", "deep learning"],
            "credibility_score": 0.9,
            "bias_assessment": {"detected": False, "type": None, "confidence": 0.0},
        },
        "embedding": [0.1] * 1536,  # OpenAI embedding dimension
    }


@pytest.mark.integration
@pytest.mark.skipif(SKIP_INTEGRATION, reason="Integration tests disabled")
class TestKafkaIntegration:
    """Kafka integration tests"""

    @pytest.mark.asyncio
    async def test_producer_connection(self):
        """Test Kafka producer can connect"""
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        # Should not raise
        producer.close()

    @pytest.mark.asyncio
    async def test_message_roundtrip(self, sample_content_message):
        """Test message can be produced and consumed"""
        from kafka import KafkaProducer, KafkaConsumer

        topic = "test-news-feed-integration"
        bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")

        # Produce message
        producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        future = producer.send(topic, sample_content_message)
        future.get(timeout=10)  # Wait for send to complete
        producer.close()

        # Consume message
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=5000,
        )

        messages = list(consumer)
        consumer.close()

        assert len(messages) > 0
        assert messages[-1].value["id"] == sample_content_message["id"]


@pytest.mark.integration
@pytest.mark.skipif(SKIP_INTEGRATION, reason="Integration tests disabled")
class TestPostgreSQLIntegration:
    """PostgreSQL integration tests"""

    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection"""
        import asyncpg

        dsn = os.getenv(
            "POSTGRES_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/news_feed"
        )

        conn = await asyncpg.connect(dsn)
        version = await conn.fetchval("SELECT version()")
        await conn.close()

        assert "PostgreSQL" in version

    @pytest.mark.asyncio
    async def test_content_crud(self, processed_content_sample):
        """Test content CRUD operations"""
        import asyncpg

        dsn = os.getenv(
            "POSTGRES_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/news_feed"
        )

        conn = await asyncpg.connect(dsn)

        try:
            # Create
            await conn.execute(
                """
                INSERT INTO content (id, platform, title, processing_status)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET
                    processing_status = EXCLUDED.processing_status
                """,
                processed_content_sample["id"],
                processed_content_sample["platform"],
                processed_content_sample["title"],
                processed_content_sample["processing_status"],
            )

            # Read
            row = await conn.fetchrow(
                "SELECT * FROM content WHERE id = $1", processed_content_sample["id"]
            )
            assert row is not None
            assert row["title"] == processed_content_sample["title"]

            # Delete
            await conn.execute(
                "DELETE FROM content WHERE id = $1", processed_content_sample["id"]
            )

        finally:
            await conn.close()


@pytest.mark.integration
@pytest.mark.skipif(SKIP_INTEGRATION, reason="Integration tests disabled")
class TestRedisIntegration:
    """Redis integration tests"""

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection"""
        import redis

        r = redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"))

        # Test ping
        assert r.ping() is True
        r.close()

    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test cache set/get operations"""
        import redis

        r = redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"))

        try:
            # Set
            r.setex("test:news-feed:cache", 60, "test-value")

            # Get
            value = r.get("test:news-feed:cache")
            assert value.decode() == "test-value"

            # Delete
            r.delete("test:news-feed:cache")

        finally:
            r.close()


@pytest.mark.integration
@pytest.mark.skipif(SKIP_INTEGRATION, reason="Integration tests disabled")
class TestAPIIntegration:
    """API integration tests"""

    @pytest.fixture
    def api_base_url(self):
        return os.getenv("API_BASE_URL", "http://127.0.0.1:8080")

    @pytest.mark.asyncio
    async def test_health_endpoint(self, api_base_url):
        """Test health endpoint"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base_url}/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_readiness_endpoint(self, api_base_url):
        """Test readiness endpoint"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base_url}/ready")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_content_endpoint(self, api_base_url):
        """Test list content endpoint"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_base_url}/api/v1/content", headers={"X-Tenant-ID": "test-tenant"}
            )
            assert response.status_code in [200, 401]  # OK or needs auth

    @pytest.mark.asyncio
    async def test_search_endpoint(self, api_base_url):
        """Test search endpoint"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_base_url}/api/v1/content/search",
                params={"q": "AI technology"},
                headers={"X-Tenant-ID": "test-tenant"},
            )
            assert response.status_code in [200, 401]


@pytest.mark.integration
@pytest.mark.skipif(SKIP_INTEGRATION, reason="Integration tests disabled")
class TestFullPipeline:
    """End-to-end pipeline tests"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_content_processing_pipeline(self, sample_content_message):
        """Test full content processing pipeline"""
        # This test requires all services running
        # Skip if not in CI environment with full setup

        if not os.getenv("FULL_INTEGRATION_TEST"):
            pytest.skip("Full integration test not enabled")

        from kafka import KafkaProducer
        import asyncpg

        # 1. Send raw content to input topic
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        producer.send("news-feed-raw-content", sample_content_message)
        producer.flush()
        producer.close()

        # 2. Wait for processing (with timeout)
        max_wait = 30  # seconds
        start_time = time.time()

        conn = await asyncpg.connect(
            os.getenv(
                "POSTGRES_DSN",
                "postgresql://postgres:postgres@127.0.0.1:5432/news_feed",
            )
        )

        processed = None
        while time.time() - start_time < max_wait:
            row = await conn.fetchrow(
                """
                SELECT * FROM content
                WHERE id = $1 AND processing_status = 'completed'
                """,
                sample_content_message["id"],
            )

            if row:
                processed = dict(row)
                break

            await asyncio.sleep(1)

        await conn.close()

        # 3. Verify processing results
        assert processed is not None, "Content was not processed within timeout"
        assert processed["processing_status"] == "completed"
        assert processed.get("summary") is not None
        assert processed.get("category") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
