#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "Setup complete. Activate with: source scripts/activate_venv.sh"
echo "Configure sensors in publisher/sensor/ds18b20_reader.py (SENSOR_MAP)."
