"""
ElevatedIQ News Feed Engine - Performance Testing Suite

This package provides comprehensive performance testing tools:

- locustfile.py: HTTP load testing with Locust
- benchmark_tests.py: CPU-bound benchmarks with pytest-benchmark
- docker-compose.load-test.yml: Containerized load testing

Usage:
    # Load testing
    locust -f testing/test_suite_2/performance/locustfile.py --host=http://127.0.0.1:8096

    # Benchmark testing
    pytest testing/test_suite_2/performance/benchmark_tests.py -v --benchmark-only
"""
