# User Documentation - Inception

## Services Overview

| Service | Description | Port |
|---------|-------------|------|
| NGINX | Web server with HTTPS | 443 |
| WordPress | Content management | via NGINX |
| MariaDB | Database | internal |

## Starting and Stopping

```bash
make        # Build and start all services
make stop   # Stop containers
make down   # Stop and remove containers
make re     # Rebuild from scratch
```

## Accessing the Website

1. Open your browser
2. Go to `https://localhost` (or `https://login.42.fr` if configured)
3. Accept the certificate warning (self-signed certificate)

## Admin Panel

- URL: `https://localhost/wp-admin`
- Username: `boss`
- Password: Check `secrets/credentials.txt`

## Second User

- Username: `author`
- Password: Same as admin (from `secrets/credentials.txt`)

## Checking Status

```bash
make status   # Show container status
make logs     # View all logs
```

## Data Persistence

Data is stored in:
- `~/data/wordpress/` - WordPress files
- `~/data/mariadb/` - Database files

Data persists between container restarts.

## Troubleshooting

**Containers not starting?**
```bash
make logs
```

**Database connection error?**
Wait 30 seconds for MariaDB to initialize on first run.

**Certificate warning?**
Normal - the certificate is self-signed for development.
