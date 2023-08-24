## for start mySQL container:
SHELL := /bin/bash
PRODUCTION_COMPOSE_FILE := ../infra/production/docker-compose.yml
DEVELOPMENT_COMPOSE_FILE := ../infra/development/docker-compose.yml
RELATIVE_MANAGE_PY_PATH := ../backend/src/manage.py
ENV ?= dev

SUPERUSER_EMAIL = admin@fake.com
SUPERUSER_USERNAME = admin
SUPERUSER_PASSWORD = admin

COLOR_RESET = \033[0m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_WHITE = \033[00m

.DEFAULT_GOAL := help


.PHONY: help
help:
	@echo -e "$(COLOR_GREEN)Makefile help:"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "$(COLOR_GREEN)-$$(echo $$l | cut -f 1 -d':'):$(COLOR_WHITE)$$(echo $$l | cut -f 2- -d'#')\n"; done


.PHONY: run
run: clean start collectstatic migrate createsuperuser # Initialize the application
	@echo -e "$(COLOR_GREEN)Application initialized$(COLOR_RESET)"


.PHONY: start
start: # Start the application
ifeq ($(ENV),prod)
	@echo -e "$(COLOR_YELLOW)Starting production build...$(COLOR_RESET)"
	$(eval COMPOSE_FILE=$(PRODUCTION_COMPOSE_FILE))
else ifeq ($(ENV),dev)
	@echo -e "$(COLOR_YELLOW)Starting development build...$(COLOR_RESET)"
	$(eval COMPOSE_FILE=$(DEVELOPMENT_COMPOSE_FILE))
endif
	@until docker compose -f $(COMPOSE_FILE) up --build -d; do \
		echo -e "$(COLOR_YELLOW)Waiting app to be started...$(COLOR_RESET)"; \
		sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)App started$(COLOR_RESET)"


.PHONY: down
down: # Shutdown the application
ifeq ($(ENV),prod)
	@echo -e "$(COLOR_YELLOW)Stopping production build...$(COLOR_RESET)"
	$(eval COMPOSE_FILE=$(PRODUCTION_COMPOSE_FILE))
else ifeq ($(ENV),dev)
	@echo -e "$(COLOR_YELLOW)Stopping development build...$(COLOR_RESET)"
	$(eval COMPOSE_FILE=$(DEVELOPMENT_COMPOSE_FILE))
endif
	@until docker compose -f $(COMPOSE_FILE) down; do \
		echo -e "$(COLOR_YELLOW)Waiting app to be stopped...$(COLOR_RESET)"; \
		sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)App stopped$(COLOR_RESET)"


.PHONY: collectstatic
collectstatic: # Collect static files
ifeq ($(ENV),prod)
	@echo -e "$(COLOR_YELLOW)Collecting static files for production build...$(COLOR_RESET)"
	$(eval COMMAND=docker compose -f $(PRODUCTION_COMPOSE_FILE) run --rm backend python manage.py collectstatic --noinput)
	@echo "Command: $(COMMAND)"
else ifeq ($(ENV),dev)
	@echo -e "$(COLOR_GREEN)Skipping collecting static files for development build...$(COLOR_GREEN)"
	$(eval COMMAND=exit 0)
endif
	@until $(COMMAND); do \
		echo -e "$(COLOR_YELLOW)Waiting static files to be collected...$(COLOR_RESET)"; \
		sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Static files collected$(COLOR_RESET)"


.PHONY: migrate
migrate: # Apply database migrations
ifeq ($(ENV),prod)
	@echo -e "$(COLOR_YELLOW)Migrating production database...$(COLOR_RESET)"
	$(eval COMMAND=docker compose -f $(PRODUCTION_COMPOSE_FILE) run --rm backend python manage.py migrate)
else ifeq ($(ENV),dev)
	@echo -e "$(COLOR_YELLOW)Migrating development database...$(COLOR_RESET)"
	$(eval COMMAND=python $(RELATIVE_MANAGE_PY_PATH) migrate)
endif
	@until $(COMMAND); do \
		echo -e "$(COLOR_YELLOW)Waiting migrations to be applied...$(COLOR_RESET)"; \
		sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Migrations applied$(COLOR_RESET)"


.PHONY: createsuperuser
createsuperuser: # Create superuser
ifeq ($(ENV),prod)
	@echo -e "$(COLOR_YELLOW)Creating superuser for production database...$(COLOR_RESET)"
	$(eval COMMAND=docker compose -f $(PRODUCTION_COMPOSE_FILE) run --rm backend python manage.py createsuperuser --username=$(SUPERUSER_USERNAME) --email=$(SUPERUSER_EMAIL) --noinput)
else ifeq ($(ENV),dev)
	@echo -e "$(COLOR_YELLOW)Creating superuser for development database...$(COLOR_RESET)"
	$(eval COMMAND=python $(RELATIVE_MANAGE_PY_PATH) createsuperuser --username=$(SUPERUSER_USERNAME) --email=$(SUPERUSER_EMAIL) --noinput)
endif
	@until $(COMMAND); do \
		echo -e "$(COLOR_YELLOW)Waiting superuser to be created...$(COLOR_RESET)"; \
		sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Superuser created. Login: $(SUPERUSER_EMAIL) Password: $(SUPERUSER_PASSWORD)$(COLOR_RESET)"


.PHONY: clean
clean: # Delete database, volumes and networks
ifeq ($(ENV),prod)
	@echo -e "$(COLOR_YELLOW)Deleting production database...$(COLOR_RESET)"
	$(eval COMPOSE_FILE=$(PRODUCTION_COMPOSE_FILE))
else ifeq ($(ENV),dev)
	@echo -e "$(COLOR_YELLOW)Deleting development database...$(COLOR_RESET)"
	$(eval COMPOSE_FILE=$(DEVELOPMENT_COMPOSE_FILE))
endif
	@until docker compose -f $(COMPOSE_FILE) down -v; do \
		echo -e "$(COLOR_YELLOW)Waiting database to be deleted...$(COLOR_RESET)"; \
		sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Database deleted$(COLOR_RESET)"
