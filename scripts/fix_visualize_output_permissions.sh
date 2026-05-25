#!/usr/bin/env bash
# Docker writes Visualize/output as root; host plotting needs user ownership.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/Visualize/output"
REF="${ROOT}/exports"

mkdir -p "${OUT}"

if [[ -w "${OUT}" ]]; then
  exit 0
fi

owner="$(id -u):$(id -g)"
if [[ -d "${REF}" ]]; then
  ref_owner="$(stat -c '%u:%g' "${REF}" 2>/dev/null || true)"
  if [[ -n "${ref_owner}" ]]; then
    owner="${ref_owner}"
  fi
fi

echo "Fixing permissions on Visualize/output (was created by Docker as root)..." >&2

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  docker run --rm -v "${OUT}:/out" alpine:3.20 chown -R "${owner}" /out
elif [[ "$(id -u)" -eq 0 ]]; then
  chown -R "${owner}" "${OUT}"
else
  sudo chown -R "${owner}" "${OUT}"
fi
