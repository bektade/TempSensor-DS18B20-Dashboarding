# WebApp — run from this directory: cd WebApp && make <target>
SHELL := /bin/bash
COMPOSE := docker compose
DJANGO := $(COMPOSE) exec -T django_web python manage.py
ROOT := $(CURDIR)
VENV_PY := $(ROOT)/.venv/bin/python
IMPORT_PENDING := $(ROOT)/data/import_pending
ARCHIVE_OK := $(ROOT)/data/archive/db_migrated
ARCHIVE_FAIL := $(ROOT)/data/archive/import_failed

.PHONY: help startwebapp stopWebApp migrate setup env import importcsv logs status urls resetadmin

help:
	@echo "WebApp targets:"
	@echo "  make setup        Create .venv + .env (host tools only)"
	@echo "  make startwebapp  Start postgres + django (no pgAdmin)"
	@echo "  make stopWebApp   Stop postgres + django"
	@echo "  make migrate      Apply Django migrations"
	@echo "  make import       Import CSV files into PostgreSQL (see below)"
	@echo "  make logs         Follow django_web logs"
	@echo "  make status       Show container status"
	@echo "  make resetadmin   Reset Django /admin/ password from .env"
	@echo ""
	@echo "pgAdmin (optional, separate stack): cd pgadmin && make start"
	@echo "  Guide: pgadmin/README.md"
	@echo "  make migrate      Apply Django migrations"
	@echo "  make import       Import CSV files into PostgreSQL (see below)"
	@echo "  make logs         Follow django_web logs"
	@echo "  make status       Show container status"
	@echo "  make resetadmin   Reset Django /admin/ password from .env"
	@echo ""
	@echo "Import CSV into database:"
	@echo "  1. make startwebapp"
	@echo "  2. Copy CSV files into:  data/import_pending/"
	@echo "     Example:"
	@echo "       cp ../exports/*.csv data/import_pending/"
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

stopWebApp:
	$(COMPOSE) down

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
		echo "  cp ../exports/*.csv data/import_pending/"; \
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
