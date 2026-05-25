#!/usr/bin/env bash
# Erase all (or filtered) points from InfluxDB. Does not modify CSV exports.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

usage() {
  cat <<'EOF'
Usage: scripts/clean_influx_data.sh [options]

Delete time-series data from InfluxDB. CSV files under exports/ are
never touched. New readings continue to flow into Influx after cleanup.

Options:
  -y, --yes              Skip confirmation prompt
  -m, --measurement NAME Only delete this measurement (default: entire bucket)
  -h, --help             Show this help

Requires: docker compose stack running, .env with INFLUXDB_* variables.
EOF
}

YES=false
MEASUREMENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes) YES=true ;;
    -m|--measurement)
      MEASUREMENT="${2:?--measurement requires a name}"
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

if [[ ! -f .env ]]; then
  echo "Missing .env — run: cp .env.example .env"
  exit 1
fi

set -a
# shellcheck source=/dev/null
source <(tr -d '\r' < .env)
set +a

ORG="${INFLUXDB_ORG:-tempsensor}"
BUCKET="${INFLUXDB_BUCKET:-temperature}"
TOKEN="${INFLUXDB_ADMIN_TOKEN:?Set INFLUXDB_ADMIN_TOKEN in .env}"
CSV_DIR="${CSV_DIR:-exports}"

if ! docker compose ps --status running --services 2>/dev/null | grep -qx influxdb; then
  echo "InfluxDB container is not running. Start the stack: docker compose up -d"
  exit 1
fi

echo "InfluxDB org:    ${ORG}"
echo "InfluxDB bucket: ${BUCKET}"
if [[ -n "${MEASUREMENT}" ]]; then
  echo "Measurement:     ${MEASUREMENT} only"
else
  echo "Scope:           all data in bucket"
fi
echo "CSV dir (unchanged): ${CSV_DIR}/"
echo ""

if [[ "${YES}" != true ]]; then
  read -r -p "Delete InfluxDB data? CSV will NOT be modified. [y/N] " reply
  case "${reply}" in
    [yY]|[yY][eE][sS]) ;;
    *) echo "Cancelled."; exit 0 ;;
  esac
fi

DELETE_ARGS=(
  delete
  --org "${ORG}"
  --bucket "${BUCKET}"
  --start 1970-01-01T00:00:00Z
  --stop 2099-12-31T23:59:59Z
  --token "${TOKEN}"
)

if [[ -n "${MEASUREMENT}" ]]; then
  DELETE_ARGS+=(--pred "_measurement=\"${MEASUREMENT}\"")
fi

echo "Deleting InfluxDB data..."
docker compose exec -T influxdb influx "${DELETE_ARGS[@]}"
echo "Done. InfluxDB is empty for the selected scope; files in ${CSV_DIR}/ were not modified."
echo "Grafana will show new data only after Telegraf writes again (refresh the dashboard)."
