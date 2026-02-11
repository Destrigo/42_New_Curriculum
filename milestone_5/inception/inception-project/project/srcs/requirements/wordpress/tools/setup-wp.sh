#!/bin/sh
# =============================================================================
# WordPress Setup Script for Inception Project
# =============================================================================

# Read passwords from Docker secrets
DB_PASSWORD=$(cat /run/secrets/db_password 2>/dev/null || echo "userpassword")
WP_ADMIN_PASSWORD=$(cat /run/secrets/credentials 2>/dev/null || echo "adminpassword")
WP_USER_PASSWORD=$(cat /run/secrets/credentials 2>/dev/null || echo "userpassword")

# Create log directory
mkdir -p /var/log/php83
chown nobody:nobody /var/log/php83

# Wait for MariaDB to be ready
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

# Change to web root
cd /var/www/html

# Check if WordPress is already installed
if [ -f "wp-config.php" ]; then
    echo "WordPress already configured. Checking installation..."
else
    echo "Downloading WordPress..."
    
    # Download WordPress
    wp core download --allow-root --path=/var/www/html
    
    echo "Creating wp-config.php..."
    
    # Create wp-config.php
    wp config create --allow-root \
        --dbname="${MYSQL_DATABASE}" \
        --dbuser="${MYSQL_USER}" \
        --dbpass="${DB_PASSWORD}" \
        --dbhost="${MYSQL_HOST:-mariadb}" \
        --dbcharset="utf8mb4" \
        --dbcollate="utf8mb4_general_ci" \
        --path=/var/www/html
    
    # Add additional configuration
    wp config set WP_DEBUG false --raw --allow-root
    wp config set WP_DEBUG_LOG false --raw --allow-root
    wp config set WP_DEBUG_DISPLAY false --raw --allow-root
    wp config set DISALLOW_FILE_EDIT true --raw --allow-root
    
    echo "WordPress configuration created!"
fi

# Check if WordPress is installed (database tables exist)
if wp core is-installed --allow-root 2>/dev/null; then
    echo "WordPress is already installed."
else
    echo "Installing WordPress..."
    
    # Install WordPress
    wp core install --allow-root \
        --url="https://${DOMAIN_NAME}" \
        --title="${WP_TITLE:-Inception}" \
        --admin_user="${WP_ADMIN_USER:-boss}" \
        --admin_password="${WP_ADMIN_PASSWORD}" \
        --admin_email="${WP_ADMIN_EMAIL:-admin@example.com}" \
        --skip-email
    
    echo "WordPress installed successfully!"
    
    # Create second user (regular author)
    echo "Creating additional user..."
    wp user create "${WP_USER:-author}" "${WP_USER_EMAIL:-user@example.com}" \
        --role=author \
        --user_pass="${WP_USER_PASSWORD}" \
        --allow-root
    
    echo "Second user created!"
    
    # Update permalink structure
    wp rewrite structure '/%postname%/' --allow-root
    
    # Install and activate a theme (optional, uses default)
    echo "WordPress setup complete!"
    echo "Admin user: ${WP_ADMIN_USER:-boss}"
    echo "Regular user: ${WP_USER:-author}"
fi

# Set proper ownership
chown -R nobody:nobody /var/www/html

echo "Starting PHP-FPM..."

# Start PHP-FPM in foreground (PID 1)
exec php-fpm83 -F
