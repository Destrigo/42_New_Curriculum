# =============================================================================
# MariaDB Dockerfile for Inception Project
# =============================================================================
# Using Alpine 3.19 (penultimate stable as of 2024)

FROM alpine:3.19

# Install MariaDB
RUN apk update && apk add --no-cache \
    mariadb \
    mariadb-client \
    mariadb-common \
    && rm -rf /var/cache/apk/*

# Create necessary directories and set permissions
RUN mkdir -p /var/lib/mysql /var/run/mysqld /var/log/mysql \
    && chown -R mysql:mysql /var/lib/mysql /var/run/mysqld /var/log/mysql \
    && chmod 755 /var/run/mysqld

# Copy custom configuration
COPY conf/50-server.cnf /etc/my.cnf.d/50-server.cnf

# Copy initialization script
COPY tools/init-db.sh /usr/local/bin/init-db.sh
RUN chmod +x /usr/local/bin/init-db.sh

# Expose MySQL port (only accessible within Docker network)
EXPOSE 3306

# Run initialization script which starts MariaDB
CMD ["/usr/local/bin/init-db.sh"]
