#!/bin/sh
# On up: archive any existing CSVs, then publish a new file.
# On down: stop publisher, plot latest CSV (PNG name matches CSV basename).
set -e

export MPLCONFIGDIR=/tmp/matplotlib

mkdir -p /app/Visualize/output

archive_csv() {
  python -c "from mqtt_csv_logger import archive_csv_exports; paths = archive_csv_exports(); print(f'Archived {len(paths)} CSV file(s)', flush=True)"
}

plot_latest_csv() {
  if ! ls /app/exports/*.csv >/dev/null 2>&1; then
    echo 'No active CSV to plot.' >&2
    return 0
  fi
  echo 'Generating presentation PNG...' >&2
  if python /app/Visualize/sensorDataVisualizer.py \
    --export-dir /app/exports \
    --presentation \
    --output-auto; then
    return 0
  fi
  echo 'ERROR: Visualizer failed inside container (see traceback above).' >&2
  return 1
}

archive_csv

term_handler() {
  if [ -n "${child:-}" ]; then
    kill -TERM "${child}" 2>/dev/null || true
    wait "${child}" 2>/dev/null || true
  fi
  plot_latest_csv || true
  exit 0
}

trap term_handler TERM INT

python -u mqtt_publisher.py &
child=$!
wait "${child}"
