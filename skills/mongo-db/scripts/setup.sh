#!/usr/bin/env bash
# Sets up a Python virtual environment and installs required dependencies
# for the mongo-db skill. Run once from the workspace root:
#   bash skills/mongo-db/scripts/setup.sh

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

echo "==> mongo-db skill setup"

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is not installed or not on PATH" >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  echo "==> Virtual environment already exists, updating packages"
fi

echo "==> Installing dependencies"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet pymongo

echo ""
echo "Setup complete. Dependencies installed:"
"$VENV_DIR/bin/pip" show pymongo | grep -E "^(Name|Version):"
echo ""
echo "Python interpreter: $VENV_DIR/bin/python3"
echo "Run the client with:"
echo "  $VENV_DIR/bin/python3 skills/mongo-db/scripts/mongo_client.py '{\"operation\":\"list_databases\"}'"
