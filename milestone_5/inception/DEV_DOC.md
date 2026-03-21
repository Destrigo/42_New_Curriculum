# Developer Documentation - Inception

## Prerequisites

- Docker and Docker Compose
- Make

## Setup

1. Edit `srcs/.env` - replace `login` with your 42 username
2. Edit `secrets/*.txt` - set secure passwords
3. Create data directories:
   ```bash
   mkdir -p ~/data/wordpress ~/data/mariadb
   ```
4. Build and run:
   ```bash
   make
   ```

## Project Structure

```
inception/
├── Makefile
├── README.md
├── USER_DOC.md
├── DEV_DOC.md
├── .gitignore
├── secrets/
│   ├── db_password.txt
│   ├── db_root_password.txt
│   └── credentials.txt
└── srcs/
    ├── .env
    ├── docker-compose.yml
    └── requirements/
        ├── nginx/
        │   ├── Dockerfile
        │   ├── .dockerignore
        │   ├── conf/
        │   │   └── nginx.conf
        │   └── tools/
        │       └── setup-ssl.sh
        ├── wordpress/
        │   ├── Dockerfile
        │   ├── .dockerignore
        │   ├── conf/
        │   │   └── www.conf
        │   └── tools/
        │       └── setup-wp.sh
        └── mariadb/
            ├── Dockerfile
            ├── .dockerignore
            ├── conf/
            │   └── 50-server.cnf
            └── tools/
                └── init-db.sh
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make` | Setup, build, and start |
| `make build` | Build images only |
| `make up` | Start containers |
| `make down` | Stop and remove containers |
| `make stop` | Stop containers |
| `make logs` | View logs |
| `make status` | Show container status |
| `make clean` | Remove images |
| `make fclean` | Full cleanup |
| `make re` | Rebuild |

## Container Access

```bash
docker exec -it nginx sh
docker exec -it wordpress sh
docker exec -it mariadb sh
```

## Testing TLS

```bash
# Should succeed (TLSv1.2)
openssl s_client -connect localhost:443 -tls1_2

# Should succeed (TLSv1.3)
openssl s_client -connect localhost:443 -tls1_3

# Should fail (TLSv1.1 not allowed)
openssl s_client -connect localhost:443 -tls1_1
```

## Database Access

```bash
docker exec -it mariadb sh
mysql -u wpuser -p wordpress
# Enter password from secrets/db_password.txt
```

## Debugging

**View specific logs:**
```bash
docker logs nginx
docker logs wordpress
docker logs mariadb
```

**Check container health:**
```bash
docker inspect --format='{{.State.Health.Status}}' wordpress
docker inspect --format='{{.State.Health.Status}}' mariadb
```

**Restart single service:**
```bash
docker compose -f srcs/docker-compose.yml restart nginx
```
