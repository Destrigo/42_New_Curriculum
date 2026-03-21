FROM alpine:3.19

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
    php83-session \
    php83-simplexml \
    php83-ctype \
    php83-tokenizer \
    php83-opcache \
    curl \
    mariadb-client \
    && rm -rf /var/cache/apk/*

RUN ln -sf /usr/bin/php83 /usr/bin/php

RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp

RUN mkdir -p /var/www/html /run/php /var/log/php83

COPY conf/www.conf /etc/php83/php-fpm.d/www.conf
COPY tools/setup-wp.sh /usr/local/bin/setup-wp.sh
RUN chmod +x /usr/local/bin/setup-wp.sh

WORKDIR /var/www/html
RUN chown -R nobody:nobody /var/www/html /var/log/php83

EXPOSE 9000

CMD ["/usr/local/bin/setup-wp.sh"]
