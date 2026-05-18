#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Create it first with: ./EnvironmentSetup/firstTimeSetup.sh"
    exit 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Activated virtual environment in $VENV_DIR"
