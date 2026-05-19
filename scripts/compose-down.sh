#!/usr/bin/env bash
# Stop publisher, plot latest CSV on the host (reliable on Pi), then tear down the stack.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ -f venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source venv/bin/activate
fi

echo "Stopping mqtt-publisher..."
docker compose stop mqtt-publisher

if compgen -G "exports/temp_reading_*.csv" > /dev/null; then
  echo "Plotting latest CSV..."
  python Visualize/sensorDataVisualizer.py \
    --export-dir exports \
    --presentation \
    --output-auto \
    || echo "WARNING: Host plot failed; check venv (pip install -r requirements.txt)." >&2
else
  echo "No active CSV in exports/ to plot."
fi

echo "Stopping remaining services..."
docker compose down "$@"
