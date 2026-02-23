"""
ElevatedIQ News Feed Engine - Performance Benchmark Tests

This module provides pytest-benchmark tests for measuring performance
of critical code paths without external dependencies.

Usage:
    pytest testing/test_suite_2/performance/benchmark_tests.py -v --benchmark-only
    pytest testing/test_suite_2/performance/benchmark_tests.py -v --benchmark-autosave
    pytest testing/test_suite_2/performance/benchmark_tests.py -v --benchmark-compare

Requirements:
    pip install pytest-benchmark

Note: These are synchronous benchmarks for CPU-bound operations.
For async operations, see locustfile.py for load testing.
"""

import hashlib
import json
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest

# Try to import pytest-benchmark, skip if not available
try:
    import pytest_benchmark

    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False


# =============================================================================
# Test Data Generators
# =============================================================================


def generate_random_string(length: int = 100) -> str:
    """Generate a random string of specified length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_content_item(include_embeddings: bool = False) -> Dict[str, Any]:
    """Generate a realistic content item for testing."""
    item = {
        "id": str(uuid.uuid4()),
        "title": generate_random_string(50),
        "content": generate_random_string(2000),
        "summary": generate_random_string(200),
        "url": f"https://example.com/news/{uuid.uuid4()}",
        "source": random.choice(["TechCrunch", "Wired", "Ars Technica", "The Verge"]),
        "author": generate_random_string(20),
        "published_at": datetime.now().isoformat(),
        "category": random.choice(["technology", "business", "science", "health"]),
        "tags": [generate_random_string(10) for _ in range(5)],
        "sentiment": random.uniform(-1, 1),
        "relevance_score": random.uniform(0, 1),
        "engagement_score": random.randint(0, 10000),
        "metadata": {
            "word_count": random.randint(100, 5000),
            "reading_time": random.randint(1, 30),
            "language": "en",
        },
    }

    if include_embeddings:
        item["embeddings"] = [random.uniform(-1, 1) for _ in range(768)]

    return item


def generate_content_batch(
    count: int = 100, include_embeddings: bool = False
) -> List[Dict]:
    """Generate a batch of content items."""
    return [generate_content_item(include_embeddings) for _ in range(count)]


def generate_user_preferences() -> Dict[str, Any]:
    """Generate user preference data."""
    return {
        "user_id": str(uuid.uuid4()),
        "categories": random.sample(
            ["technology", "business", "science", "health", "sports"], 3
        ),
        "sources": random.sample(
            ["TechCrunch", "Wired", "Ars Technica", "The Verge", "Reuters"], 3
        ),
        "keywords": [generate_random_string(10) for _ in range(10)],
        "min_relevance": random.uniform(0.5, 0.9),
        "history": [str(uuid.uuid4()) for _ in range(50)],
    }


# =============================================================================
# JSON Serialization Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestJSONSerializationBenchmarks:
    """Benchmark JSON serialization/deserialization operations."""

    def test_serialize_single_content_item(self, benchmark):
        """Benchmark serializing a single content item."""
        item = generate_content_item()
        result = benchmark(json.dumps, item)
        assert isinstance(result, str)

    def test_serialize_content_batch_100(self, benchmark):
        """Benchmark serializing 100 content items."""
        batch = generate_content_batch(100)
        result = benchmark(json.dumps, batch)
        assert isinstance(result, str)

    def test_serialize_content_batch_1000(self, benchmark):
        """Benchmark serializing 1000 content items."""
        batch = generate_content_batch(1000)
        result = benchmark(json.dumps, batch)
        assert isinstance(result, str)

    def test_deserialize_single_content_item(self, benchmark):
        """Benchmark deserializing a single content item."""
        item = generate_content_item()
        json_str = json.dumps(item)
        result = benchmark(json.loads, json_str)
        assert isinstance(result, dict)

    def test_deserialize_content_batch_100(self, benchmark):
        """Benchmark deserializing 100 content items."""
        batch = generate_content_batch(100)
        json_str = json.dumps(batch)
        result = benchmark(json.loads, json_str)
        assert isinstance(result, list)
        assert len(result) == 100


# =============================================================================
# Data Processing Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestDataProcessingBenchmarks:
    """Benchmark data processing operations."""

    def test_content_filtering_by_category(self, benchmark):
        """Benchmark filtering content by category."""
        batch = generate_content_batch(1000)
        target_category = "technology"

        def filter_by_category():
            return [item for item in batch if item["category"] == target_category]

        result = benchmark(filter_by_category)
        assert isinstance(result, list)

    def test_content_filtering_by_relevance(self, benchmark):
        """Benchmark filtering content by relevance score."""
        batch = generate_content_batch(1000)
        min_relevance = 0.7

        def filter_by_relevance():
            return [item for item in batch if item["relevance_score"] >= min_relevance]

        result = benchmark(filter_by_relevance)
        assert isinstance(result, list)

    def test_content_sorting_by_engagement(self, benchmark):
        """Benchmark sorting content by engagement score."""
        batch = generate_content_batch(1000)

        def sort_by_engagement():
            return sorted(batch, key=lambda x: x["engagement_score"], reverse=True)

        result = benchmark(sort_by_engagement)
        assert isinstance(result, list)
        assert len(result) == 1000

    def test_content_deduplication_by_id(self, benchmark):
        """Benchmark deduplicating content by ID."""
        batch = generate_content_batch(500)
        # Add duplicates
        duplicates = random.sample(batch, 100)
        batch_with_dupes = batch + duplicates
        random.shuffle(batch_with_dupes)

        def deduplicate():
            seen = set()
            result = []
            for item in batch_with_dupes:
                if item["id"] not in seen:
                    seen.add(item["id"])
                    result.append(item)
            return result

        result = benchmark(deduplicate)
        assert len(result) == 500

    def test_content_aggregation_by_source(self, benchmark):
        """Benchmark aggregating content by source."""
        batch = generate_content_batch(1000)

        def aggregate_by_source():
            aggregation = {}
            for item in batch:
                source = item["source"]
                if source not in aggregation:
                    aggregation[source] = {"count": 0, "total_engagement": 0}
                aggregation[source]["count"] += 1
                aggregation[source]["total_engagement"] += item["engagement_score"]
            return aggregation

        result = benchmark(aggregate_by_source)
        assert isinstance(result, dict)


# =============================================================================
# Text Processing Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestTextProcessingBenchmarks:
    """Benchmark text processing operations."""

    def test_text_hashing_md5(self, benchmark):
        """Benchmark MD5 hashing of text content."""
        text = generate_random_string(5000)

        def hash_text():
            return hashlib.md5(text.encode()).hexdigest()

        result = benchmark(hash_text)
        assert len(result) == 32

    def test_text_hashing_sha256(self, benchmark):
        """Benchmark SHA256 hashing of text content."""
        text = generate_random_string(5000)

        def hash_text():
            return hashlib.sha256(text.encode()).hexdigest()

        result = benchmark(hash_text)
        assert len(result) == 64

    def test_text_tokenization_basic(self, benchmark):
        """Benchmark basic text tokenization."""
        text = " ".join([generate_random_string(10) for _ in range(1000)])

        def tokenize():
            return text.lower().split()

        result = benchmark(tokenize)
        assert len(result) == 1000

    def test_word_frequency_counting(self, benchmark):
        """Benchmark word frequency counting."""
        words = [
            random.choice(
                [
                    "the",
                    "a",
                    "is",
                    "are",
                    "was",
                    "were",
                    "have",
                    "has",
                    "do",
                    "does",
                    "will",
                    "would",
                    "could",
                    "should",
                ]
            )
            for _ in range(10000)
        ]
        text = " ".join(words)

        def count_frequencies():
            freq = {}
            for word in text.split():
                freq[word] = freq.get(word, 0) + 1
            return freq

        result = benchmark(count_frequencies)
        assert isinstance(result, dict)

    def test_text_normalization(self, benchmark):
        """Benchmark text normalization operations."""
        texts = [generate_random_string(500) for _ in range(100)]

        def normalize_all():
            return [text.lower().strip() for text in texts]

        result = benchmark(normalize_all)
        assert len(result) == 100


# =============================================================================
# Embedding Vector Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestEmbeddingVectorBenchmarks:
    """Benchmark embedding vector operations."""

    def test_cosine_similarity_calculation(self, benchmark):
        """Benchmark cosine similarity between two vectors."""
        import math

        vec_a = [random.uniform(-1, 1) for _ in range(768)]
        vec_b = [random.uniform(-1, 1) for _ in range(768)]

        def cosine_similarity():
            dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
            norm_a = math.sqrt(sum(a * a for a in vec_a))
            norm_b = math.sqrt(sum(b * b for b in vec_b))
            return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0

        result = benchmark(cosine_similarity)
        assert -1 <= result <= 1

    def test_batch_cosine_similarity(self, benchmark):
        """Benchmark cosine similarity for batch of vectors."""
        import math

        query_vec = [random.uniform(-1, 1) for _ in range(768)]
        corpus_vecs = [[random.uniform(-1, 1) for _ in range(768)] for _ in range(100)]

        def batch_similarity():
            results = []
            query_norm = math.sqrt(sum(q * q for q in query_vec))
            for vec in corpus_vecs:
                dot_product = sum(q * v for q, v in zip(query_vec, vec))
                vec_norm = math.sqrt(sum(v * v for v in vec))
                sim = (
                    dot_product / (query_norm * vec_norm)
                    if query_norm and vec_norm
                    else 0
                )
                results.append(sim)
            return results

        result = benchmark(batch_similarity)
        assert len(result) == 100

    def test_euclidean_distance_calculation(self, benchmark):
        """Benchmark Euclidean distance between two vectors."""
        import math

        vec_a = [random.uniform(-1, 1) for _ in range(768)]
        vec_b = [random.uniform(-1, 1) for _ in range(768)]

        def euclidean_distance():
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

        result = benchmark(euclidean_distance)
        assert result >= 0

    def test_vector_averaging(self, benchmark):
        """Benchmark averaging multiple vectors."""
        vectors = [[random.uniform(-1, 1) for _ in range(768)] for _ in range(50)]

        def average_vectors():
            n = len(vectors)
            dim = len(vectors[0])
            result = [0.0] * dim
            for vec in vectors:
                for i, v in enumerate(vec):
                    result[i] += v
            return [v / n for v in result]

        result = benchmark(average_vectors)
        assert len(result) == 768


# =============================================================================
# Data Validation Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestDataValidationBenchmarks:
    """Benchmark data validation operations."""

    def test_uuid_validation(self, benchmark):
        """Benchmark UUID validation."""
        uuids = [str(uuid.uuid4()) for _ in range(1000)]

        def validate_uuids():
            valid = []
            for uid in uuids:
                try:
                    uuid.UUID(uid, version=4)
                    valid.append(True)
                except ValueError:
                    valid.append(False)
            return valid

        result = benchmark(validate_uuids)
        assert all(result)

    def test_url_pattern_validation(self, benchmark):
        """Benchmark URL pattern matching."""
        import re

        urls = [f"https://example.com/path/{i}" for i in range(1000)]
        url_pattern = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"127.0.0.1|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        def validate_urls():
            return [bool(url_pattern.match(url)) for url in urls]

        result = benchmark(validate_urls)
        assert all(result)

    def test_content_item_schema_validation(self, benchmark):
        """Benchmark content item schema validation."""
        items = generate_content_batch(100)
        required_fields = ["id", "title", "content", "url", "source", "published_at"]

        def validate_items():
            results = []
            for item in items:
                is_valid = all(field in item for field in required_fields)
                is_valid = is_valid and isinstance(item.get("id"), str)
                is_valid = is_valid and isinstance(item.get("title"), str)
                is_valid = is_valid and len(item.get("title", "")) > 0
                results.append(is_valid)
            return results

        result = benchmark(validate_items)
        assert all(result)


# =============================================================================
# Date/Time Processing Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestDateTimeProcessingBenchmarks:
    """Benchmark date/time processing operations."""

    def test_iso_datetime_parsing(self, benchmark):
        """Benchmark ISO datetime string parsing."""
        from datetime import datetime

        dates = [(datetime.now() - timedelta(days=i)).isoformat() for i in range(1000)]

        def parse_dates():
            return [
                datetime.fromisoformat(d.replace("Z", "+00:00") if "Z" in d else d)
                for d in dates
            ]

        result = benchmark(parse_dates)
        assert len(result) == 1000

    def test_datetime_range_filtering(self, benchmark):
        """Benchmark filtering items by datetime range."""
        from datetime import datetime

        now = datetime.now()
        items = [
            {"id": i, "created_at": now - timedelta(days=random.randint(0, 365))}
            for i in range(1000)
        ]

        start_date = now - timedelta(days=30)
        end_date = now

        def filter_by_range():
            return [
                item for item in items if start_date <= item["created_at"] <= end_date
            ]

        result = benchmark(filter_by_range)
        assert isinstance(result, list)

    def test_datetime_formatting(self, benchmark):
        """Benchmark datetime formatting."""
        from datetime import datetime

        dates = [datetime.now() - timedelta(days=i) for i in range(1000)]

        def format_dates():
            return [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates]

        result = benchmark(format_dates)
        assert len(result) == 1000


# =============================================================================
# Memory Allocation Benchmarks
# =============================================================================


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
class TestMemoryAllocationBenchmarks:
    """Benchmark memory allocation patterns."""

    def test_list_comprehension_vs_append(self, benchmark):
        """Benchmark list comprehension vs append pattern."""

        def list_comprehension():
            return [i * 2 for i in range(10000)]

        result = benchmark(list_comprehension)
        assert len(result) == 10000

    def test_dict_creation_from_items(self, benchmark):
        """Benchmark dictionary creation from key-value pairs."""
        keys = [f"key_{i}" for i in range(10000)]
        values = list(range(10000))
        pairs = list(zip(keys, values))

        def create_dict():
            return dict(pairs)

        result = benchmark(create_dict)
        assert len(result) == 10000

    def test_set_creation_from_list(self, benchmark):
        """Benchmark set creation from list with duplicates."""
        items = [random.randint(0, 1000) for _ in range(100000)]

        def create_set():
            return set(items)

        result = benchmark(create_set)
        assert isinstance(result, set)


# =============================================================================
# Run benchmarks if pytest-benchmark not available (fallback)
# =============================================================================

if not BENCHMARK_AVAILABLE:

    @pytest.fixture
    def benchmark():
        """Fallback benchmark fixture that just runs the function."""

        def _benchmark(func, *args, **kwargs):
            return func(*args, **kwargs)

        return _benchmark


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
