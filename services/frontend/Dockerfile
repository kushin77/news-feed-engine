# Frontend \u2014 AI Media Platform
# nginx:alpine serving static HTML/CSS/JS

FROM nginx:1.27-alpine

# Build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

LABEL org.opencontainers.image.title="The Feed \u2014 Frontend" \
      org.opencontainers.image.description="AI-powered media platform landing page" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="${VERSION}"

# Security: Install security updates
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache ca-certificates curl tzdata && \
    update-ca-certificates && \
    rm -rf /var/cache/apk/*

# Remove default nginx content and config
RUN rm -rf /usr/share/nginx/html/* && \
    rm -f /etc/nginx/conf.d/default.conf

# Copy static frontend files
COPY index.html       /usr/share/nginx/html/index.html
COPY products.html    /usr/share/nginx/html/products.html
COPY marketing.html   /usr/share/nginx/html/marketing.html
COPY news-feed.html   /usr/share/nginx/html/news-feed.html
COPY manifest.json    /usr/share/nginx/html/manifest.json
COPY sw.js            /usr/share/nginx/html/sw.js

# Copy nginx configuration
COPY nginx-main.conf /etc/nginx/nginx.conf
COPY nginx.conf      /etc/nginx/conf.d/default.conf

# Set file permissions
RUN chown -R nginx:nginx /usr/share/nginx/html /etc/nginx/conf.d && \
    chmod 644 /usr/share/nginx/html/*.html \
              /usr/share/nginx/html/manifest.json \
              /usr/share/nginx/html/sw.js && \
    mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp \
             /run/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx /run/nginx && \
    chmod -R 755 /var/cache/nginx /var/run /var/log/nginx /run/nginx

# nginx.conf listens on 8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["curl", "-f", "http://127.0.0.1:8080/health"]

USER nginx

CMD ["nginx", "-g", "daemon off;"]
