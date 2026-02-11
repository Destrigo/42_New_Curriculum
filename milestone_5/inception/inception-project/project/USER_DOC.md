# User Documentation - Inception

This document explains how to use and manage the Inception WordPress infrastructure.

## Services Overview

The Inception stack provides a complete WordPress website with the following services:

| Service | Description | Access |
|---------|-------------|--------|
| **NGINX** | Web server handling HTTPS requests | https://login.42.fr |
| **WordPress** | Content management system | Via NGINX |
| **MariaDB** | Database storing WordPress data | Internal only |

## Starting and Stopping the Project

### Start the Project

```bash
# From the project root directory
make
```

This command will:
1. Create necessary data directories
2. Build all Docker images
3. Start all containers

### Stop the Project

```bash
# Stop containers (keeps data)
make stop

# Stop and remove containers (keeps data)
make down
```

### Restart the Project

```bash
# Stop and start
make down && make up

# Complete rebuild
make re
```

## Accessing the Website

### Main Website

1. Open your web browser
2. Navigate to `https://login.42.fr` (replace 'login' with the configured username)
3. Accept the security warning (self-signed certificate)

### WordPress Administration Panel

1. Go to `https://login.42.fr/wp-admin`
2. Log in with administrator credentials

**Default Admin Account**:
- Username: `boss` (or as configured in `.env`)
- Password: Found in `secrets/credentials.txt`

### Creating Content

1. Log in to the admin panel
2. Navigate to Posts → Add New
3. Create your content
4. Click Publish

## Managing Credentials

### Where Credentials Are Stored

| Credential | Location |
|------------|----------|
| Database password | `secrets/db_password.txt` |
| Database root password | `secrets/db_root_password.txt` |
| WordPress user password | `secrets/credentials.txt` |
| Domain name | `srcs/.env` |
| WordPress admin username | `srcs/.env` |

### Changing Passwords

**Important**: Changing passwords after initial setup requires additional steps.

1. Stop the containers: `make stop`
2. Update the password in the relevant secret file
3. For database passwords, you may need to update them in MariaDB manually
4. Restart: `make up`

### WordPress User Management

1. Log in to WordPress admin panel
2. Go to Users → All Users
3. Add, edit, or remove users as needed

## Checking Service Status

### Quick Status Check

```bash
make status
```

This shows all container states.

### Detailed Health Check

```bash
make health
```

This tests each service individually.

### Viewing Logs

```bash
# All logs
make logs

# Specific service
make logs-nginx
make logs-wordpress
make logs-mariadb
```

### Entering Containers (Advanced)

For troubleshooting, you can enter containers:

```bash
make shell-nginx
make shell-wordpress
make shell-mariadb
```

## Data Persistence

Your data is stored in two locations:

| Data Type | Host Location |
|-----------|--------------|
| WordPress files | `/home/login/data/wordpress` |
| Database files | `/home/login/data/mariadb` |

**Backing up data**:
```bash
# Stop services first
make stop

# Copy data
cp -r /home/login/data/wordpress ~/backup/wordpress
cp -r /home/login/data/mariadb ~/backup/mariadb
```

## Troubleshooting

### Website Not Loading

1. Check if containers are running: `make status`
2. View logs for errors: `make logs`
3. Verify /etc/hosts has the domain entry

### Can't Log In to WordPress

1. Verify credentials in `secrets/credentials.txt`
2. Try resetting password via WP-CLI:
   ```bash
   docker exec wordpress wp user update boss --user_pass=newpassword --allow-root
   ```

### Database Connection Error

1. Check MariaDB is running: `docker ps | grep mariadb`
2. View MariaDB logs: `make logs-mariadb`
3. Verify database credentials match between services

### SSL Certificate Warning

This is expected behavior with self-signed certificates. Click "Advanced" and "Proceed" to continue.

## Security Notes

- Keep the `secrets/` directory secure
- Never commit secrets to version control
- Use strong, unique passwords
- Regularly update containers for security patches

## Getting Help

If you encounter issues:

1. Check the logs: `make logs`
2. Review this documentation
3. Consult the [README.md](README.md) for technical details
4. Check the [DEV_DOC.md](DEV_DOC.md) for developer information
