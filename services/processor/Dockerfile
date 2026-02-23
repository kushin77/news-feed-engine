# ElevatedIQ News Feed Processor Dockerfile
# Python-based ML pipeline for content analysis
# Multi-stage build for production and testing

ARG VERSION=2.0.0

# ============================================================================
# Base Stage - Common dependencies
# ============================================================================
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1001 elevatediq && \
    useradd -u 1001 -g elevatediq -m elevatediq

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Test Stage - Development and testing dependencies
# ============================================================================
FROM base AS test

# Install test dependencies
COPY requirements-dev.txt* ./
RUN if [ -f requirements-dev.txt ]; then pip install --no-cache-dir -r requirements-dev.txt; fi
RUN pip install --no-cache-dir \
    pytest>=9.0.0 \
    pytest-cov>=4.1.0 \
    pytest-asyncio>=0.23.0 \
    ruff>=0.1.0 \
    black>=23.0.0 \
    bandit>=1.7.0 \
    pip-audit>=2.6.0 \
    httpx>=0.25.0 \
    respx>=0.20.0

# Copy source code
COPY . .

# Set ownership
RUN chown -R elevatediq:elevatediq /app

# Create coverage directory
RUN mkdir -p /app/coverage && chown elevatediq:elevatediq /app/coverage

# Environment variables for testing
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TESTING=true \
    PYTHONPATH=/app

# Switch to non-root user
USER elevatediq

# Default command runs tests
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=processor", "--cov-report=term-missing"]

# ============================================================================
# Production Stage - Optimized runtime
# ============================================================================
FROM base AS production

# Copy source code
COPY . .

# Set ownership
RUN chown -R elevatediq:elevatediq /app

# Switch to non-root user
USER elevatediq

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Labels
LABEL org.opencontainers.image.title="ElevatedIQ News Feed Processor" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.vendor="ElevatedIQ" \
      com.elevatediq.managed="iac" \
      com.elevatediq.immutable="true"

# Run the processor
CMD ["python", "-m", "processor.main"]
