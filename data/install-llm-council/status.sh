#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${HOME}/workspace/llm-council"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) TARGET_DIR="${2:-$TARGET_DIR}"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo "LLM Council status"
echo "- Dir: $TARGET_DIR"

if [[ -f "$TARGET_DIR/.llm-council.pid" ]]; then
  PID=$(cat "$TARGET_DIR/.llm-council.pid" || true)
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "- Launcher PID: $PID (running)"
  else
    echo "- Launcher PID file exists but process not running"
  fi
else
  echo "- No launcher PID file"
fi

echo "- Listening ports (common):"
ss -ltnp 2>/dev/null | rg ':8001|:8002|:4173|:4174|:4175|:5173|:5174' || true

echo "- Quick checks:"
for url in http://127.0.0.1:8001/ http://127.0.0.1:8002/ http://127.0.0.1:4173/ http://127.0.0.1:4175/ http://127.0.0.1:5173/ http://127.0.0.1:5174/; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)
  echo "  $url -> $code"
done
