# Inception Project - Complete Guide

*This guide provides detailed instructions for completing the 42 Inception project.*

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Understanding](#architecture-understanding)
3. [Prerequisites](#prerequisites)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [File Structure](#file-structure)
6. [Configuration Details](#configuration-details)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)

---

## Project Overview

The Inception project requires you to set up a small infrastructure composed of:
- **NGINX** container with TLS (port 443 only)
- **WordPress + PHP-FPM** container
- **MariaDB** container
- **Two Docker volumes** for database and WordPress files
- **Docker network** connecting all containers

### Key Rules to Remember

1. **No ready-made images** - You must write your own Dockerfiles
2. **No `latest` tag** - Always specify versions
3. **No passwords in Dockerfiles** - Use environment variables and secrets
4. **No infinite loops** - Don't use `tail -f`, `sleep infinity`, `while true`
5. **No `network: host`** or `--link` - Use Docker networks
6. **Penultimate stable version** of Alpine or Debian only
7. **Named volumes only** - No bind mounts for persistent data
8. **Containers must auto-restart** on crash

---

## Architecture Understanding

```
                    Internet
                        │
                        │ Port 443 (HTTPS)
                        ▼
    ┌──────────────────────────────────────────────────┐
    │                  HOST MACHINE                     │
    │  ┌────────────────────────────────────────────┐  │
    │  │            Docker Network                   │  │
    │  │                                            │  │
    │  │  ┌──────────┐    ┌──────────┐    ┌──────┐ │  │
    │  │  │  NGINX   │◄──►│WordPress │◄──►│Maria │ │  │
    │  │  │  :443    │9000│ PHP-FPM  │3306│  DB  │ │  │
    │  │  └──────────┘    └────┬─────┘    └──┬───┘ │  │
    │  │                       │             │      │  │
    │  └───────────────────────┼─────────────┼──────┘  │
    │                          │             │         │
    │                     ┌────┴────┐   ┌────┴────┐   │
    │                     │WordPress│   │Database │   │
    │                     │ Volume  │   │ Volume  │   │
    │                     └────┬────┘   └────┬────┘   │
    │                          │             │         │
    │              /home/login/data/wordpress │        │
    │              /home/login/data/mariadb ──┘        │
    └──────────────────────────────────────────────────┘
```

### How It Works

1. **User requests `https://login.42.fr`**
2. **NGINX** receives the request on port 443 with TLS
3. **NGINX** proxies PHP requests to WordPress container on port 9000
4. **WordPress/PHP-FPM** processes the request
5. **WordPress** queries **MariaDB** on port 3306 for data
6. Response travels back through the chain

---

## Prerequisites

### On Your Virtual Machine

1. **Install Docker and Docker Compose**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER

# Apply group changes (or logout/login)
newgrp docker
```

2. **Configure /etc/hosts**
```bash
# Add your domain to hosts file (replace 'login' with your username)
echo "127.0.0.1 login.42.fr" | sudo tee -a /etc/hosts
```

3. **Create data directories**
```bash
# Replace 'login' with your actual username
mkdir -p /home/login/data/wordpress
mkdir -p /home/login/data/mariadb
```

---

## Step-by-Step Setup

### Step 1: Create Project Structure

```bash
mkdir -p inception
cd inception
mkdir -p srcs/requirements/{nginx,wordpress,mariadb}/{conf,tools}
mkdir -p secrets
```

### Step 2: Create Secrets

Create files in the `secrets/` directory:

```bash
# Generate secure passwords
echo "your_db_password_here" > secrets/db_password.txt
echo "your_db_root_password_here" > secrets/db_root_password.txt
echo "wp_user_password" > secrets/credentials.txt
```

### Step 3: Create Environment File

The `.env` file goes in `srcs/`:

```bash
# srcs/.env
DOMAIN_NAME=login.42.fr
MYSQL_HOST=mariadb
MYSQL_DATABASE=wordpress
MYSQL_USER=wpuser
WP_TITLE=Inception
WP_ADMIN_USER=boss
WP_ADMIN_EMAIL=boss@login.42.fr
WP_USER=author
WP_USER_EMAIL=author@login.42.fr
```

### Step 4: Build Each Service

See the detailed configuration sections below for each Dockerfile and configuration file.

### Step 5: Run the Project

```bash
make        # Build and start all containers
make stop   # Stop containers
make clean  # Remove containers and images
make fclean # Remove everything including volumes
```

---

## File Structure

```
inception/
├── Makefile
├── README.md
├── USER_DOC.md
├── DEV_DOC.md
├── secrets/
│   ├── credentials.txt
│   ├── db_password.txt
│   └── db_root_password.txt
└── srcs/
    ├── .env
    ├── docker-compose.yml
    └── requirements/
        ├── mariadb/
        │   ├── Dockerfile
        │   ├── .dockerignore
        │   ├── conf/
        │   │   └── 50-server.cnf
        │   └── tools/
        │       └── init-db.sh
        ├── nginx/
        │   ├── Dockerfile
        │   ├── .dockerignore
        │   ├── conf/
        │   │   └── nginx.conf
        │   └── tools/
        │       └── setup-ssl.sh
        └── wordpress/
            ├── Dockerfile
            ├── .dockerignore
            ├── conf/
            │   └── www.conf
            └── tools/
                └── setup-wp.sh
```

---

## Configuration Details

### Understanding Each Component

#### MariaDB Container
- Runs the MySQL-compatible database server
- Listens on port 3306 (internal network only)
- Data persists in the `mariadb` volume
- Initializes database and users on first run

#### WordPress Container
- Runs PHP-FPM to process PHP files
- Listens on port 9000 for FastCGI connections
- WordPress files stored in the `wordpress` volume
- Connects to MariaDB for data storage

#### NGINX Container
- Reverse proxy and web server
- Only container exposed to outside (port 443)
- Handles TLS termination
- Proxies PHP requests to WordPress container

---

## Testing & Validation

### Basic Tests

1. **Check containers are running**
```bash
docker ps
# Should show 3 containers: nginx, wordpress, mariadb
```

2. **Test HTTPS connection**
```bash
curl -k https://login.42.fr
# Should return WordPress HTML
```

3. **Check TLS version**
```bash
openssl s_client -connect login.42.fr:443 -tls1_2
openssl s_client -connect login.42.fr:443 -tls1_3
# Both should work

openssl s_client -connect login.42.fr:443 -tls1_1
# Should fail (older TLS not allowed)
```

4. **Test database connection**
```bash
docker exec -it mariadb mysql -u wpuser -p wordpress
# Enter password from secrets, should connect
```

5. **Check volumes**
```bash
docker volume ls
# Should show your named volumes

ls /home/login/data/wordpress
ls /home/login/data/mariadb
# Should contain data
```

6. **Test container restart**
```bash
docker kill wordpress
docker ps
# After a moment, wordpress should restart automatically
```

### WordPress Validation

1. Navigate to `https://login.42.fr`
2. Complete WordPress installation if first time
3. Log in as admin (username cannot contain "admin")
4. Create second user account
5. Verify posts/pages work correctly

---

## Troubleshooting

### Common Issues

**Container won't start**
```bash
docker logs <container_name>
# Check for error messages
```

**Permission denied errors**
```bash
# Ensure data directories have correct permissions
sudo chown -R 1000:1000 /home/login/data/
```

**Can't connect to database**
- Verify MariaDB container is running
- Check environment variables match
- Ensure secrets are being read correctly

**SSL certificate errors**
- Certificates must be generated inside the container
- Verify certificate paths in nginx.conf

**"Connection refused" on port 443**
- Check NGINX container is running
- Verify port 443 is exposed in docker-compose.yml
- Check firewall settings on VM

**WordPress shows "Error establishing database connection"**
- Verify MariaDB is running and healthy
- Check database credentials
- Ensure WordPress can reach MariaDB on the network

### Useful Debug Commands

```bash
# View all container logs
docker compose -f srcs/docker-compose.yml logs

# Enter a container
docker exec -it nginx sh
docker exec -it wordpress sh
docker exec -it mariadb sh

# Check network connectivity
docker exec wordpress ping mariadb

# Inspect network
docker network inspect inception_network

# Check volume contents
docker volume inspect inception_wordpress
docker volume inspect inception_mariadb
```

---

## Security Best Practices

1. **Never commit secrets to git** - Add `secrets/` and `.env` to `.gitignore`
2. **Use strong passwords** - Generate random passwords for all services
3. **Keep images updated** - Use specific version tags, update regularly
4. **Minimize container privileges** - Don't run as root when possible
5. **Use Docker secrets** - Better than environment variables for sensitive data

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [NGINX Documentation](https://nginx.org/en/docs/)
- [WordPress Installation](https://wordpress.org/support/article/how-to-install-wordpress/)
- [MariaDB Documentation](https://mariadb.com/kb/en/documentation/)
- [PHP-FPM Configuration](https://www.php.net/manual/en/install.fpm.php)
