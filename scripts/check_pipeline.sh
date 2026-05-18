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
source .env
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
echo "=== CSV (last 3 lines) ==="
tail -3 exports/mqtt_readings.csv 2>/dev/null || echo "(no CSV yet)"

echo ""
echo "=== InfluxDB: point count (last 10m) ==="
docker compose exec influxdb influx query \
  --org "${INFLUXDB_ORG}" \
  --token "${INFLUXDB_ADMIN_TOKEN}" \
  'from(bucket: "'"${INFLUXDB_BUCKET}"'")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "sensor_reading")
    |> count()'
