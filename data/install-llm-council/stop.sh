#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${HOME}/workspace/llm-council"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) TARGET_DIR="${2:-$TARGET_DIR}"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -f "$TARGET_DIR/.llm-council.pid" ]]; then
  PID=$(cat "$TARGET_DIR/.llm-council.pid" || true)
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$TARGET_DIR/.llm-council.pid"
fi

# Safety cleanup for known process patterns
pkill -f "$TARGET_DIR/.venv/bin/python3 -m backend.main" 2>/dev/null || true
pkill -f "$TARGET_DIR/frontend/node_modules/.bin/vite" 2>/dev/null || true

echo "✅ LLM Council stopped (best-effort)."
