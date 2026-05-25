# TempSensor MQTT / Grafana stack
# Run all targets from the repo root (this Makefile's directory):
#   cd ~/Projects/TempSensor && make <target>
SHELL := /bin/bash
ROOT := $(CURDIR)

ifeq ($(shell docker info >/dev/null 2>&1 && echo yes),yes)
  COMPOSE := docker compose
else
  COMPOSE := sudo docker compose
endif

.PHONY: help env startReadSensor stopReadSensor status logs logs-grafana plot check clean-influx

help:
	@echo "TempSensor stack (MQTT, InfluxDB, Grafana, CSV export)"
	@echo "Run from: $(ROOT)"
	@echo "  cd $(ROOT)"
	@echo ""
	@echo "  make env              Create .env from .env.example (first time)"
	@echo "  make startReadSensor  Prompt TestUnit + serial, start sensor stack"
	@echo "  make stopReadSensor   Stop stack and plot latest CSV (PNG)"
	@echo "  make status           Show running containers"
	@echo "  make logs             Tail mqtt-publisher logs"
	@echo "  make logs-grafana     Tail Grafana logs"
	@echo "  make plot             Plot latest CSV to Visualize/output/ (host venv)"
	@echo "  make check            Verify MQTT, CSV, Influx pipeline"
	@echo "  make clean-influx     Delete InfluxDB data (see docs/INFLUXDB.md)"
	@echo ""
	@echo "Start workflow:"
	@echo "  1. make env              (once)"
	@echo "  2. make startReadSensor  (enter TestUnit and Serial Number)"
	@echo "  3. Open Grafana:         http://localhost:3000"
	@echo ""
	@echo "Stop workflow:"
	@echo "  make stopReadSensor      (archives CSV on next start; writes PNG on stop)"
	@echo ""
	@echo "Product test database (separate):  cd WebApp && make help"

env:
	@if [[ ! -f .env ]]; then cp .env.example .env && echo "Created .env — edit secrets before make startReadSensor"; else echo ".env already exists"; fi

startReadSensor: env
	@echo "Running from: $(ROOT)"
	@$(ROOT)/scripts/compose-up.sh

stopReadSensor:
	@$(ROOT)/scripts/compose-down.sh

status:
	@$(COMPOSE) ps

logs:
	@$(COMPOSE) logs -f mqtt-publisher

logs-grafana:
	@$(COMPOSE) logs -f grafana

plot:
	@$(ROOT)/scripts/fix_visualize_output_permissions.sh
	@$(ROOT)/scripts/plot_latest_csv.sh --export-dir exports --presentation --output-auto

check:
	@$(ROOT)/scripts/check_pipeline.sh

clean-influx:
	@$(ROOT)/scripts/clean_influx_data.sh
