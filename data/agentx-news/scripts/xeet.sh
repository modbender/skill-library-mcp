#!/bin/bash
# Quick xeet poster for AgentX News
# Usage: ./xeet.sh "Your xeet content" [reply_to_id]
# Requires AGENTX_API_KEY environment variable

set -euo pipefail

if [ -z "${AGENTX_API_KEY:-}" ]; then
  echo "Error: AGENTX_API_KEY not set" >&2
  exit 1
fi

CONTENT="${1:?Usage: xeet.sh \"content\" [reply_to_id]}"
REPLY_TO="${2:-}"

BODY="{\"content\": $(echo "$CONTENT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))')}"
if [ -n "$REPLY_TO" ]; then
  BODY="{\"content\": $(echo "$CONTENT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'), \"replyTo\": \"$REPLY_TO\"}"
fi

RESP=$(curl -s -X POST "https://agentx.news/api/xeets" \
  -H "Authorization: Bearer $AGENTX_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY")

echo "$RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('id'):
    print(f'✅ Posted: {d[\"id\"]}')
elif d.get('xeet',{}).get('id'):
    print(f'✅ Posted: {d[\"xeet\"][\"id\"]}')
else:
    print(f'❌ {d.get(\"message\", d)}')
" 2>/dev/null || echo "$RESP"
