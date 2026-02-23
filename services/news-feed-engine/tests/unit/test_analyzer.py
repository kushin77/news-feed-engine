"""
ElevatedIQ News Feed Engine - Unit Tests for Content Analyzer
"""

import json
import pytest
from unittest.mock import MagicMock, patch

# Import module under test
import sys

sys.path.insert(0, "../../processor")

from processor.analyzer import ContentAnalyzer, VideoScriptGenerator


class TestContentAnalyzer:
    """Test suite for ContentAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance with mocked client"""
        with patch("processor.analyzer.get_api_key") as mock_key:
            mock_key.return_value = "test-api-key"
            with patch("processor.analyzer.anthropic.Anthropic") as _:
                analyzer = ContentAnalyzer()
                analyzer.client = MagicMock()
                return analyzer

    @pytest.fixture
    def sample_content(self):
        """Sample content for testing"""
        return {
            "text": """
            Breaking: OpenAI announces GPT-5 with revolutionary capabilities.
            The new model demonstrates unprecedented reasoning abilities
            and marks a significant milestone in AI development.
            CEO Sam Altman presented the breakthrough at a tech conference.
            """,
            "platform": "twitter",
            "metadata": {"author": "tech_news", "followers": 500000},
        }

    def test_categories_defined(self, analyzer):
        """Test that valid categories are defined"""
        assert len(analyzer.CATEGORIES) > 0
        assert "technology" in analyzer.CATEGORIES
        assert "business" in analyzer.CATEGORIES
        assert "finance" in analyzer.CATEGORIES

    def test_geo_classifications_defined(self, analyzer):
        """Test that geographic classifications are defined"""
        assert len(analyzer.GEO_CLASSIFICATIONS) == 4
        assert "local" in analyzer.GEO_CLASSIFICATIONS
        assert "global" in analyzer.GEO_CLASSIFICATIONS

    def test_validate_category_valid(self, analyzer):
        """Test category validation with valid input"""
        assert analyzer._validate_category("technology") == "technology"
        assert analyzer._validate_category("BUSINESS") == "business"
        assert analyzer._validate_category("Finance") == "finance"

    def test_validate_category_invalid(self, analyzer):
        """Test category validation with invalid input"""
        assert analyzer._validate_category("invalid") == "technology"
        assert analyzer._validate_category(None) == "technology"
        assert analyzer._validate_category("") == "technology"

    def test_validate_geo_valid(self, analyzer):
        """Test geographic classification validation"""
        assert analyzer._validate_geo("local") == "local"
        assert analyzer._validate_geo("GLOBAL") == "global"

    def test_validate_geo_invalid(self, analyzer):
        """Test geographic classification with invalid input"""
        assert analyzer._validate_geo("invalid") == "global"
        assert analyzer._validate_geo(None) == "global"

    def test_clamp_values(self, analyzer):
        """Test value clamping function"""
        assert analyzer._clamp(0.5, 0.0, 1.0) == 0.5
        assert analyzer._clamp(-0.5, 0.0, 1.0) == 0.0
        assert analyzer._clamp(1.5, 0.0, 1.0) == 1.0
        assert analyzer._clamp("invalid", 0.0, 1.0) == 0.5

    def test_default_analysis(self, analyzer):
        """Test default analysis structure"""
        result = analyzer._default_analysis()

        assert "summary" in result
        assert "category" in result
        assert "tags" in result
        assert "sentiment" in result
        assert "quality_score" in result
        assert "geo_classification" in result
        assert "key_points" in result
        assert "entities" in result
        assert "credibility_score" in result
        assert "bias_assessment" in result

        # Verify defaults
        assert result["category"] == "technology"
        assert result["sentiment"] == 0.0
        assert result["quality_score"] == 0.5

    def test_parse_response_valid_json(self, analyzer):
        """Test parsing valid JSON response"""
        response = json.dumps(
            {
                "summary": "Test summary",
                "category": "technology",
                "tags": ["ai", "tech"],
                "sentiment": 0.8,
                "quality_score": 0.9,
                "geo_classification": "global",
                "key_points": ["Point 1", "Point 2"],
                "entities": [{"name": "OpenAI", "type": "org"}],
                "topics": ["AI", "Machine Learning"],
                "credibility_score": 0.85,
                "bias_assessment": {"detected": False, "type": None, "confidence": 0.0},
            }
        )

        result = analyzer._parse_response(response)

        assert result["summary"] == "Test summary"
        assert result["category"] == "technology"
        assert len(result["tags"]) == 2
        assert result["sentiment"] == 0.8

    def test_parse_response_with_code_block(self, analyzer):
        """Test parsing response with markdown code blocks"""
        response = """```json
{
    "summary": "Test summary",
    "category": "business",
    "tags": ["finance"],
    "sentiment": 0.5,
    "quality_score": 0.7,
    "geo_classification": "regional",
    "key_points": [],
    "entities": [],
    "topics": [],
    "credibility_score": 0.6,
    "bias_assessment": {"detected": false}
}
```"""

        result = analyzer._parse_response(response)
        assert result["category"] == "business"

    def test_parse_response_invalid_json(self, analyzer):
        """Test parsing invalid JSON falls back to default"""
        result = analyzer._parse_response("not valid json")
        assert result == analyzer._default_analysis()

    def test_build_analysis_prompt(self, analyzer):
        """Test prompt building includes required elements"""
        prompt = analyzer._build_analysis_prompt(
            text="Sample text", platform="youtube", metadata={"channel": "TechNews"}
        )

        assert "youtube" in prompt.lower()
        assert "Sample text" in prompt
        assert "category" in prompt.lower()
        assert "sentiment" in prompt.lower()

    @pytest.mark.asyncio
    async def test_analyze_no_client(self):
        """Test analyze returns default when client not initialized"""
        with patch("processor.analyzer.get_api_key") as mock_key:
            mock_key.return_value = None
            analyzer = ContentAnalyzer()

            result = await analyzer.analyze(text="Test content", platform="twitter")

            assert result == analyzer._default_analysis()


class TestVideoScriptGenerator:
    """Test suite for VideoScriptGenerator class"""

    @pytest.fixture
    def generator(self):
        """Create generator instance"""
        with patch("processor.analyzer.get_api_key") as mock_key:
            mock_key.return_value = "test-api-key"
            with patch("processor.analyzer.anthropic.Anthropic"):
                return VideoScriptGenerator()

    @pytest.fixture
    def sample_content(self):
        """Sample processed content"""
        return {
            "title": "AI Breakthrough",
            "summary": "Major advancement in AI technology announced",
            "ai_analysis": {
                "key_points": [
                    "New model released",
                    "Improved performance",
                    "Industry impact",
                ]
            },
        }

    def test_default_script_structure(self, generator, sample_content):
        """Test default script has required fields"""
        result = generator._default_script(sample_content)

        assert "title" in result
        assert "hook" in result
        assert "body" in result
        assert "call_to_action" in result
        assert "scenes" in result
        assert "total_words" in result
        assert "estimated_duration" in result

    def test_default_script_uses_content(self, generator, sample_content):
        """Test default script incorporates content"""
        result = generator._default_script(sample_content)

        assert result["title"] == sample_content["title"]
        assert sample_content["summary"] in result["body"]


class TestAnalyzerEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_text_analysis(self):
        """Test handling of empty text"""
        with patch("processor.analyzer.get_api_key") as mock_key:
            mock_key.return_value = None
            analyzer = ContentAnalyzer()
            result = analyzer._default_analysis()
            assert result["summary"] == ""

    def test_very_long_text_truncation(self):
        """Test that very long text is handled"""
        with patch("processor.analyzer.get_api_key") as mock_key:
            mock_key.return_value = "test-key"
            with patch("processor.analyzer.anthropic.Anthropic"):
                analyzer = ContentAnalyzer()

                # Create very long text
                long_text = "word " * 10000

                # Build prompt should truncate
                prompt = analyzer._build_analysis_prompt(
                    text=long_text, platform="rss", metadata=None
                )

                # Verify truncation occurred (8000 char limit in code)
                assert len(prompt) < len(long_text)

    def test_special_characters_in_text(self):
        """Test handling of special characters"""
        with patch("processor.analyzer.get_api_key") as mock_key:
            mock_key.return_value = "test-key"
            with patch("processor.analyzer.anthropic.Anthropic"):
                analyzer = ContentAnalyzer()

                special_text = "Test with émojis 🚀 and spëcial çharacters"
                prompt = analyzer._build_analysis_prompt(
                    text=special_text, platform="twitter", metadata={}
                )

                assert special_text in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
