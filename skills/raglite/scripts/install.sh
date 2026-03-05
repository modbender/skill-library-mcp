#!/usr/bin/env bash
set -euo pipefail

# Minimal installer: creates a venv inside the skill folder and installs raglite.
# By default installs from PyPI. For TestPyPI, set RAGLITE_PIP_INDEX_URL.

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel >/dev/null

if [[ -n "${RAGLITE_PIP_INDEX_URL:-}" ]]; then
  python -m pip install --upgrade -i "$RAGLITE_PIP_INDEX_URL" --extra-index-url https://pypi.org/simple raglite-chromadb
else
  python -m pip install --upgrade raglite-chromadb
fi

echo "Installed raglite (raglite-chromadb) into $VENV_DIR"
