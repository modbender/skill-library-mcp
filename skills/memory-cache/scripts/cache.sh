#!/usr/bin/env bash
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/../.venv"
REQ_FILE="$BASE_DIR/../requirements.txt"
PYTHON_SCRIPT="$BASE_DIR/cache_manager.py"

if [ ! -d "$VENV_DIR" ]; then
    echo "Initializing environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install -q --upgrade pip
    pip install -q -r "$REQ_FILE"
    echo "Environment ready."
else
    source "$VENV_DIR/bin/activate"
fi

python3 "$PYTHON_SCRIPT" "$@"
