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
    wp core download --allow-root --path=/var/www/html
    
    echo "Creating wp-config.php..."
    wp config create --allow-root \
        --dbname="${MYSQL_DATABASE}" \
        --dbuser="${MYSQL_USER}" \
        --dbpass="${DB_PASSWORD}" \
        --dbhost="${MYSQL_HOST:-mariadb}" \
        --dbcharset="utf8mb4" \
        --dbcollate="utf8mb4_general_ci" \
        --path=/var/www/html
    
    wp config set WP_DEBUG false --raw --allow-root
    wp config set WP_DEBUG_LOG false --raw --allow-root
    wp config set DISALLOW_FILE_EDIT true --raw --allow-root
    
    echo "WordPress configuration created!"
fi

if wp core is-installed --allow-root 2>/dev/null; then
    echo "WordPress is already installed."
else
    echo "Installing WordPress..."
    
    wp core install --allow-root \
        --url="https://${DOMAIN_NAME}" \
        --title="${WP_TITLE:-Inception}" \
        --admin_user="${WP_ADMIN_USER:-boss}" \
        --admin_password="${WP_ADMIN_PASSWORD}" \
        --admin_email="${WP_ADMIN_EMAIL:-admin@example.com}" \
        --skip-email
    
    echo "Creating additional user..."
    wp user create "${WP_USER:-author}" "${WP_USER_EMAIL:-user@example.com}" \
        --role=author \
        --user_pass="${WP_USER_PASSWORD}" \
        --allow-root
    
    wp rewrite structure '/%postname%/' --allow-root
    
    echo "WordPress installation complete!"
    echo "Admin: ${WP_ADMIN_USER:-boss}"
    echo "User: ${WP_USER:-author}"
fi

chown -R nobody:nobody /var/www/html

echo "Starting PHP-FPM..."
exec php-fpm83 -F
