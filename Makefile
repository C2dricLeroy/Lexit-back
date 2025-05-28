PROJECT_NAME=fastapi_app

SERVICE_NAME=web

COMPOSE=docker compose

start:
	@$(COMPOSE) up

startd:
	@$(COMPOSE) up -d --build

dbd:
	@$(COMPOSE) up db -d --build

down:
	@$(COMPOSE) down

logs:
	@$(COMPOSE) logs -f

ps:
	@$(COMPOSE) ps

build:
	@$(COMPOSE) build

bash:
	@$(COMPOSE) exec $(SERVICE_NAME) /bin/bash

freeze:
	@$(COMPOSE) exec $(SERVICE_NAME) pip freeze > requirements.txt

test:
	@$(COMPOSE) exec $(SERVICE_NAME) pytest

delete:
	@$(COMPOSE) down -v

rebuild:
	@$(COMPOSE) down -v
	@$(COMPOSE) up --build
