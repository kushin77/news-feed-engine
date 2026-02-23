# ElevatedIQ News Feed Engine - Clean multi-stage Dockerfile

# Build stage
FROM golang:1.24-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /app

# Copy full source so local replace directives (if build context is repo root)
# resolve during build. When building from service directory, this will copy
# only the service sources; for internal replace mappings, build with repo root
# as context: docker build -f services/news-feed-engine/Dockerfile -t image .
COPY . .

# Download dependencies
RUN go mod download

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -mod=mod -ldflags='-w -s' -o /app/news-feed-engine ./cmd/news-feed

# Production stage
FROM alpine:3.19

# Runtime deps
RUN apk add --no-cache ca-certificates tzdata curl

# Create non-root user
RUN addgroup -g 1001 -S elevatediq && \
    adduser -u 1001 -S elevatediq -G elevatediq

WORKDIR /app

# Copy binary and migrations from builder
COPY --from=builder /app/news-feed-engine /app/
COPY --from=builder /app/migrations /app/migrations

# Ensure ownership
RUN chown -R elevatediq:elevatediq /app || true

USER elevatediq

EXPOSE 8080

# Healthcheck probes local loopback
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD ["curl", "-f", "http://127.0.0.1:8080/health"]

ENV ELEVATEDIQ_ENVIRONMENT=production \
    PORT=8080

ENTRYPOINT ["/app/news-feed-engine"]
# ElevatedIQ News Feed Engine Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM golang:1.24-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory
WORKDIR /app

# Copy full source so local replace directives resolve during build
COPY . .

# Download dependencies
RUN go mod download

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -mod=mod \
    -ldflags="-w -s -X main.version=$(git describe --tags --always --dirty 2>/dev/null || echo 'dev')" \
    -o /app/news-feed-engine \
    ./cmd/news-feed

# Production stage
FROM alpine:3.19

# Install runtime dependencies
RUN apk add --no-cache ca-certificates tzdata curl

# Create non-root user for security
RUN addgroup -g 1001 -S elevatediq && \
    adduser -u 1001 -S elevatediq -G elevatediq

# Set working directory
WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/news-feed-engine /app/

# Copy migrations for database setup (if present)
COPY --from=builder /app/migrations /app/migrations

# Set ownership
RUN chown -R elevatediq:elevatediq /app || true

# Switch to non-root user
USER elevatediq

# Expose port
EXPOSE 8080

# Health check (probe container-local address)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["curl","-f","http://127.0.0.1:8080/health"]

# Set environment variables
ENV ELEVATEDIQ_ENVIRONMENT=production \
    PORT=8080

# Run the binary
ENTRYPOINT ["/app/news-feed-engine"]
# ElevatedIQ News Feed Engine Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM golang:1.24-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory
WORKDIR /app

# Copy go mod file for dependency download (avoid failing COPY if pkg/ absent)
COPY go.mod ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -mod=mod \
    -ldflags="-w -s -X main.version=$(git describe --tags --always --dirty 2>/dev/null || echo 'dev')" \
    -o /app/news-feed-engine \
    ./cmd/news-feed

# Production stage
FROM alpine:3.19

# Install runtime dependencies
RUN apk add --no-cache ca-certificates tzdata curl

RUN go mod download
RUN addgroup -g 1001 -S elevatediq && \
    adduser -u 1001 -S elevatediq -G elevatediq
COPY . .
# Set working directory
# Set working directory
WORKDIR /app

# Copy source code first so local replace directives can resolve
# (some builds reference the repo root as a replace target).
COPY . .

# Download dependencies after source is present
RUN go mod download
WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/news-feed-engine /app/

# Copy migrations for database setup
COPY --from=builder /app/migrations /app/migrations

# Set ownership
RUN chown -R elevatediq:elevatediq /app

# Switch to non-root user
USER elevatediq

# Expose port
EXPOSE 8080

# Health check
# Health check (probe container-local address)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["curl","-f","http://127.0.0.1:8080/health"]

# Set environment variables
ENV ELEVATEDIQ_ENVIRONMENT=production \
    PORT=8080

# Run the binary
ENTRYPOINT ["/app/news-feed-engine"]
