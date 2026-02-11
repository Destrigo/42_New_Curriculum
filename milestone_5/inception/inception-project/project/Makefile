# **************************************************************************** #
#                                 INCEPTION                                    #
# **************************************************************************** #

# Variables
NAME			= inception
COMPOSE_FILE	= srcs/docker-compose.yml
DATA_PATH		= /home/$(USER)/data
ENV_FILE		= srcs/.env

# Colors
GREEN	= \033[0;32m
YELLOW	= \033[0;33m
RED		= \033[0;31m
RESET	= \033[0m

# Docker Compose command
DOCKER_COMPOSE = docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)

# Default target
all: setup build up

# Setup: Create necessary directories and verify prerequisites
setup:
	@echo "$(YELLOW)Setting up directories...$(RESET)"
	@mkdir -p $(DATA_PATH)/wordpress
	@mkdir -p $(DATA_PATH)/mariadb
	@echo "$(GREEN)Directories created at $(DATA_PATH)$(RESET)"

# Build Docker images
build:
	@echo "$(YELLOW)Building Docker images...$(RESET)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Build complete!$(RESET)"

# Start containers
up:
	@echo "$(YELLOW)Starting containers...$(RESET)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Containers are up!$(RESET)"

# Start containers with logs visible
up-logs:
	@echo "$(YELLOW)Starting containers with logs...$(RESET)"
	@$(DOCKER_COMPOSE) up

# Stop containers
stop:
	@echo "$(YELLOW)Stopping containers...$(RESET)"
	@$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)Containers stopped!$(RESET)"

# Stop and remove containers
down:
	@echo "$(YELLOW)Stopping and removing containers...$(RESET)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Containers removed!$(RESET)"

# Remove containers, networks, and images
clean: down
	@echo "$(YELLOW)Cleaning up images...$(RESET)"
	@docker image prune -af
	@echo "$(GREEN)Cleanup complete!$(RESET)"

# Full clean: remove everything including volumes and data
fclean: down
	@echo "$(RED)WARNING: This will delete all data!$(RESET)"
	@echo "$(YELLOW)Removing volumes...$(RESET)"
	@$(DOCKER_COMPOSE) down -v --rmi all 2>/dev/null || true
	@docker system prune -af --volumes 2>/dev/null || true
	@echo "$(YELLOW)Removing data directories...$(RESET)"
	@sudo rm -rf $(DATA_PATH)/wordpress/* 2>/dev/null || true
	@sudo rm -rf $(DATA_PATH)/mariadb/* 2>/dev/null || true
	@echo "$(GREEN)Full cleanup complete!$(RESET)"

# Rebuild everything from scratch
re: fclean all

# Show container status
status:
	@echo "$(YELLOW)Container Status:$(RESET)"
	@docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Show logs
logs:
	@$(DOCKER_COMPOSE) logs -f

# Show logs for specific service
logs-nginx:
	@$(DOCKER_COMPOSE) logs -f nginx

logs-wordpress:
	@$(DOCKER_COMPOSE) logs -f wordpress

logs-mariadb:
	@$(DOCKER_COMPOSE) logs -f mariadb

# Enter containers
shell-nginx:
	@docker exec -it nginx sh

shell-wordpress:
	@docker exec -it wordpress sh

shell-mariadb:
	@docker exec -it mariadb sh

# Health check
health:
	@echo "$(YELLOW)Checking services...$(RESET)"
	@echo "NGINX:"
	@docker exec nginx nginx -t 2>&1 || echo "$(RED)NGINX not running$(RESET)"
	@echo "\nMariaDB:"
	@docker exec mariadb mysqladmin ping -h localhost 2>&1 || echo "$(RED)MariaDB not running$(RESET)"
	@echo "\nWordPress/PHP-FPM:"
	@docker exec wordpress php-fpm83 -t 2>&1 || echo "$(RED)PHP-FPM not running$(RESET)"

# Help
help:
	@echo "$(GREEN)Inception Makefile Commands:$(RESET)"
	@echo "  make / make all    - Setup, build, and start everything"
	@echo "  make setup         - Create data directories"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start containers (detached)"
	@echo "  make up-logs       - Start containers with logs visible"
	@echo "  make stop          - Stop containers"
	@echo "  make down          - Stop and remove containers"
	@echo "  make clean         - Remove containers and images"
	@echo "  make fclean        - Remove everything including volumes"
	@echo "  make re            - Rebuild from scratch"
	@echo "  make status        - Show container status"
	@echo "  make logs          - Show all logs"
	@echo "  make logs-nginx    - Show NGINX logs"
	@echo "  make logs-wordpress- Show WordPress logs"
	@echo "  make logs-mariadb  - Show MariaDB logs"
	@echo "  make shell-nginx   - Enter NGINX container"
	@echo "  make shell-wordpress - Enter WordPress container"
	@echo "  make shell-mariadb - Enter MariaDB container"
	@echo "  make health        - Check service health"

.PHONY: all setup build up up-logs stop down clean fclean re status logs \
        logs-nginx logs-wordpress logs-mariadb shell-nginx shell-wordpress \
        shell-mariadb health help
