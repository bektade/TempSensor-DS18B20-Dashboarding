#!/usr/bin/env bash
# Prompt for TestUnit + Serial Number, save to .env, then start the stack.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

set_env_key() {
  local key="$1"
  local value="$2"
  local tmp
  tmp="$(mktemp)"
  if grep -q "^${key}=" .env 2>/dev/null; then
    grep -v "^${key}=" .env > "${tmp}" || true
    printf '%s=%s\n' "${key}" "${value}" >> "${tmp}"
    mv "${tmp}" .env
  else
    printf '%s=%s\n' "${key}" "${value}" >> .env
  fi
}

echo "Enter run labels for the CSV / PNG file name:"
echo "  Format: date_time_TestUnit_serialNumber.csv"
echo ""

read -r -p "TestUnit (e.g. Pro18.1): " TEST_UNIT
read -r -p "Serial Number (e.g. 73216-0098): " SERIAL_NUMBER

if [[ -z "${TEST_UNIT}" ]]; then
  echo "TestUnit is required." >&2
  exit 1
fi
if [[ -z "${SERIAL_NUMBER}" ]]; then
  echo "Serial Number is required." >&2
  exit 1
fi

set_env_key TEST_UNIT "${TEST_UNIT}"
set_env_key SERIAL_NUMBER "${SERIAL_NUMBER}"

echo ""
echo "CSV name will be like: $(date +%Y-%m-%d)_$(date +%I%M%p)_${TEST_UNIT}_${SERIAL_NUMBER}.csv"
echo "Starting stack..."
echo ""

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
else
  COMPOSE=(docker-compose)
fi

if [[ "${EUID}" -eq 0 ]]; then
  "${COMPOSE[@]}" up -d --build "$@"
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  "${COMPOSE[@]}" up -d --build "$@"
else
  sudo "${COMPOSE[@]}" up -d --build "$@"
fi
