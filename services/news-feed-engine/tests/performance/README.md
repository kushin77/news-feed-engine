# ElevatedIQ News Feed Engine - Performance Testing Suite

This directory contains comprehensive performance testing tools for the News Feed Engine.

## Overview

| Tool | Purpose | Use Case |
|------|---------|----------|
| `locustfile.py` | HTTP load testing | API endpoint stress testing |
| `benchmark_tests.py` | CPU-bound benchmarks | Code path performance |
| `docker-compose.load-test.yml` | Containerized load testing | CI/CD integration |

## Quick Start

### Prerequisites

```bash
# Install performance testing dependencies
pip install locust pytest-benchmark
```bash

### Run Locust Load Tests

```bash
# Start Locust web UI (interactive mode)
locust -f tests/performance/locustfile.py --host=http://dev.elevatediq.ai:8096

# Headless mode for CI/CD
locust -f tests/performance/locustfile.py \
  --host=http://dev.elevatediq.ai:8096 \
  --headless \
  --users=100 \
  --spawn-rate=10 \
  --run-time=60s \
  --csv=reports/load-test
```bash

Access the Locust web UI at: <http://dev.elevatediq.ai:8089>

### Run Benchmark Tests

```bash
# Run all benchmarks
pytest tests/performance/benchmark_tests.py -v --benchmark-only

# Save benchmark results
pytest tests/performance/benchmark_tests.py -v --benchmark-autosave

# Compare with previous results
pytest tests/performance/benchmark_tests.py -v --benchmark-compare

# Generate JSON report
pytest tests/performance/benchmark_tests.py -v \
  --benchmark-json=reports/benchmark-results.json
```bash

### Docker-Based Load Testing

```bash
# Single mode (for local testing)
docker compose -f docker-compose.load-test.yml up load-tester

# Distributed mode (1 master + 4 workers)
docker compose -f docker-compose.load-test.yml --profile distributed up

# CI/CD mode (headless, generates reports)
docker compose -f docker-compose.load-test.yml --profile ci up load-tester-ci

# Custom configuration
TARGET_HOST=http://api.elevatediq.com:8080 \
LOCUST_USERS=500 \
LOCUST_SPAWN_RATE=50 \
LOCUST_RUN_TIME=300s \
docker compose -f docker-compose.load-test.yml --profile ci up load-tester-ci
```bash

## Locust Load Test Scenarios

### Task Weights

The load test simulates realistic user behavior with weighted tasks:

| Task | Weight | Description |
|------|--------|-------------|
| `health_check` | 50 | Health endpoint monitoring |
| `get_content_feed` | 30 | Main content feed retrieval |
| `get_trending_topics` | 20 | Trending topics API |
| `search_content` | 15 | Content search functionality |
| `get_analytics` | 10 | Analytics data retrieval |
| `submit_content` | 5 | Content submission |
| `get_video_status` | 5 | Video processing status |
| `get_ai_recommendations` | 10 | AI-powered recommendations |
| `get_embeddings` | 5 | Vector embeddings retrieval |
| `batch_operations` | 3 | Bulk operations |

### Custom User Classes

Create custom user classes for specific scenarios:

```python
from locust import HttpUser, task, between

class PowerUser(HttpUser):
    wait_time = between(0.5, 2)
    weight = 10  # 10% of users

    @task(10)
    def heavy_search(self):
        self.client.get("/api/v1/search", params={
            "q": "machine learning",
            "limit": 100,
            "include_embeddings": True
        })

class CasualUser(HttpUser):
    wait_time = between(5, 15)
    weight = 90  # 90% of users

    @task(10)
    def browse_feed(self):
        self.client.get("/api/v1/content", params={"limit": 10})
```bash

## Benchmark Tests

### Categories

1. **JSON Serialization** - Serialization/deserialization performance
2. **Data Processing** - Filtering, sorting, aggregation
3. **Text Processing** - Hashing, tokenization, normalization
4. **Embedding Vectors** - Cosine similarity, Euclidean distance
5. **Data Validation** - Schema validation, pattern matching
6. **DateTime Processing** - Parsing, formatting, filtering
7. **Memory Allocation** - List/dict/set creation patterns

### Sample Output

```

------------------------------------ benchmark: 20 tests ------------------------------------
Name                                      Min      Max     Mean   StdDev   Median
test_serialize_single_content_item     23.1μs   89.2μs   25.6μs    4.2μs   24.3μs
test_serialize_content_batch_100       2.31ms   3.45ms   2.54ms  0.12ms   2.48ms
test_cosine_similarity_calculation     45.2μs   67.8μs   48.3μs   3.1μs   47.1μs
test_content_filtering_by_category     0.89ms   1.23ms   0.94ms  0.05ms   0.92ms

```bash

## Makefile Targets

```bash
# Run load tests
make load-test

# Run benchmark tests
make benchmark

# Run load tests with Docker
make docker-load-test

# Generate performance report
make perf-report
```bash

## CI/CD Integration

### GitHub Actions Example

```yaml
performance-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Start services
      run: docker compose up -d

    - name: Run load tests
      run: |
        docker compose -f docker-compose.load-test.yml --profile ci up \
          --exit-code-from load-tester-ci

    - name: Run benchmarks
      run: |
        pip install pytest pytest-benchmark
        pytest tests/performance/benchmark_tests.py \
          --benchmark-json=reports/benchmark.json

    - name: Upload reports
      uses: actions/upload-artifact@v3
      with:
        name: performance-reports
        path: reports/
```bash

## Performance Baselines

### API Response Time Targets

| Endpoint | P50 | P90 | P99 |
|----------|-----|-----|-----|
| `/health` | <10ms | <20ms | <50ms |
| `/api/v1/content` | <100ms | <200ms | <500ms |
| `/api/v1/search` | <200ms | <400ms | <1000ms |
| `/api/v1/trending` | <50ms | <100ms | <200ms |
| `/api/v1/analytics` | <150ms | <300ms | <600ms |

### Throughput Targets

| Scenario | Target RPS | Notes |
|----------|-----------|-------|
| Light load (10 users) | 500+ RPS | Health checks |
| Medium load (100 users) | 200+ RPS | Mixed workload |
| Heavy load (500 users) | 100+ RPS | Full API utilization |
| Stress test (1000 users) | 50+ RPS | Error rate <1% |

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the target service is running
   - Check firewall/network settings
   - Verify the correct host and port

2. **High Error Rate**
   - Check service logs for errors
   - Reduce spawn rate
   - Increase service resources

3. **Slow Response Times**
   - Check database connections
   - Review caching configuration
   - Monitor CPU/memory usage

### Debug Mode

```bash
# Locust with debug logging
LOCUST_LOGLEVEL=DEBUG locust -f tests/performance/locustfile.py

# Benchmark with detailed output
pytest tests/performance/benchmark_tests.py -v --benchmark-verbose
```bash

## Reports

Reports are generated in the `reports/` directory:

- `load-test_stats.csv` - Request statistics
- `load-test_failures.csv` - Failed requests
- `load-test_stats_history.csv` - Time-series data
- `load-test-report.html` - Interactive HTML report
- `benchmark-results.json` - Benchmark JSON data

## Contributing

When adding new performance tests:

1. Follow existing naming conventions
2. Add appropriate task weights
3. Document expected performance baselines
4. Update this README with new test descriptions
