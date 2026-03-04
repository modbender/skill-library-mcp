#!/usr/bin/env bash
# stop.sh — Stop LLM Council background services

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SKILL_DIR}/pids"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

if [[ ! -f "$PID_FILE" ]]; then
  echo -e "${YELLOW}[council-brief]${NC} No PID file found — services may not be running."
  exit 0
fi

echo -e "${GREEN}[council-brief]${NC} Stopping LLM Council services..."

while IFS= read -r pid; do
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" && echo "  Killed PID $pid" || echo "  Failed to kill PID $pid"
  else
    echo "  PID $pid not running (already stopped)"
  fi
done < "$PID_FILE"

rm -f "$PID_FILE"
echo -e "${GREEN}[council-brief]${NC} Done."
