#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[smoke] python version: $(python3 -V)"

bash "$SKILL_DIR/setup.sh" >/dev/null

"$SKILL_DIR/venv/bin/python" -c "from src.config import load_config; from src.db import init_db; cfg=load_config(); init_db(); print('[smoke] db ok:', cfg.db_path)"

"$SKILL_DIR/bin/taxclaw" list >/dev/null || true

echo "[smoke] ok"
