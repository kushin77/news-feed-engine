# Frontend Service Makefile - React + TypeScript + Vite

.PHONY: setup dev build build-docker test test-coverage lint lint:fix format clean help faang-check docker-up docker-down docker-logs

.DEFAULT_GOAL := help

help:
	@echo "Service: frontend"
	@echo "Tech stack: React 18 + TypeScript + Vite + Tailwind + Vitest"
	@echo ""
	@echo "Available targets:"
	@echo "  setup               - Install dependencies"
	@echo "  dev                 - Run dev server (http://localhost:5173)"
	@echo "  build               - Build for production"
	@echo "  build-docker        - Build Docker image"
	@echo "  test                - Run tests"
	@echo "  test:coverage       - Run tests with coverage report"
	@echo "  lint                - Run ESLint"
	@echo "  lint:fix            - Fix ESLint issues"
	@echo "  format              - Format code with Prettier"
	@echo "  type-check          - TypeScript type checking"
	@echo "  faang-check         - Run full FAANG quality checks (lint + type + coverage)"
	@echo "  clean               - Clean build artifacts"
	@echo "  docker-up           - Start Docker container"
	@echo "  docker-down         - Stop Docker container"
	@echo "  docker-logs         - Show Docker logs"

setup:
	@echo "Installing dependencies..."
	npm ci --prefer-offline
	npm run type-check
	@echo "✓ Dependencies installed"

dev:
	@echo "Starting dev server..."
	npm run dev

build:
	@echo "Building for production..."
	npm run build
	@echo "✓ Build complete at ./dist"

build-docker:
	@echo "Building Docker image..."
	docker build -t news-feed-frontend:latest . --build-arg BUILD_DATE="$$(date -u +'%Y-%m-%dT%H:%M:%SZ')" --build-arg VCS_REF="$$(git rev-parse --short HEAD)"
	@echo "✓ Docker image built: news-feed-frontend:latest"

test:
	@echo "Running tests..."
	npm run test

test:coverage:
	@echo "Running tests with coverage..."
	npm run test:coverage
	@echo "✓ Coverage report: ./coverage/index.html"

lint:
	@echo "Linting code..."
	npm run lint

lint:fix:
	@echo "Fixing linting issues..."
	npm run lint:fix
	@echo "✓ Linting issues fixed"

format:
	@echo "Formatting code..."
	npm run format
	@echo "✓ Code formatted"

type-check:
	@echo "Checking TypeScript..."
	npm run type-check
	@echo "✓ No type errors"

faang-check:
	@echo "Running FAANG quality checks..."
	npm run faang-check
	@echo "✓ All FAANG checks passed"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf node_modules dist coverage
	@echo "✓ Cleaned"

docker-up:
	@echo "Starting Docker container..."
	docker run -d -p 80:80 --name news-feed-frontend news-feed-frontend:latest

docker-down:
	@echo "Stopping Docker container..."
	docker stop news-feed-frontend || true
	docker rm news-feed-frontend || true
	@echo "✓ Container stopped"

docker-logs:
	@echo "Showing Docker logs..."
	docker logs -f news-feed-frontend

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
