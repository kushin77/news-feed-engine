# STAGE 1: Build React app with Vite
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (production + dev for build)
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY . .

# Build application
RUN npm run build

# STAGE 2: Serve with Nginx
FROM nginx:1.27-alpine

# Build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Labels
LABEL org.opencontainers.image.title="The Feed — Frontend" \
      org.opencontainers.image.description="AI-powered media platform frontend (React + Typescript)" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="${VERSION}"

# Security: Install security updates
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache ca-certificates curl tzdata && \
    update-ca-certificates && \
    rm -rf /var/cache/apk/*

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Expose port
EXPOSE 80

# Run as non-root
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
