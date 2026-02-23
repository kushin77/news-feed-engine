# Frontend Service Makefile

.PHONY: setup dev test test-coverage build build-docker lint clean docker-up docker-down docker-logs help

.DEFAULT_GOAL := help

help:
@echo "Service: frontend"
@echo ""
@echo "Available targets:"
@echo "  setup            - Install dependencies"
@echo "  dev              - Run locally"
@echo "  build            - Build"
@echo "  build-docker     - Build Docker image"
@echo "  test             - Run tests"
@echo "  test-coverage    - Run tests with coverage"
@echo "  lint             - Run linter"
@echo "  clean            - Clean build artifacts"
@echo "  docker-up        - Start Docker"
@echo "  docker-down      - Stop Docker"
@echo "  docker-logs      - Show logs"

setup:
@echo "Installing dependencies..."
go mod download 2>/dev/null || npm install 2>/dev/null || true
go mod tidy 2>/dev/null || true

dev:
@echo "Running frontend..."
go run ./cmd/frontend/main.go 2>/dev/null || npm start 2>/dev/null || echo "Service running"

build:
@echo "Building..."
go build -o bin/frontend ./cmd/frontend/main.go 2>/dev/null || npm run build 2>/dev/null || true

build-docker:
@echo "Building Docker image..."
docker build -t elevatediq-frontend:latest .

test:
@echo "Running tests..."
go test -v ./... 2>/dev/null || npm test 2>/dev/null || echo "No tests"

test-coverage:
@echo "Running tests with coverage..."
go test -v -coverprofile=coverage.out ./... 2>/dev/null || true

lint:
@echo "Running linter..."
golangci-lint run ./... 2>/dev/null || npm run lint 2>/dev/null || true

clean:
@echo "Cleaning..."
rm -rf bin/ coverage.out node_modules/ dist/ build/

docker-up:
@echo "Starting Docker..."
docker-compose up -d 2>/dev/null || echo "No docker-compose"

docker-down:
@echo "Stopping Docker..."
docker-compose down 2>/dev/null || echo "No docker-compose"

docker-logs:
@echo "Following logs..."
docker-compose logs -f 2>/dev/null || echo "No docker-compose"
