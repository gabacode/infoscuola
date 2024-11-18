.DEFAULT_GOAL := help

DOCKER_COMPOSE := docker compose

start:
	@bash -c "$(DOCKER_COMPOSE) up -d"

restart:
	@bash -c "$(DOCKER_COMPOSE) down && $(DOCKER_COMPOSE) up -d"

stop:
	@bash -c "$(DOCKER_COMPOSE) down"

build:
	@bash -c "$(DOCKER_COMPOSE) build"

start-ext:
	@bash -c "$(DOCKER_COMPOSE) -f docker-compose.ext.yml up -d"

stop-ext:
	@bash -c "$(DOCKER_COMPOSE) -f docker-compose.ext.yml down"

restart-ext:
	@bash -c "$(DOCKER_COMPOSE) -f docker-compose.ext.yml down && $(DOCKER_COMPOSE) -f docker-compose.ext.yml up -d"

build-ext:
	@bash -c "$(DOCKER_COMPOSE) -f docker-compose.ext.yml build"

logs:
	@bash -c "$(DOCKER_COMPOSE) logs -t --tail=50 -f"

help:
	@echo "Available commands:"
	@echo "======================================================="
	@echo "  General"
	@echo "======================================================="
	@echo "  logs         - Show logs"
	@echo "======================================================="
	@echo "  Production"
	@echo "======================================================="
	@echo "  start        - Start the application"
	@echo "  restart      - Restart the application"
	@echo "  stop         - Stop the application"
	@echo "  build        - Build the application"
	@echo "======================================================="
	@echo "  External Mode"
	@echo "======================================================="
	@echo "  start-ext    - Start the application in external mode"
	@echo "  stop-ext     - Stop the application in external mode"
	@echo "  restart-ext  - Restart the application in external mode"
	@echo "  build-ext    - Build the application in external mode"
	@echo "======================================================="

.PHONY: install start stop restart build start-ext stop-ext restart-ext logs help
