*This project has been created as part of the 42 curriculum by login.*

# Inception

Docker-based infrastructure with NGINX, WordPress + PHP-FPM, and MariaDB.

## Description

This project sets up a small web infrastructure using Docker containers:

- **NGINX**: Web server with TLSv1.2/TLSv1.3 (port 443)
- **WordPress + PHP-FPM**: Content management system
- **MariaDB**: Database server

All services run in isolated containers connected via a Docker network, with persistent data stored in Docker volumes.

## Instructions

### Prerequisites

- Docker and Docker Compose installed
- No sudo required if Docker is pre-configured

### Quick Start

```bash
# 1. Edit srcs/.env - replace 'login' with your username
# 2. Edit secrets/*.txt - set secure passwords
# 3. Run:
make
```

### Access

- Website: https://localhost
- Admin: https://localhost/wp-admin
- Username: boss
- Password: (see secrets/credentials.txt)

## Project Description

### Virtual Machines vs Docker

| VM | Docker |
|---|---|
| Full OS, heavy | Shared kernel, lightweight |
| Minutes to boot | Seconds to start |
| GB of RAM | MB of RAM |

### Secrets vs Environment Variables

| Env Vars | Secrets |
|---|---|
| Visible in inspect | Encrypted in memory |
| For non-sensitive config | For passwords |

### Docker Network vs Host Network

| Docker Network | Host Network |
|---|---|
| Isolated | No isolation |
| Container DNS | Direct host access |

### Docker Volumes vs Bind Mounts

| Named Volumes | Bind Mounts |
|---|---|
| Docker-managed | Direct host path |
| More portable | Host-dependent |

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [NGINX Documentation](https://nginx.org/en/docs/)
- [WordPress Codex](https://codex.wordpress.org/)
- [MariaDB Documentation](https://mariadb.com/kb/en/documentation/)

### AI Usage

AI was used for initial boilerplate and debugging configuration syntax. All code was reviewed and understood before implementation.
