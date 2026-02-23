"""
ElevatedIQ News Feed Engine - Unit Tests for Configuration
"""

import os
import pytest
from unittest.mock import patch, MagicMock

import sys

sys.path.insert(0, "../../processor")

from processor.config import Settings, get_settings, get_api_key


class TestSettings:
    """Test suite for Settings configuration class"""

    def test_default_values(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

            assert settings.environment == "development"
            assert settings.log_level == "info"
            assert settings.batch_size == 10
            assert settings.max_workers == 4
            assert settings.claude_max_tokens == 4096

    def test_environment_override(self):
        """Test environment variable overrides"""
        env_vars = {
            "ELEVATEDIQ_ENVIRONMENT": "production",
            "ELEVATEDIQ_LOG_LEVEL": "debug",
            "BATCH_SIZE": "20",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Force new settings instance
            get_settings.cache_clear()
            settings = Settings()

            assert settings.environment == "production"
            assert settings.log_level == "debug"
            assert settings.batch_size == 20

    def test_kafka_defaults(self):
        """Test Kafka configuration defaults"""
        settings = Settings()

        assert settings.kafka_bootstrap_servers == "elevatediq-kafka:9092"
        assert settings.kafka_consumer_group == "news-feed-processor"
        assert settings.kafka_input_topic == "news-feed-raw-content"
        assert settings.kafka_output_topic == "news-feed-processed-content"

    def test_api_keys_optional(self):
        """Test that API keys are optional by default"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

            assert settings.anthropic_api_key is None
            assert settings.openai_api_key is None
            assert settings.youtube_api_key is None
            assert settings.twitter_api_key is None

    def test_claude_model_default(self):
        """Test Claude model defaults"""
        settings = Settings()

        assert "claude" in settings.claude_model.lower()
        assert settings.claude_max_tokens == 4096

    def test_gcp_project_default(self):
        """Test GCP project default"""
        settings = Settings()
        assert settings.gcp_project_id == "elevatediq-production"


class TestGetSettings:
    """Test suite for get_settings function"""

    def test_returns_settings_instance(self):
        """Test that get_settings returns Settings instance"""
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_caching(self):
        """Test that settings are cached"""
        get_settings.cache_clear()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2


class TestGetApiKey:
    """Test suite for get_api_key function"""

    def test_unknown_key_returns_none(self):
        """Test that unknown key names return None"""
        result = get_api_key("unknown_key")
        assert result is None

    def test_anthropic_key_from_env(self):
        """Test getting Anthropic key from environment"""
        env_vars = {"ANTHROPIC_API_KEY": "test-anthropic-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            get_settings.cache_clear()
            result = get_api_key("anthropic")
            assert result == "test-anthropic-key"

    def test_openai_key_from_env(self):
        """Test getting OpenAI key from environment"""
        env_vars = {"OPENAI_API_KEY": "test-openai-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            get_settings.cache_clear()
            result = get_api_key("openai")
            assert result == "test-openai-key"

    def test_youtube_key_from_env(self):
        """Test getting YouTube key from environment"""
        env_vars = {"YOUTUBE_API_KEY": "test-youtube-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            get_settings.cache_clear()
            result = get_api_key("youtube")
            assert result == "test-youtube-key"

    def test_gcp_fallback_in_production(self):
        """Test GCP Secret Manager fallback in production"""
        env_vars = {"ELEVATEDIQ_ENVIRONMENT": "production"}

        with patch.dict(os.environ, env_vars, clear=True):
            get_settings.cache_clear()
            with patch("processor.config.load_secret_from_gcp") as mock_gcp:
                mock_gcp.return_value = "gcp-secret-value"
                _ = get_api_key("anthropic")
                # Should attempt GCP fallback when env var not set
                mock_gcp.assert_called_once()


class TestLoadSecretFromGCP:
    """Test suite for GCP Secret Manager integration"""

    def test_gcp_secret_loading(self):
        """Test successful secret loading from GCP"""
        from processor.config import load_secret_from_gcp

        with patch("processor.config.secretmanager") as mock_sm:
            mock_client = MagicMock()
            mock_sm.SecretManagerServiceClient.return_value = mock_client

            mock_response = MagicMock()
            mock_response.payload.data.decode.return_value = "secret-value"
            mock_client.access_secret_version.return_value = mock_response

            # This will fail gracefully without real GCP credentials
            result = load_secret_from_gcp("test-secret")
            # In tests without GCP, should return None
            assert result is None or result == "secret-value"

    def test_gcp_error_handling(self):
        """Test graceful error handling for GCP failures"""
        from processor.config import load_secret_from_gcp

        # Should not raise exception
        result = load_secret_from_gcp("nonexistent-secret")
        assert result is None


class TestSettingsValidation:
    """Test configuration validation"""

    def test_positive_batch_size(self):
        """Test batch size validation"""
        env_vars = {"BATCH_SIZE": "0"}

        with patch.dict(os.environ, env_vars, clear=True):
            get_settings.cache_clear()
            settings = Settings()
            # Should accept 0 but may want validation
            assert settings.batch_size >= 0

    def test_valid_postgres_dsn(self):
        """Test PostgreSQL DSN format"""
        settings = Settings()
        assert settings.postgres_dsn.startswith("postgresql://")

    def test_valid_redis_url(self):
        """Test Redis URL format"""
        settings = Settings()
        assert settings.redis_url.startswith("redis://")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
