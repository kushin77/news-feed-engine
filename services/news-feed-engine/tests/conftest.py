"""
Test configuration and fixtures for News Feed Engine tests.
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock

# Set test environment
os.environ["ELEVATEDIQ_ENVIRONMENT"] = "test"
os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for all tests."""
    env_vars = {
        "ELEVATEDIQ_ENVIRONMENT": "test",
        "ANTHROPIC_API_KEY": "sk-ant-test-xxx",
        "OPENAI_API_KEY": "sk-test-xxx",
        "ELEVENLABS_API_KEY": "xi-test-xxx",
        "DID_API_KEY": "did-test-xxx",
        "YOUTUBE_API_KEY": "yt-test-xxx",
        "TWITTER_BEARER_TOKEN": "tw-test-xxx",
        "TIKTOK_CLIENT_KEY": "tt-test-xxx",
        "LINKEDIN_CLIENT_ID": "li-test-xxx",
        "MEDIA_MANAGER_API_KEY": "mm-test-xxx",
        "POSTGRES_HOST": "127.0.0.1",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "news_feed_test",
        "REDIS_URL": "redis://127.0.0.1:6379/15",
        "KAFKA_BOOTSTRAP_SERVERS": "127.0.0.1:9092",
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client."""
    with patch("anthropic.AsyncAnthropic") as mock:
        client = MagicMock()
        client.messages.create = MagicMock()
        mock.return_value = client
        yield mock


@pytest.fixture
def mock_aiohttp():
    """Mock aiohttp for API calls."""
    with patch("aiohttp.ClientSession") as mock:
        yield mock


@pytest.fixture
def mock_database():
    """Mock database connections."""
    with patch("asyncpg.create_pool") as mock_pg:
        with patch("aioredis.from_url") as mock_redis:
            yield {"postgres": mock_pg, "redis": mock_redis}
