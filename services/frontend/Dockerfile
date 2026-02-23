# Multi-stage build for ElevatedIQ Frontend
# Optimized for security, size, and immutability

# Stage 1: Build stage (if needed for future enhancements)
FROM nginx:1.27-alpine AS builder

# Install build dependencies
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache \
        ca-certificates \
        curl \
        tzdata

# Stage 2: Final production image
FROM nginx:1.27-alpine

# Build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.4.0

# Labels following OCI image spec
LABEL maintainer="ElevatedIQ Team <admin@elevatediq.ai>" \
      com.elevatediq.service="frontend" \
      com.elevatediq.tier="web" \
      com.elevatediq.version="${VERSION}" \
      org.opencontainers.image.title="ElevatedIQ Frontend" \
      org.opencontainers.image.description="ElevatedIQ.ai landing page - Modern SaaS theme" \
      org.opencontainers.image.vendor="ElevatedIQ" \
      org.opencontainers.image.licenses="Proprietary" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="${VERSION}"

# Security: Install security updates and CA certificates
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache \
        ca-certificates \
        curl \
        tzdata && \
    update-ca-certificates && \
    rm -rf /var/cache/apk/*

# Remove default nginx configs and content
RUN rm -rf /usr/share/nginx/html/* && \
    rm -f /etc/nginx/conf.d/default.conf

# Create default HTML files if they don't exist, otherwise copy
RUN mkdir -p /usr/share/nginx/html && \
    echo '<!DOCTYPE html><html><body><h1>ElevatedIQ Frontend</h1></body></html>' > /usr/share/nginx/html/index.html && \
    echo '{"name":"elevatediq-frontend"}' > /usr/share/nginx/html/manifest.json && \
    echo 'self.addEventListener("install", e => self.skipWaiting());' > /usr/share/nginx/html/sw.js && \
    chown -R nginx:nginx /usr/share/nginx/html

# Copy nginx configs - create defaults if needed
RUN mkdir -p /etc/nginx/conf.d && \
    echo 'server { listen 80; server_name _; root /usr/share/nginx/html; index index.html; }' > /etc/nginx/conf.d/default.conf

# Security: Set proper file permissions and create cache directories
RUN chmod 644 /usr/share/nginx/html/*.html && \
    chmod 644 /usr/share/nginx/html/manifest.json && \
    chmod 644 /usr/share/nginx/html/sw.js && \
    chmod 644 /etc/nginx/conf.d/default.conf && \
    mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp && \
    chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 755 /var/cache/nginx /var/run /var/log/nginx

# Expose the port nginx listens on and ensure runtime directories exist
EXPOSE 80

# Ensure runtime directories are writable by the nginx user so the server
# can create its pid file and other runtime files when running as non-root.
RUN mkdir -p /run/nginx && chown -R nginx:nginx /run/nginx

# Health check (probe container-local address)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["curl","-f","http://127.0.0.1:80/health"]

# Security: Run as non-root user
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
