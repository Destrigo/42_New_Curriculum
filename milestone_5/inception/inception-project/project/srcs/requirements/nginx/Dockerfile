# =============================================================================
# NGINX Dockerfile for Inception Project
# =============================================================================
# Using Alpine 3.19 (penultimate stable as of 2024)

FROM alpine:3.19

# Install NGINX and OpenSSL for TLS
RUN apk update && apk add --no-cache \
    nginx \
    openssl \
    && rm -rf /var/cache/apk/*

# Create necessary directories
RUN mkdir -p /var/www/html \
    && mkdir -p /etc/nginx/ssl \
    && mkdir -p /run/nginx

# Copy configuration file
COPY conf/nginx.conf /etc/nginx/nginx.conf

# Copy and set up SSL generation script
COPY tools/setup-ssl.sh /usr/local/bin/setup-ssl.sh
RUN chmod +x /usr/local/bin/setup-ssl.sh

# Expose HTTPS port only
EXPOSE 443

# Generate SSL certificates and start NGINX
# NGINX runs in foreground (-g 'daemon off;') to be PID 1
CMD ["/bin/sh", "-c", "/usr/local/bin/setup-ssl.sh && nginx -g 'daemon off;'"]
