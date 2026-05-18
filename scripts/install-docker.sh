#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo: sudo ./scripts/install-docker.sh"
  exit 1
fi

echo "Installing Docker and Docker Compose on $(uname -m) / $(. /etc/os-release && echo "${PRETTY_NAME}")..."

apt-get update
apt-get install -y ca-certificates curl gnupg

if ! apt-get install -y docker.io docker-compose-plugin; then
  echo "apt packages failed; trying Docker official install script..."
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sh /tmp/get-docker.sh
  rm -f /tmp/get-docker.sh
fi

systemctl enable docker
systemctl start docker

if id -u raspitemp &>/dev/null; then
  usermod -aG docker raspitemp
  DOCKER_USER=raspitemp
elif id -u pi &>/dev/null; then
  usermod -aG docker pi
  DOCKER_USER=pi
else
  DOCKER_USER="${SUDO_USER:-}"
  if [[ -n "${DOCKER_USER}" ]]; then
    usermod -aG docker "${DOCKER_USER}"
  fi
fi

echo ""
docker --version
docker compose version
echo ""
echo "Docker is installed and running."
if [[ -n "${DOCKER_USER:-}" ]]; then
  echo "User '${DOCKER_USER}' was added to the 'docker' group."
  echo "Log out and back in (or reboot), then run: docker compose up -d"
else
  echo "Log out and back in if you need to run docker without sudo."
fi
