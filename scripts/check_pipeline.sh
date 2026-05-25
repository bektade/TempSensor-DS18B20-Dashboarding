#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ ! -f .env ]]; then
  echo "Missing .env — run: cp .env.example .env"
  exit 1
fi

set -a
# shellcheck source=/dev/null
source <(tr -d '\r' < .env)
set +a

echo "=== Containers ==="
docker compose ps

echo ""
echo "=== Telegraf logs (last 20 lines) ==="
docker compose logs telegraf --tail 20

echo ""
echo "=== MQTT sample (3s) ==="
timeout 3 mosquitto_sub -h localhost -t 'tempsensor/readings' -C 2 -v 2>/dev/null || \
  echo "Install: sudo apt-get install -y mosquitto-clients"

echo ""
echo "=== CSV (latest file, last 3 lines) ==="
LATEST_CSV="$(ls -t exports/*.csv 2>/dev/null | head -1 || true)"
if [[ -n "${LATEST_CSV}" ]]; then
  echo "${LATEST_CSV}"
  tail -3 "${LATEST_CSV}"
else
  echo "(no CSV yet)"
fi

echo ""
echo "=== InfluxDB: point count (last 10m) ==="
docker compose exec influxdb influx query \
  --org "${INFLUXDB_ORG}" \
  --token "${INFLUXDB_ADMIN_TOKEN}" \
  'from(bucket: "'"${INFLUXDB_BUCKET}"'")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "sensor_reading")
    |> count()'
