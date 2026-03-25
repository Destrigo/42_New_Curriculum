FROM alpine:3.19

RUN apk update && apk add --no-cache \
    mariadb \
    mariadb-client \
    mariadb-common \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /var/lib/mysql /var/run/mysqld /var/log/mysql \
    && chown -R mysql:mysql /var/lib/mysql /var/run/mysqld /var/log/mysql \
    && chmod 755 /var/run/mysqld

COPY conf/50-server.cnf /etc/my.cnf.d/50-server.cnf
RUN sed -i 's/skip-networking/#skip-networking/' /etc/my.cnf.d/mariadb-server.cnf

COPY tools/init-db.sh /usr/local/bin/init-db.sh
RUN chmod +x /usr/local/bin/init-db.sh

EXPOSE 3306

CMD ["/usr/local/bin/init-db.sh"]
