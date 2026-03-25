#!/bin/sh

DB_PASSWORD=$(cat /run/secrets/db_password 2>/dev/null || echo "userpassword")
WP_ADMIN_PASSWORD=$(cat /run/secrets/credentials 2>/dev/null || echo "adminpassword")
WP_USER_PASSWORD=$(cat /run/secrets/credentials 2>/dev/null || echo "userpassword")

mkdir -p /var/log/php83
chown nobody:nobody /var/log/php83

echo "Waiting for MariaDB to be ready..."
max_tries=30
counter=0
while ! mysqladmin ping -h "${MYSQL_HOST:-mariadb}" --silent 2>/dev/null; do
    counter=$((counter + 1))
    if [ $counter -ge $max_tries ]; then
        echo "ERROR: MariaDB did not become ready in time!"
        exit 1
    fi
    echo "Waiting for MariaDB... ($counter/$max_tries)"
    sleep 2
done
echo "MariaDB is ready!"

cd /var/www/html

if [ -f "wp-config.php" ]; then
    echo "WordPress already configured."
else
    echo "Downloading WordPress..."
    curl -O https://wordpress.org/latest.tar.gz
    tar -xzf latest.tar.gz
    mv wordpress/* .
    rm -rf wordpress latest.tar.gz
    
    echo "Creating wp-config.php..."
    cp wp-config-sample.php wp-config.php
    
    sed -i "s/database_name_here/${MYSQL_DATABASE}/" wp-config.php
    sed -i "s/username_here/${MYSQL_USER}/" wp-config.php
    sed -i "s/password_here/${DB_PASSWORD}/" wp-config.php
    sed -i "s/localhost/${MYSQL_HOST:-mariadb}/" wp-config.php
    
    echo "WordPress configuration created!"
fi
chown -R nobody:nobody /var/www/html

echo "Starting PHP-FPM..."
exec php-fpm83 -F
