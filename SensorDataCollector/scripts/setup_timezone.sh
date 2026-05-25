#!/usr/bin/env bash
# Set Raspberry Pi timezone and sync clock from the internet (NTP).
# Default: America/Chicago (CDT/CST).
set -euo pipefail

TZ_NAME="${1:-America/Chicago}"

usage() {
  cat <<EOF
Usage: sudo scripts/setup_timezone.sh [TIMEZONE]

Sets system timezone and enables NTP time sync over the internet.
Default timezone: America/Chicago (Chicago — CDT in summer, CST in winter).

Examples:
  sudo scripts/setup_timezone.sh
  sudo scripts/setup_timezone.sh America/Chicago

After running, restart the stack so containers use the same zone:
  docker compose up -d --force-recreate mqtt-publisher grafana
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "This script must run as root on the Pi:" >&2
  echo "  sudo scripts/setup_timezone.sh" >&2
  exit 1
fi

if ! command -v timedatectl >/dev/null 2>&1; then
  echo "timedatectl not found (systemd required)." >&2
  exit 1
fi

if ! timedatectl list-timezones | grep -qx "${TZ_NAME}"; then
  echo "Unknown timezone: ${TZ_NAME}" >&2
  echo "Pick one from: timedatectl list-timezones | grep -i chicago" >&2
  exit 1
fi

echo "Before:"
timedatectl status | sed -n '1,6p'

echo ""
echo "Setting timezone to ${TZ_NAME}..."
timedatectl set-timezone "${TZ_NAME}"

echo "Enabling NTP (internet time sync)..."
timedatectl set-ntp true

# Wait briefly for sync on first enable
sleep 2

echo ""
echo "After:"
timedatectl status | sed -n '1,6p'
echo ""
echo "Local time now: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""
echo "Add to .env on the project (if missing): TZ=${TZ_NAME}"
echo "Then recreate containers:"
echo "  cd ~/Projects/TempSensor/SensorDataCollector && docker compose up -d --force-recreate mqtt-publisher grafana"
