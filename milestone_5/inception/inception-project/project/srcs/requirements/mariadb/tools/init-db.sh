#!/bin/sh
# =============================================================================
# MariaDB Initialization Script for Inception Project
# =============================================================================

# Read passwords from Docker secrets
DB_ROOT_PASSWORD=$(cat /run/secrets/db_root_password 2>/dev/null || echo "rootpassword")
DB_PASSWORD=$(cat /run/secrets/db_password 2>/dev/null || echo "userpassword")

# Check if database already initialized
if [ -d "/var/lib/mysql/mysql" ]; then
    echo "Database already initialized. Starting MariaDB..."
else
    echo "Initializing MariaDB database..."
    
    # Initialize MySQL data directory
    mysql_install_db --user=mysql --datadir=/var/lib/mysql --skip-test-db
    
    echo "Starting temporary MariaDB server for initialization..."
    
    # Start MariaDB temporarily for setup
    mysqld --user=mysql --bootstrap << EOF
-- Set root password
USE mysql;
FLUSH PRIVILEGES;

-- Update root user authentication
ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}';

-- Create database for WordPress
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Create application user
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';

-- Grant privileges to application user
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';

-- Also create user for localhost connections
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'localhost';

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove remote root access
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Remove test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- Apply changes
FLUSH PRIVILEGES;
EOF

    if [ $? -eq 0 ]; then
        echo "Database initialization complete!"
        echo "Database: ${MYSQL_DATABASE}"
        echo "User: ${MYSQL_USER}"
    else
        echo "ERROR: Database initialization failed!"
        exit 1
    fi
fi

echo "Starting MariaDB server..."

# Start MariaDB in foreground (PID 1)
# Using exec replaces the shell process with mysqld
exec mysqld --user=mysql --console
