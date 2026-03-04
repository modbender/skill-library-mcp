#!/bin/bash
# Report token usage to Ranking of Claws leaderboard
# Usage: ./report.sh [agent_name] [country] [tokens]
# Cron: */60 * * * * /path/to/report.sh MyAgent CH
set -euo pipefail

API_URL="https://rankingofclaws.angelstreet.io/api/report"
AGENT_NAME="${1:-${RANKING_AGENT_NAME:-$(hostname)}}"
COUNTRY="${2:-${RANKING_COUNTRY:-XX}}"
GATEWAY_ID=$(python3 -c "import hashlib,os;h=os.uname().nodename;print(hashlib.sha256(f'{h}-{os.environ.get(\"HOME\",\"\")}-openclaw'.encode()).hexdigest()[:16])" 2>/dev/null || echo "unknown")
STATE_FILE="${HOME}/.openclaw/ranking-of-claws-state.json"

TOKENS="${3:-}"

# Auto-detect from openclaw if no manual tokens
if [ -z "$TOKENS" ] && command -v openclaw &>/dev/null; then
  TOKENS=$(openclaw status 2>/dev/null | grep -oP '[\d,]+' | head -1 | tr -d ',' || echo "")
fi

if [ -z "$TOKENS" ] || [ "$TOKENS" = "0" ]; then
  echo "No tokens. Usage: ./report.sh MyAgent CH 50000"
  exit 0
fi

LAST=0
[ -f "$STATE_FILE" ] && LAST=$(python3 -c "import json;print(json.load(open('$STATE_FILE')).get('last',0))" 2>/dev/null || echo 0)

DELTA=$((TOKENS - LAST))
[ "$DELTA" -le 0 ] && echo "No new tokens (last=$LAST now=$TOKENS)" && exit 0

curl -sf -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"gateway_id\":\"$GATEWAY_ID\",\"agent_name\":\"$AGENT_NAME\",\"country\":\"$COUNTRY\",\"tokens_delta\":$DELTA,\"tokens_in_delta\":$((DELTA*40/100)),\"tokens_out_delta\":$((DELTA*60/100)),\"model\":\"mixed\"}" > /dev/null

mkdir -p "$(dirname "$STATE_FILE")"
echo "{\"last\":$TOKENS,\"at\":\"$(date -Iseconds)\"}" > "$STATE_FILE"
echo "Reported $DELTA tokens for $AGENT_NAME ($COUNTRY)"
