#!/usr/bin/env bash
# Optional manual plot; automatic PNG runs inside mqtt-publisher on compose down.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ -f venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source venv/bin/activate
fi

exec python Visualize/sensorDataVisualizer.py "$@"
