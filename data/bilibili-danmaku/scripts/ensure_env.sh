#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$BASE_DIR/.venv"
REQ_FILE="$BASE_DIR/requirements.txt"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[info] creating venv: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

echo "[info] upgrading pip/setuptools/wheel"
"$PIP" install -U pip setuptools wheel >/dev/null

echo "[info] installing requirements"
"$PIP" install -r "$REQ_FILE"

echo "[ok] env ready"
echo "[ok] python: $PY"
