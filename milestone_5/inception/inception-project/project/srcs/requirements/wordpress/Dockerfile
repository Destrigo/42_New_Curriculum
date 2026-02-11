# =============================================================================
# WordPress + PHP-FPM Dockerfile for Inception Project
# =============================================================================
# Using Alpine 3.19 (penultimate stable as of 2024)

FROM alpine:3.19

# Install PHP-FPM and required extensions for WordPress
RUN apk update && apk add --no-cache \
    php83 \
    php83-fpm \
    php83-mysqli \
    php83-json \
    php83-curl \
    php83-dom \
    php83-exif \
    php83-fileinfo \
    php83-mbstring \
    php83-openssl \
    php83-xml \
    php83-zip \
    php83-gd \
    php83-iconv \
    php83-intl \
    php83-phar \
    php83-soap \
    php83-xmlreader \
    php83-opcache \
    php83-tokenizer \
    php83-ctype \
    php83-session \
    php83-simplexml \
    php83-pecl-redis \
    curl \
    mariadb-client \
    && rm -rf /var/cache/apk/*

# Create PHP symlink for wp-cli
RUN ln -sf /usr/bin/php83 /usr/bin/php

# Install WP-CLI
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp

# Create necessary directories
RUN mkdir -p /var/www/html \
    && mkdir -p /run/php

# Copy PHP-FPM configuration
COPY conf/www.conf /etc/php83/php-fpm.d/www.conf

# Copy WordPress setup script
COPY tools/setup-wp.sh /usr/local/bin/setup-wp.sh
RUN chmod +x /usr/local/bin/setup-wp.sh

# Set working directory
WORKDIR /var/www/html

# Change ownership to nobody (PHP-FPM user)
RUN chown -R nobody:nobody /var/www/html

# Expose PHP-FPM port
EXPOSE 9000

# Run setup script and start PHP-FPM
CMD ["/usr/local/bin/setup-wp.sh"]
