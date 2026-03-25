NAME = inception
COMPOSE_FILE = srcs/docker-compose.yml
DATA_PATH = $(HOME)/data
ENV_FILE = srcs/.env

DOCKER_COMPOSE = docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)

all: setup build up

setup:
	@sudo mkdir -p $(DATA_PATH)/wordpress
	@sudo mkdir -p $(DATA_PATH)/mariadb
	@sudo chmod -R 777 $(DATA_PATH)
	@sudo chmod 777 $(DATA_PATH)/wordpress
	@sudo chmod 777 $(DATA_PATH)/mariadb

build:
	@$(DOCKER_COMPOSE) build

up:
	@$(DOCKER_COMPOSE) up -d

down:
	@$(DOCKER_COMPOSE) down

stop:
	@$(DOCKER_COMPOSE) stop

logs:
	@$(DOCKER_COMPOSE) logs -f

status:
	@docker ps -a

clean: down
	sudo @docker image prune -af

fclean: down
	sudo @$(DOCKER_COMPOSE) down -v --rmi all 2>/dev/null || true
	sudo @rm -rf $(DATA_PATH)/wordpress/* $(DATA_PATH)/mariadb/* 2>/dev/null || true

re: fclean all

.PHONY: all setup build up down stop logs status clean fclean re
