#!/usr/bin/env bash
set -e

# Setup virtual environment and install dependencies
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$BASE_DIR")"
VENV_DIR="$SKILL_ROOT/.venv"

echo "Setup: Creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Setup: Installing dependencies..."
"$VENV_DIR/bin/pip" install -U pip
"$VENV_DIR/bin/pip" install -r "$SKILL_ROOT/requirements.txt"

echo "Setup: Done. Use '$VENV_DIR/bin/python3 scripts/cf_manager.py' to run."
