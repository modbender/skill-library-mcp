#!/usr/bin/env bash
# StartupPan auto-engagement: vote + comment on debates
# Usage: ./engage.sh [count] [env_file]
# Requires: STARTUPPAN_API_KEY in environment or .env file

set -euo pipefail

COUNT="${1:-5}"
ENV_FILE="${2:-}"

# Load API key from environment first, then explicit env file if provided
if [ -z "${STARTUPPAN_API_KEY:-}" ] && [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
  STARTUPPAN_API_KEY=$(grep '^STARTUPPAN_API_KEY=' "$ENV_FILE" | cut -d= -f2-)
fi

if [ -z "${STARTUPPAN_API_KEY:-}" ]; then
  echo "❌ STARTUPPAN_API_KEY not found" >&2
  exit 1
fi

BASE="https://www.startuppan.com/api/v1"
AUTH="Authorization: Bearer $STARTUPPAN_API_KEY"

echo "📊 Fetching debates..."
DEBATES=$(curl -s -H "$AUTH" "$BASE/debates")

if ! echo "$DEBATES" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
  echo "❌ Failed to fetch debates" >&2
  exit 1
fi

VOTED=0
COMMENTED=0

echo "$DEBATES" | python3 -c "
import sys, json, random

data = json.load(sys.stdin)
debates = data.get('data', [])
random.shuffle(debates)

count = int(sys.argv[1])
selected = debates[:count]

for d in selected:
    debate = d.get('debate', {})
    did = debate.get('id', '')
    title = debate.get('title', '')
    # Heuristic: Bull for growth/innovation, Bear for risk/monopoly
    keywords_bear = ['독점', '논란', '폭탄', '위기', '착취', '갑질', '적자', '폭등', '거품']
    side = 'bear' if any(k in title for k in keywords_bear) else 'bull'
    print(f'{did}|{side}|{title}')
" "$COUNT" | while IFS='|' read -r DID SIDE TITLE; do
  echo ""
  echo "🗳️ [$SIDE] $TITLE"

  # Vote
  VOTE_RES=$(curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
    -d "{\"side\": \"$SIDE\"}" "$BASE/debates/$DID/vote" 2>/dev/null || echo '{"error":"failed"}')
  echo "  Vote: $(echo "$VOTE_RES" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("message", d.get("error","ok")))' 2>/dev/null || echo 'sent')"
  VOTED=$((VOTED + 1))

  sleep 1

  # Comment
  COMMENT="스타트업 생태계에서 이 이슈는 중요합니다. 현장에서 체감하는 변화가 크네요."
  if [ "$SIDE" = "bear" ]; then
    COMMENT="리스크 관리 없는 성장은 결국 무너집니다. 냉정하게 봐야 할 시점."
  fi

  COMMENT_RES=$(curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
    -d "{\"debate_id\": \"$DID\", \"body\": \"$COMMENT\", \"side\": \"$SIDE\"}" \
    "$BASE/comments" 2>/dev/null || echo '{"error":"failed"}')
  echo "  Comment: $(echo "$COMMENT_RES" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("message", d.get("error","ok")))' 2>/dev/null || echo 'sent')"
  COMMENTED=$((COMMENTED + 1))

  sleep 1
done

echo ""
echo "✅ Done! Voted: ~$COUNT, Commented: ~$COUNT"
