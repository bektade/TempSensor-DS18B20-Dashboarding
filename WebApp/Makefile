# WebApp — run from this directory: cd WebApp && make <target>
SHELL := /bin/bash
COMPOSE := docker compose
DJANGO := $(COMPOSE) exec -T django_web python manage.py
ROOT := $(CURDIR)
VENV_PY := $(ROOT)/.venv/bin/python
IMPORT_PENDING := $(ROOT)/data/import_pending
ARCHIVE_OK := $(ROOT)/data/archive/db_migrated
ARCHIVE_FAIL := $(ROOT)/data/archive/import_failed
BACKUP_DIR := $(ROOT)/data/backups

.PHONY: help startwebapp startwebapp-hub rebuildwebapp-hub stopWebApp migrate setup env import importcsv logs status urls resetadmin docker-build docker-push docker-publish db-backup db-restore

HUB_COMPOSE := $(COMPOSE) -f docker-compose.yml -f docker-compose.hub.yml

help:
	@echo "WebApp targets:"
	@echo "  make setup        Create .venv + .env (host tools only)"
	@echo "  make startwebapp      Start postgres + django (build locally)"
	@echo "  make startwebapp-hub     First start from Docker Hub (postgres + django)"
	@echo "  make rebuildwebapp-hub   Pull new image tag and restart django"
	@echo "  make db-backup        Dump PostgreSQL to data/backups/"
	@echo "  make db-restore       Restore from FILE=data/backups/....sql.gz"
	@echo "  make stopWebApp   Stop postgres + django"
	@echo "  make migrate      Apply Django migrations"
	@echo "  make import       Import CSV files into PostgreSQL (see below)"
	@echo "  make logs         Follow django_web logs"
	@echo "  make status       Show container status"
	@echo "  make resetadmin   Reset Django /admin/ password from .env"
	@echo "  make docker-build     Build WebApp image locally"
	@echo "  make docker-push      Push WebApp image to Docker Hub"
	@echo "  make docker-publish   Build + push WebApp image"
	@echo ""
	@echo "pgAdmin (optional, separate stack): cd pgadmin && make start"
	@echo "  Guide: pgadmin/README.md"
	@echo ""
	@echo "Import CSV into database:"
	@echo "  1. make startwebapp"
	@echo "  2. Copy CSV files into:  data/import_pending/"
	@echo "     Example:"
	@echo "       cp ../SensorDataCollector/exports/*.csv data/import_pending/"
	@echo "  3. make import"
	@echo ""
	@echo "  Filename pattern (optional metadata):"
	@echo "    YYYY-MM-DD_HHMMAM_ModelName_SerialNumber.csv"
	@echo "  After import:"
	@echo "    success -> data/archive/db_migrated/"
	@echo "    failed  -> data/archive/import_failed/"
	@echo "  Details: docs/CSV_IMPORT.md"
	@echo "  pgAdmin:      pgadmin/README.md (optional: cd pgadmin && make start)"
	@echo "  Django admin: docs/DJANGO_ADMIN.md (make resetadmin)"
	@echo "  Docker Hub:   docs/DOCKER_HUB.md  |  CI/CD: ../docs/CI_CD.md"

env:
	@if [[ ! -f .env ]]; then cp .env.example .env && echo "Created .env from .env.example"; fi

setup: env
	@./scripts/setup_venv.sh

startwebapp: env
	$(COMPOSE) up -d --build postgres django_web
	@echo ""
	@port=$${DJANGO_PUBLISH_PORT:-8000}; \
	lan_ip=$$(hostname -I 2>/dev/null | awk '{print $$1}'); \
	echo "WebApp running:"; \
	echo "  On this Pi:    http://localhost:$$port/"; \
	if [[ -n "$$lan_ip" ]]; then \
	  echo "  From LAN/PC:   http://$$lan_ip:$$port/  (not localhost on another computer)"; \
	fi; \
	echo "  Admin:         http://localhost:$$port/admin/"; \
	echo "  Postgres:      localhost:$${POSTGRES_PUBLISH_PORT:-5433}"; \
	echo ""
	@echo "Optional pgAdmin: cd pgadmin && make start  (see pgadmin/README.md)"
	@echo ""
	@echo "Import CSV: copy files to data/import_pending/ then run: make import"

startwebapp-hub: env
	$(HUB_COMPOSE) pull django_web
	$(HUB_COMPOSE) up -d --no-build postgres django_web
	@echo ""
	@port=$${DJANGO_PUBLISH_PORT:-8000}; \
	lan_ip=$$(hostname -I 2>/dev/null | awk '{print $$1}'); \
	echo "WebApp running (Docker Hub image: $${DOCKER_IMAGE_WEBAPP:-becktkh/tempsensor-webapp}:$${DOCKER_TAG:-latest}):"; \
	echo "  On this Pi:    http://localhost:$$port/"; \
	if [[ -n "$$lan_ip" ]]; then \
	  echo "  From LAN/PC:   http://$$lan_ip:$$port/"; \
	fi; \
	echo "  Admin:         http://localhost:$$port/admin/"
	@echo ""
	@echo "Optional pgAdmin: cd pgadmin && make start"
	@echo "Guide: docs/DOCKER_HUB.md"

rebuildwebapp-hub: env
	$(HUB_COMPOSE) pull django_web
	$(HUB_COMPOSE) up -d --no-build --force-recreate django_web
	@echo ""
	@echo "Rebuilt from Docker Hub: $${DOCKER_IMAGE_WEBAPP:-becktkh/tempsensor-webapp}:$${DOCKER_TAG:-latest}"
	@echo "  http://localhost:$${DJANGO_PUBLISH_PORT:-8000}/"

stopWebApp:
	$(COMPOSE) down

db-backup: env
	@mkdir -p "$(BACKUP_DIR)"
	@if ! $(COMPOSE) ps --status running --services 2>/dev/null | grep -qx postgres; then \
		echo "PostgreSQL is not running. Start first: make startwebapp or make startwebapp-hub" >&2; \
		exit 1; \
	fi
	@stamp=$$(date +%Y%m%d_%H%M%S); \
	out="$(BACKUP_DIR)/sauna_tests_$$stamp.sql.gz"; \
	$(COMPOSE) exec -T postgres pg_dump -U $${POSTGRES_USER:-sauna_user} -d $${POSTGRES_DB:-sauna_tests} \
		| gzip > "$$out"; \
	echo "Backup written: $$out"

db-restore: env
	@if [[ -z "$(FILE)" ]]; then \
		echo "Usage: make db-restore FILE=data/backups/sauna_tests_YYYYMMDD_HHMMSS.sql.gz" >&2; \
		exit 1; \
	fi
	@if [[ ! -f "$(FILE)" ]]; then \
		echo "File not found: $(FILE)" >&2; \
		exit 1; \
	fi
	@if ! $(COMPOSE) ps --status running --services 2>/dev/null | grep -qx postgres; then \
		echo "PostgreSQL is not running. Start first: make startwebapp or make startwebapp-hub" >&2; \
		exit 1; \
	fi
	@echo "Restoring $(FILE) into $${POSTGRES_DB:-sauna_tests} ..."
	@gunzip -c "$(FILE)" | $(COMPOSE) exec -T postgres psql -U $${POSTGRES_USER:-sauna_user} -d $${POSTGRES_DB:-sauna_tests} -v ON_ERROR_STOP=1
	@echo "Restore complete."

migrate: env
	@if $(COMPOSE) ps --status running --services 2>/dev/null | grep -qx django_web; then \
		$(DJANGO) migrate --noinput; \
	elif [[ -x $(VENV_PY) ]]; then \
		POSTGRES_HOST=$${POSTGRES_HOST:-localhost} POSTGRES_PORT=$${POSTGRES_PORT:-5433} \
			$(VENV_PY) manage.py migrate --noinput; \
	else \
		echo "Start containers first (make startwebapp) or run make setup for host migrate." >&2; \
		exit 1; \
	fi

import: env
	@mkdir -p "$(IMPORT_PENDING)" "$(ARCHIVE_OK)" "$(ARCHIVE_FAIL)"
	@echo "=== Import CSV into PostgreSQL ==="
	@echo "Pending folder: $(IMPORT_PENDING)"
	@pending=$$(find "$(IMPORT_PENDING)" -maxdepth 1 -name '*.csv' 2>/dev/null | wc -l); \
	if [[ "$$pending" -eq 0 ]]; then \
		echo ""; \
		echo "No CSV files found. Copy exports first, for example:"; \
		echo "  cp ../SensorDataCollector/exports/*.csv data/import_pending/"; \
		echo "Then run: make import"; \
		exit 1; \
	fi
	@echo "Files to import:"
	@find "$(IMPORT_PENDING)" -maxdepth 1 -name '*.csv' -printf '  %f\n' | sort
	@echo ""
	@if $(COMPOSE) ps --status running --services 2>/dev/null | grep -qx django_web; then \
		$(DJANGO) import_pending_csv; \
	elif [[ -x $(VENV_PY) ]]; then \
		POSTGRES_HOST=$${POSTGRES_HOST:-localhost} POSTGRES_PORT=$${POSTGRES_PORT:-5433} \
			$(VENV_PY) manage.py import_pending_csv; \
	else \
		echo "Start containers first: make startwebapp" >&2; \
		exit 1; \
	fi
	@echo ""
	@echo "Done. Successful imports archived under: data/archive/db_migrated/"
	@echo "Failed imports (if any) under:          data/archive/import_failed/"
	@echo "View runs: http://localhost:$${DJANGO_PUBLISH_PORT:-8000}/"

importcsv: import

logs:
	$(COMPOSE) logs -f django_web

status:
	@$(COMPOSE) ps

resetadmin: env
	@./scripts/reset_django_admin.sh

docker-build:
	@DOCKERHUB_USER=$${DOCKERHUB_USER:?Set DOCKERHUB_USER} ./scripts/docker-publish.sh

docker-push:
	@DOCKERHUB_USER=$${DOCKERHUB_USER:?Set DOCKERHUB_USER} PUSH=1 ./scripts/docker-publish.sh --push

docker-publish: docker-push

urls:
	@port=$${DJANGO_PUBLISH_PORT:-8000}; \
	lan_ip=$$(hostname -I 2>/dev/null | awk '{print $$1}'); \
	echo "Django app URLs (port $$port):"; \
	echo "  Browser ON the Pi:     http://localhost:$$port/"; \
	if [[ -n "$$lan_ip" ]]; then \
	  echo "  Browser on another PC: http://$$lan_ip:$$port/"; \
	  echo "  (localhost on your PC does NOT reach the Pi)"; \
	else \
	  echo "  Browser on another PC: http://<pi-ip>:$$port/"; \
	fi; \
	echo ""; \
	if $(COMPOSE) ps --status running --services 2>/dev/null | grep -qx django_web; then \
	  echo "django_web: running"; \
	else \
	  echo "django_web: NOT running — run: make startwebapp"; \
	fi
