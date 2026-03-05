#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/.openclaw/workspace/skills/social-push-semi/vendor/xhs"
PY="$BASE/.venv/bin/python"

if [[ ! -f "$BASE/requirements.txt" ]]; then
  echo "Missing requirements: $BASE/requirements.txt" >&2
  exit 2
fi

if [[ ! -x "$PY" ]]; then
  python3 -m venv "$BASE/.venv"
fi

source "$BASE/.venv/bin/activate"
python -m pip install -U pip setuptools wheel
pip install -r "$BASE/requirements.txt"

echo "vendor xhs ready: $BASE/.venv"
