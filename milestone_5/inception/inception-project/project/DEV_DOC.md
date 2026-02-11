# Developer Documentation - Inception

This document provides technical information for developers working on or maintaining the Inception project.

## Environment Setup

### Prerequisites

Before starting, ensure you have:

- **Operating System**: Debian 11/12 or Ubuntu 22.04 LTS (in a VM)
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (plugin version)
- **Git**: For version control
- **Text Editor**: vim, nano, or your preferred editor

### Installing Docker

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/debian $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

### Configuring the Environment

1. **Clone the repository**:
```bash
git clone <repository-url> inception
cd inception
```

2. **Set up your username**:
```bash
# Replace 'login' with your 42 username in all files
export MY_LOGIN="your_login_here"

# Update .env file
sed -i "s/login/${MY_LOGIN}/g" srcs/.env

# Update /etc/hosts
echo "127.0.0.1 ${MY_LOGIN}.42.fr" | sudo tee -a /etc/hosts
```

3. **Create secure secrets**:
```bash
# Generate random passwords
openssl rand -base64 32 > secrets/db_password.txt
openssl rand -base64 32 > secrets/db_root_password.txt
openssl rand -base64 24 > secrets/credentials.txt

# Secure the files
chmod 600 secrets/*.txt
```

4. **Create data directories**:
```bash
sudo mkdir -p /home/${MY_LOGIN}/data/wordpress
sudo mkdir -p /home/${MY_LOGIN}/data/mariadb
sudo chown -R $USER:$USER /home/${MY_LOGIN}/data
```

## Building and Launching

### Using the Makefile

The Makefile provides all necessary commands:

| Command | Description |
|---------|-------------|
| `make` / `make all` | Setup, build, and start |
| `make build` | Build images only |
| `make up` | Start containers |
| `make up-logs` | Start with visible logs |
| `make stop` | Stop containers |
| `make down` | Stop and remove containers |
| `make clean` | Remove containers and images |
| `make fclean` | Remove everything including data |
| `make re` | Full rebuild |

### Manual Docker Compose Commands

If you need more control:

```bash
# Build images
docker compose -f srcs/docker-compose.yml --env-file srcs/.env build

# Start services
docker compose -f srcs/docker-compose.yml --env-file srcs/.env up -d

# View logs
docker compose -f srcs/docker-compose.yml --env-file srcs/.env logs -f

# Stop services
docker compose -f srcs/docker-compose.yml --env-file srcs/.env down
```

## Container Management

### Accessing Containers

```bash
# Enter NGINX container
docker exec -it nginx sh

# Enter WordPress container
docker exec -it wordpress sh

# Enter MariaDB container
docker exec -it mariadb sh

# Access MariaDB CLI
docker exec -it mariadb mysql -u wpuser -p wordpress
```

### Useful Commands

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs nginx
docker logs wordpress
docker logs mariadb

# Inspect container
docker inspect nginx

# View network details
docker network inspect inception_network

# List volumes
docker volume ls

# Inspect volume
docker volume inspect inception_wordpress
```

## Data Storage

### Volume Configuration

The project uses named volumes with local driver bindings:

```yaml
volumes:
  wordpress:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/${USER}/data/wordpress

  mariadb:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/${USER}/data/mariadb
```

### Data Locations

| Data | Container Path | Host Path |
|------|---------------|-----------|
| WordPress files | `/var/www/html` | `/home/login/data/wordpress` |
| MariaDB data | `/var/lib/mysql` | `/home/login/data/mariadb` |

### Backup Procedures

```bash
# Stop services
make stop

# Backup WordPress files
tar -czvf wordpress-backup.tar.gz -C /home/login/data/wordpress .

# Backup database files
tar -czvf mariadb-backup.tar.gz -C /home/login/data/mariadb .

# Alternative: MySQL dump
docker exec mariadb mysqldump -u root -p wordpress > wordpress.sql
```

### Restore Procedures

```bash
# Stop services
make stop

# Restore WordPress files
tar -xzvf wordpress-backup.tar.gz -C /home/login/data/wordpress

# Restore database files
tar -xzvf mariadb-backup.tar.gz -C /home/login/data/mariadb

# Restart
make up
```

## Project Structure

```
inception/
├── Makefile                    # Build automation
├── README.md                   # Project overview
├── USER_DOC.md                 # User documentation
├── DEV_DOC.md                  # Developer documentation
├── secrets/                    # Docker secrets (not in git)
│   ├── db_password.txt         # Database user password
│   ├── db_root_password.txt    # Database root password
│   └── credentials.txt         # WordPress passwords
└── srcs/
    ├── .env                    # Environment variables
    ├── docker-compose.yml      # Service definitions
    └── requirements/
        ├── nginx/
        │   ├── Dockerfile      # NGINX image
        │   ├── conf/
        │   │   └── nginx.conf  # NGINX configuration
        │   └── tools/
        │       └── setup-ssl.sh # SSL certificate generation
        ├── wordpress/
        │   ├── Dockerfile      # WordPress/PHP-FPM image
        │   ├── conf/
        │   │   └── www.conf    # PHP-FPM pool configuration
        │   └── tools/
        │       └── setup-wp.sh # WordPress installation script
        └── mariadb/
            ├── Dockerfile      # MariaDB image
            ├── conf/
            │   └── 50-server.cnf # MariaDB configuration
            └── tools/
                └── init-db.sh  # Database initialization script
```

## Debugging

### Common Issues and Solutions

**1. Container fails to start**
```bash
# Check logs
docker logs <container_name>

# Check if port is in use
sudo netstat -tlnp | grep 443
sudo netstat -tlnp | grep 3306
```

**2. Permission denied on volumes**
```bash
# Fix ownership
sudo chown -R 1000:1000 /home/login/data/wordpress
sudo chown -R 999:999 /home/login/data/mariadb
```

**3. Database connection failed**
```bash
# Test from WordPress container
docker exec wordpress ping mariadb
docker exec wordpress mysql -h mariadb -u wpuser -p

# Check MariaDB is accepting connections
docker exec mariadb mysqladmin -u root -p status
```

**4. NGINX 502 Bad Gateway**
```bash
# Check WordPress/PHP-FPM is running
docker exec wordpress ps aux | grep php-fpm
docker exec wordpress php-fpm83 -t

# Check connectivity
docker exec nginx ping wordpress
```

**5. SSL Certificate errors**
```bash
# Regenerate certificates
docker exec nginx /usr/local/bin/setup-ssl.sh
docker exec nginx nginx -s reload
```

### Testing TLS Configuration

```bash
# Test TLS 1.2
openssl s_client -connect login.42.fr:443 -tls1_2

# Test TLS 1.3
openssl s_client -connect login.42.fr:443 -tls1_3

# Test TLS 1.1 (should fail)
openssl s_client -connect login.42.fr:443 -tls1_1

# View certificate details
openssl s_client -connect login.42.fr:443 -showcerts
```

## Best Practices

### Security

1. Never commit secrets to git - add to `.gitignore`
2. Use strong, randomly generated passwords
3. Keep base images updated
4. Don't run containers as root when possible
5. Limit network exposure (only port 443)

### Performance

1. Use multi-stage builds for smaller images
2. Leverage Docker layer caching
3. Configure PHP OPcache (already done)
4. Use appropriate resource limits in compose file

### Maintenance

1. Regularly update base images
2. Monitor logs for errors
3. Back up data before updates
4. Test changes in development first

## Additional Resources

### Docker
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Networking](https://docs.docker.com/network/)

### Services
- [NGINX Admin Guide](https://docs.nginx.com/nginx/admin-guide/)
- [PHP-FPM Configuration](https://www.php.net/manual/en/install.fpm.configuration.php)
- [MariaDB Configuration](https://mariadb.com/kb/en/configuring-mariadb-with-option-files/)
- [WP-CLI Commands](https://developer.wordpress.org/cli/commands/)
