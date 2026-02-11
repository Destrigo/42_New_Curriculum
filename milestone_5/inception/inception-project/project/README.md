*This project has been created as part of the 42 curriculum by login.*

# Inception

A Docker-based infrastructure project that sets up a complete WordPress environment with NGINX, PHP-FPM, and MariaDB, all running in separate containers.

## Description

Inception is a system administration project that demonstrates containerization using Docker. The project creates a small but complete web infrastructure with the following components:

- **NGINX**: Web server and reverse proxy handling HTTPS connections (TLSv1.2/TLSv1.3 only)
- **WordPress + PHP-FPM**: Content management system with PHP FastCGI Process Manager
- **MariaDB**: MySQL-compatible database server

All services run in isolated containers connected via a Docker network, with persistent data stored in Docker volumes.

### Architecture Diagram

```
           Internet
               │
               ▼ (Port 443 HTTPS)
        ┌──────────────┐
        │    NGINX     │
        │  (TLS 1.2/3) │
        └──────┬───────┘
               │ FastCGI :9000
               ▼
        ┌──────────────┐
        │  WordPress   │
        │   PHP-FPM    │
        └──────┬───────┘
               │ MySQL :3306
               ▼
        ┌──────────────┐
        │   MariaDB    │
        └──────────────┘
```

## Instructions

### Prerequisites

- A Virtual Machine running Debian or Ubuntu
- Docker and Docker Compose installed
- sudo/root access

### Installation

1. Clone the repository:
```bash
git clone <repository-url> inception
cd inception
```

2. Configure your environment:
```bash
# Edit srcs/.env and replace 'login' with your username
nano srcs/.env

# Add your domain to /etc/hosts
echo "127.0.0.1 login.42.fr" | sudo tee -a /etc/hosts
```

3. Set secure passwords in the secrets directory:
```bash
# Generate secure passwords
openssl rand -base64 32 > secrets/db_password.txt
openssl rand -base64 32 > secrets/db_root_password.txt
openssl rand -base64 24 > secrets/credentials.txt
```

4. Build and run:
```bash
make
```

### Accessing the Site

Open your browser and navigate to `https://login.42.fr` (replace 'login' with your username).

**Note**: You will see a certificate warning because the SSL certificate is self-signed. This is expected for development environments.

## Project Description

### Virtual Machines vs Docker

| Aspect | Virtual Machines | Docker Containers |
|--------|-----------------|-------------------|
| **Isolation** | Full OS isolation | Process-level isolation |
| **Resource Usage** | Heavy (GB of RAM) | Lightweight (MB of RAM) |
| **Boot Time** | Minutes | Seconds |
| **Portability** | Limited | Highly portable |
| **Use Case** | Different OS needs | Microservices, same OS |

**Why Docker for this project**: Docker provides lightweight, fast, and reproducible environments perfect for running web services without the overhead of full virtualization.

### Secrets vs Environment Variables

| Aspect | Environment Variables | Docker Secrets |
|--------|----------------------|----------------|
| **Storage** | In memory, visible in `docker inspect` | Encrypted, stored in tmpfs |
| **Access** | Any process can read | Only authorized containers |
| **Security** | Less secure | More secure |
| **Use Case** | Non-sensitive config | Passwords, API keys |

**This project uses both**: Environment variables for non-sensitive configuration (domain name, usernames) and Docker secrets for sensitive data (passwords).

### Docker Network vs Host Network

| Aspect | Docker Network | Host Network |
|--------|---------------|--------------|
| **Isolation** | Containers isolated | No isolation |
| **Port Conflicts** | Avoided | Possible |
| **Security** | Better (controlled access) | Reduced |
| **Performance** | Slight overhead | Native performance |

**This project uses Docker network**: Provides isolation between containers while allowing controlled communication on specific ports.

### Docker Volumes vs Bind Mounts

| Aspect | Docker Volumes | Bind Mounts |
|--------|---------------|-------------|
| **Management** | Managed by Docker | Manual |
| **Portability** | More portable | Host-dependent |
| **Backup** | Docker commands | Standard file tools |
| **Performance** | Optimized | OS-dependent |

**This project uses named volumes**: Required by the project specification, with data stored at `/home/login/data/`.

## Resources

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [NGINX Documentation](https://nginx.org/en/docs/)
- [WordPress Codex](https://codex.wordpress.org/)
- [MariaDB Documentation](https://mariadb.com/kb/en/documentation/)
- [PHP-FPM Documentation](https://www.php.net/manual/en/install.fpm.php)

### Tutorials
- [Docker Getting Started](https://docs.docker.com/get-started/)
- [Docker Compose Tutorial](https://docs.docker.com/compose/gettingstarted/)
- [NGINX Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

### AI Usage in This Project

AI tools were used to:
- Understand Docker best practices and PID 1 concepts
- Debug configuration file syntax
- Generate initial boilerplate for Dockerfiles
- Explain complex concepts like FastCGI communication

All AI-generated content was reviewed, tested, and understood before implementation. The project author can explain all code and configuration choices.

## License

This project is part of the 42 curriculum and is subject to 42's academic integrity policies.
