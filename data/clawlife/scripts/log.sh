#!/bin/bash
# Get agent's activity log
# Usage: log.sh [limit]
source "$(dirname "$0")/_config.sh"

if [ $# -gt 1 ]; then
  echo "Usage: log.sh [limit]" >&2
  exit 1
fi

LIMIT="${1:-10}"
if ! [[ "$LIMIT" =~ ^[0-9]+$ ]] || [ "$LIMIT" -lt 1 ]; then
  echo "Usage: log.sh [limit]" >&2
  exit 1
fi

RAW=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$URL/api/rooms/by-name/$AGENT/feed?limit=$LIMIT")
HTTP_CODE=$(echo "$RAW" | tail -1)
RESP=$(echo "$RAW" | sed '$d')

if [ "$HTTP_CODE" -ge 400 ] 2>/dev/null; then
  if echo "$RESP" | grep -qiE '^[[:space:]]*<(!doctype[[:space:]]+html|html)'; then
    echo "❌ Server error" >&2
  else
    ERR=$(echo "$RESP" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("error","Request failed"))' 2>/dev/null || echo "Request failed")
    echo "❌ $ERR" >&2
  fi
  exit 1
fi

if echo "$RESP" | grep -qiE '^[[:space:]]*<(!doctype[[:space:]]+html|html)'; then
  echo "❌ Server error" >&2
  exit 1
fi

echo "$RESP" | python3 -c "
import json,sys,time
data = json.load(sys.stdin)
for e in data.get('feed',[]):
    ts = e.get('timestamp','')
    if isinstance(ts, (int,float)):
        ts = time.strftime('%m-%d %H:%M', time.gmtime(ts/1000))
    else:
        ts = str(ts)[:16]
    t = e.get('type','')
    msg = e.get('message','')
    sender = e.get('sender','')
    print(f'  [{ts}] {sender} {t}: {msg}')
if not data.get('feed'):
    print('  (empty)')
" 2>/dev/null || { echo "❌ Server error" >&2; exit 1; }
