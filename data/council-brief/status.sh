#!/usr/bin/env bash
# status.sh — Check if LLM Council services are running

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SKILL_DIR}/pids"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "=== Council Brief / LLM Council Status ==="

# Check by PID file
if [[ -f "$PID_FILE" ]]; then
  echo ""
  echo "PIDs from last install:"
  while IFS= read -r pid; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      CMD="$(ps -p "$pid" -o comm= 2>/dev/null || echo '?')"
      echo -e "  PID $pid: ${GREEN}RUNNING${NC} ($CMD)"
    else
      echo -e "  PID $pid: ${RED}NOT RUNNING${NC}"
    fi
  done < "$PID_FILE"
else
  echo -e "  ${YELLOW}No PID file — services have not been started or were stopped.${NC}"
fi

# Check ports directly
echo ""
echo "Port listeners:"
for port in 8001 4173 5173 5174; do
  if lsof -nP -iTCP:${port} -sTCP:LISTEN &>/dev/null; then
    PROC="$(lsof -nP -iTCP:${port} -sTCP:LISTEN 2>/dev/null | tail -1 | awk '{print $1}')"
    echo -e "  :${port} → ${GREEN}LISTENING${NC} ($PROC)"
  else
    echo -e "  :${port} → ${RED}nothing${NC}"
  fi
done

echo ""
