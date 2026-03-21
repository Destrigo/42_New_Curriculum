FROM alpine:3.19

RUN apk update && apk add --no-cache \
    nginx \
    openssl \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /var/www/html \
    && mkdir -p /etc/nginx/ssl \
    && mkdir -p /run/nginx

COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY tools/setup-ssl.sh /usr/local/bin/setup-ssl.sh
RUN chmod +x /usr/local/bin/setup-ssl.sh

EXPOSE 443

CMD ["/bin/sh", "-c", "/usr/local/bin/setup-ssl.sh && nginx -g 'daemon off;'"]
