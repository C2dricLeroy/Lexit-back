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
	@$(COMPOSE) up -d --build
	@$(COMPOSE) exec $(SERVICE_NAME) coverage run -m pytest
	@$(COMPOSE) exec $(SERVICE_NAME) coverage html

delete:
	@$(COMPOSE) down -v

rebuild:
	@$(COMPOSE) down -v
	@$(COMPOSE) up --build

migrate:
	@$(COMPOSE) up -d
	@$(COMPOSE) exec $(SERVICE_NAME) alembic upgrade head

downgrade:
	@$(COMPOSE) up -d
	@$(COMPOSE) exec $(SERVICE_NAME) alembic downgrade $(rev)"

makemigration:
	@$(COMPOSE) up -d
	@$(COMPOSE) exec $(SERVICE_NAME) alembic revision --autogenerate -m "$(m)"
