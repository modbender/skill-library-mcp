#!/bin/bash
set -euo pipefail

# logs.sh — View service logs
# Usage: logs.sh <service-name> [--follow] [--lines <n>]

[[ $# -lt 1 ]] && { echo "Usage: $0 <service-name> [--follow] [--lines <n>]"; exit 1; }

SERVICE_NAME="$1"; shift
LOG_DIR="$HOME/Library/Logs/toolguard/${SERVICE_NAME}"
LINES=50
FOLLOW=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --follow|-f) FOLLOW=true; shift ;;
    --lines|-n) LINES="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ ! -d "$LOG_DIR" ]]; then
  echo "No logs found for service '${SERVICE_NAME}'."
  exit 1
fi

echo "=== stdout (${LOG_DIR}/stdout.log) ==="
if [[ "$FOLLOW" == "true" ]]; then
  tail -n "$LINES" -f "$LOG_DIR/stdout.log" 2>/dev/null &
  STDOUT_PID=$!
  echo ""
  echo "=== stderr (${LOG_DIR}/stderr.log) ==="
  tail -n "$LINES" -f "$LOG_DIR/stderr.log" 2>/dev/null
  kill $STDOUT_PID 2>/dev/null || true
else
  tail -n "$LINES" "$LOG_DIR/stdout.log" 2>/dev/null || echo "  (empty)"
  echo ""
  echo "=== stderr (${LOG_DIR}/stderr.log) ==="
  tail -n "$LINES" "$LOG_DIR/stderr.log" 2>/dev/null || echo "  (empty)"
fi
