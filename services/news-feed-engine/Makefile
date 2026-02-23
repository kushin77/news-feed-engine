# ElevatedIQ News Feed Engine - Makefile
# Build, test, and deploy commands

.PHONY: all build test lint clean docker-build docker-push deploy

# Variables
SERVICE_NAME := news-feed-engine
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
DOCKER_REGISTRY := gcr.io/elevatediq-production
GO_FILES := $(shell find . -name '*.go' -not -path "./vendor/*")
PYTHON_FILES := $(shell find processor -name '*.py')

# Go build settings
GOOS ?= linux
GOARCH ?= amd64
CGO_ENABLED := 0
LDFLAGS := -ldflags "-X main.version=$(VERSION) -s -w"

# Default target
all: lint test build

# ==================== BUILD ====================

build: build-go build-python
	@echo "✅ Build complete"

build-go:
	@echo "🔨 Building Go service..."
	CGO_ENABLED=$(CGO_ENABLED) GOOS=$(GOOS) GOARCH=$(GOARCH) \
		go build $(LDFLAGS) -o bin/$(SERVICE_NAME) ./cmd/news-feed

build-python:
	@echo "📦 Building Python processor..."
	cd processor && pip install -r requirements.txt --quiet

# ==================== TEST ====================

test: test-go test-python
	@echo "✅ All tests passed"

test-go:
	@echo "🧪 Running Go tests..."
	go test -v -race -cover ./...

test-python:
	@echo "🧪 Running Python tests..."
	cd processor && python -m pytest tests/ -v --tb=short

test-integration:
	@echo "🔗 Running integration tests..."
	SKIP_INTEGRATION_TESTS=false python -m pytest tests/integration/ -v -m integration

test-coverage:
	@echo "📊 Generating coverage report..."
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	cd processor && python -m pytest --cov=processor --cov-report=html tests/

# ==================== LINT ====================

lint: lint-go lint-python
	@echo "✅ Linting complete"

lint-go:
	@echo "🔍 Linting Go code..."
	golangci-lint run ./...

lint-python:
	@echo "🔍 Linting Python code..."
	cd processor && python -m flake8 . --max-line-length=79
	cd processor && python -m black --check .
	cd processor && python -m isort --check-only .

format:
	@echo "🎨 Formatting code..."
	gofmt -w $(GO_FILES)
	cd processor && python -m black .
	cd processor && python -m isort .

# ==================== DOCKER ====================

docker-build:
	@echo "🐳 Building Docker images..."
	docker build -t $(DOCKER_REGISTRY)/$(SERVICE_NAME):$(VERSION) .
	docker build -t $(DOCKER_REGISTRY)/$(SERVICE_NAME)-processor:$(VERSION) \
		-f processor/Dockerfile processor/

docker-build-test:
	@echo "🐳 Building Docker test images..."
	docker build -t $(DOCKER_REGISTRY)/$(SERVICE_NAME)-processor:test \
		--target test -f processor/Dockerfile processor/

docker-push:
	@echo "📤 Pushing Docker images..."
	docker push $(DOCKER_REGISTRY)/$(SERVICE_NAME):$(VERSION)
	docker push $(DOCKER_REGISTRY)/$(SERVICE_NAME)-processor:$(VERSION)

docker-up:
	@echo "🚀 Starting local development environment..."
	docker-compose -f docker-compose.news-feed.yml up -d

docker-down:
	@echo "🛑 Stopping local development environment..."
	docker-compose -f docker-compose.news-feed.yml down

docker-logs:
	@echo "📋 Showing logs..."
	docker-compose -f docker-compose.news-feed.yml logs -f

# ==================== DOCKER INTEGRATION TESTS ====================

test-docker:
	@echo "🐳 Running containerized test suite..."
	docker-compose -f docker-compose.test.yml up -d test-postgres test-redis
	@sleep 5
	docker-compose -f docker-compose.test.yml run --rm test-runner
	docker-compose -f docker-compose.test.yml down -v

test-docker-integration:
	@echo "🔗 Running containerized integration tests..."
	docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-kafka
	@sleep 10
	docker-compose -f docker-compose.test.yml run --rm integration-test-runner
	docker-compose -f docker-compose.test.yml down -v

test-docker-lint:
	@echo "🔍 Running containerized linting..."
	docker-compose -f docker-compose.test.yml run --rm lint-runner

test-docker-security:
	@echo "🔒 Running containerized security scan..."
	docker-compose -f docker-compose.test.yml run --rm security-scanner

test-docker-all:
	@echo "🚀 Running full containerized test suite..."
	docker-compose -f docker-compose.test.yml up -d test-postgres test-redis test-kafka
	@sleep 10
	docker-compose -f docker-compose.test.yml run --rm lint-runner
	docker-compose -f docker-compose.test.yml run --rm security-scanner
	docker-compose -f docker-compose.test.yml run --rm test-runner
	docker-compose -f docker-compose.test.yml run --rm integration-test-runner
	docker-compose -f docker-compose.test.yml down -v
	@echo "✅ All containerized tests complete"

test-docker-clean:
	@echo "🧹 Cleaning up test containers..."
	docker-compose -f docker-compose.test.yml down -v --remove-orphans
	docker volume rm -f elevatediq-test-postgres-data elevatediq-test-coverage 2>/dev/null || true

# ==================== PERFORMANCE TESTS ====================

load-test:
	@echo "🚀 Starting Locust load test (Web UI)..."
	locust -f tests/performance/locustfile.py \
		--host=http://localhost:8096 \
		--web-host=0.0.0.0
	@echo "Access Locust UI at: http://localhost:8089"

load-test-headless:
	@echo "🚀 Running headless load test..."
	@mkdir -p reports
	locust -f tests/performance/locustfile.py \
		--host=http://localhost:8096 \
		--headless \
		--users=100 \
		--spawn-rate=10 \
		--run-time=60s \
		--csv=reports/load-test \
		--html=reports/load-test-report.html
	@echo "✅ Load test complete. Reports in reports/"

benchmark:
	@echo "📊 Running benchmark tests..."
	cd processor && source venv/bin/activate && \
		python -m pytest ../tests/performance/benchmark_tests.py \
		-v --benchmark-only
	@echo "✅ Benchmark tests complete"

benchmark-save:
	@echo "📊 Running and saving benchmark results..."
	@mkdir -p reports
	cd processor && source venv/bin/activate && \
		python -m pytest ../tests/performance/benchmark_tests.py \
		-v --benchmark-autosave \
		--benchmark-json=../reports/benchmark-results.json
	@echo "✅ Benchmark results saved to reports/"

benchmark-compare:
	@echo "📊 Comparing benchmark results with previous run..."
	cd processor && source venv/bin/activate && \
		python -m pytest ../tests/performance/benchmark_tests.py \
		-v --benchmark-compare
	@echo "✅ Benchmark comparison complete"

docker-load-test:
	@echo "🐳 Running Docker load test (Web UI)..."
	docker compose -f docker-compose.load-test.yml up load-tester
	@echo "Access Locust UI at: http://localhost:8089"

docker-load-test-ci:
	@echo "🐳 Running Docker load test (CI mode)..."
	@mkdir -p reports
	docker compose -f docker-compose.load-test.yml --profile ci up \
		--exit-code-from load-tester-ci
	@echo "✅ Docker load test complete. Reports in reports/"

docker-load-test-distributed:
	@echo "🐳 Running distributed Docker load test..."
	docker compose -f docker-compose.load-test.yml --profile distributed up
	@echo "Access Locust UI at: http://localhost:8089"

docker-load-test-clean:
	@echo "🧹 Cleaning up load test containers..."
	docker compose -f docker-compose.load-test.yml down -v --remove-orphans

perf-report:
	@echo "📈 Generating performance report..."
	@mkdir -p reports
	@echo "# Performance Test Report" > reports/PERFORMANCE_REPORT.md
	@echo "Generated: $$(date)" >> reports/PERFORMANCE_REPORT.md
	@echo "" >> reports/PERFORMANCE_REPORT.md
	@if [ -f reports/benchmark-results.json ]; then \
		echo "## Benchmark Results" >> reports/PERFORMANCE_REPORT.md; \
		echo "See benchmark-results.json for detailed metrics." >> reports/PERFORMANCE_REPORT.md; \
	fi
	@if [ -f reports/load-test_stats.csv ]; then \
		echo "## Load Test Results" >> reports/PERFORMANCE_REPORT.md; \
		echo "See load-test_stats.csv for detailed metrics." >> reports/PERFORMANCE_REPORT.md; \
	fi
	@echo "✅ Performance report generated"

# ==================== SECURITY TESTS ====================

security-test:
	@echo "🔒 Running security tests..."
	cd processor && source venv/bin/activate && \
		python -m pytest ../tests/security/ -v -m security
	@echo "✅ Security tests complete"

security-scan:
	@echo "🔍 Running Bandit security scan..."
	@mkdir -p reports
	cd processor && source venv/bin/activate && \
		bandit -r . -f json -o ../reports/bandit-report.json || true
	@echo "✅ Bandit scan complete. Report: reports/bandit-report.json"

security-deps:
	@echo "📦 Checking for vulnerable dependencies..."
	@mkdir -p reports
	cd processor && source venv/bin/activate && \
		pip-audit -o ../reports/pip-audit-report.json --format=json || true
	@echo "✅ Dependency scan complete. Report: reports/pip-audit-report.json"

security-audit:
	@echo "🛡️ Running full security audit..."
	@mkdir -p reports
	$(MAKE) security-test
	$(MAKE) security-scan
	$(MAKE) security-deps
	@echo ""
	@echo "📊 Security Audit Summary"
	@echo "========================="
	@echo "Security tests: ✅ Complete"
	@echo "Bandit scan: ✅ Complete"
	@echo "Dependency scan: ✅ Complete"
	@echo ""
	@echo "Reports available in reports/ directory"
	@echo "✅ Full security audit complete"

# ==================== DEPLOY ====================

deploy-staging:
	@echo "🚀 Deploying to staging..."
	kubectl apply -k k8s/overlays/staging/

deploy-production:
	@echo "🚀 Deploying to production..."
	kubectl apply -k k8s/overlays/production/

rollback:
	@echo "⏪ Rolling back deployment..."
	kubectl rollout undo deployment/$(SERVICE_NAME)

# ==================== DATABASE ====================

migrate-up:
	@echo "📈 Running database migrations..."
	migrate -path migrations -database "$(POSTGRES_DSN)" up

migrate-down:
	@echo "📉 Rolling back database migration..."
	migrate -path migrations -database "$(POSTGRES_DSN)" down 1

migrate-status:
	@echo "📊 Migration status..."
	migrate -path migrations -database "$(POSTGRES_DSN)" version

# ==================== DEVELOPMENT ====================

dev:
	@echo "🔧 Starting development server..."
	go run ./cmd/news-feed

dev-processor:
	@echo "🔧 Starting Python processor..."
	cd processor && python -m processor.main

generate:
	@echo "⚙️ Generating code..."
	go generate ./...

openapi-validate:
	@echo "📋 Validating OpenAPI spec..."
	npx @apidevtools/swagger-cli validate api/openapi.yaml

# ==================== CLEAN ====================

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf bin/
	rm -rf coverage.out coverage.html
	rm -rf processor/__pycache__ processor/**/__pycache__
	rm -rf processor/.pytest_cache
	rm -rf processor/htmlcov
	docker-compose -f docker-compose.news-feed.yml down -v --remove-orphans

# ==================== HELP ====================

help:
	@echo "ElevatedIQ News Feed Engine - Available Commands"
	@echo ""
	@echo "Build:"
	@echo "  make build          - Build Go and Python components"
	@echo "  make build-go       - Build Go service only"
	@echo "  make build-python   - Install Python dependencies"
	@echo ""
	@echo "Test:"
	@echo "  make test           - Run all tests"
	@echo "  make test-go        - Run Go tests"
	@echo "  make test-python    - Run Python tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-coverage  - Generate coverage reports"
	@echo ""
	@echo "Docker Tests:"
	@echo "  make test-docker        - Run containerized tests"
	@echo "  make test-docker-all    - Run full containerized suite"
	@echo "  make test-docker-clean  - Clean up test containers"
	@echo ""
	@echo "Performance:"
	@echo "  make load-test          - Start Locust load test (Web UI)"
	@echo "  make load-test-headless - Run headless load test"
	@echo "  make benchmark          - Run benchmark tests"
	@echo "  make benchmark-save     - Run and save benchmark results"
	@echo "  make benchmark-compare  - Compare with previous benchmarks"
	@echo "  make docker-load-test   - Docker load test (Web UI)"
	@echo "  make docker-load-test-ci - Docker load test (CI mode)"
	@echo "  make perf-report        - Generate performance report"
	@echo ""
	@echo "Security:"
	@echo "  make security-test      - Run security tests"
	@echo "  make security-scan      - Run Bandit security scan"
	@echo "  make security-deps      - Check for vulnerable dependencies"
	@echo "  make security-audit     - Run full security audit"
	@echo ""
	@echo "Lint:"
	@echo "  make lint           - Run all linters"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-push    - Push to registry"
	@echo "  make docker-up      - Start local environment"
	@echo "  make docker-down    - Stop local environment"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy-staging     - Deploy to staging"
	@echo "  make deploy-production  - Deploy to production"
	@echo "  make rollback           - Rollback deployment"
	@echo ""
	@echo "Database:"
	@echo "  make migrate-up     - Run migrations"
	@echo "  make migrate-down   - Rollback migration"
	@echo "  make migrate-status - Show migration status"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start Go dev server"
	@echo "  make dev-processor  - Start Python processor"
	@echo "  make clean          - Clean build artifacts"
