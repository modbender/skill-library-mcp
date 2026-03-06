#!/usr/bin/env bash
set -euo pipefail

# 用法：
# bash scripts/analyze.sh <danmaku_csv> [meta_json] [outdir] [name]

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CSV_PATH="${1:-}"
META_PATH="${2:-}"
OUTDIR="${3:-$BASE_DIR/output}"
NAME="${4:-bilibili_danmaku}"
PY="${BASE_DIR}/.venv/bin/python"

if [[ -z "$CSV_PATH" ]]; then
  echo "Usage: bash scripts/analyze.sh <danmaku_csv> [meta_json] [outdir] [name]"
  exit 1
fi

if [[ ! -x "$PY" ]]; then
  echo "[error] venv python not found: $PY"
  echo "[hint] run: bash $BASE_DIR/scripts/ensure_env.sh"
  exit 2
fi

if [[ -n "$META_PATH" && -f "$META_PATH" ]]; then
  "$PY" "$BASE_DIR/scripts/analyze_danmaku.py" --csv "$CSV_PATH" --meta "$META_PATH" --outdir "$OUTDIR" --name "$NAME"
else
  "$PY" "$BASE_DIR/scripts/analyze_danmaku.py" --csv "$CSV_PATH" --outdir "$OUTDIR" --name "$NAME"
fi
