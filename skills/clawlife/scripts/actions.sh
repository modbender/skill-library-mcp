#!/bin/bash
# List available actions in your room
# Usage: actions.sh
source "$(dirname "$0")/_config.sh"

if [ $# -ne 0 ]; then
  echo "Usage: actions.sh" >&2
  exit 1
fi

RAW=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$URL/api/agents/by-name/$AGENT/actions")
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

_RESP="$RESP" python3 -c '
import json,sys,os
d = json.loads(os.environ["_RESP"])
actions = d.get("available_actions", [])
for a in actions:
    aid = a.get("id","?")
    aname = a.get("name","?")
    sc = a.get("shell_cost")
    cost = " (%s🐚)" % sc if sc else ""
    pos = ""
    p = a.get("position")
    if p:
        pos = " @(%s,%s)" % (p.get("x",0), p.get("y",0))
    print("  %-25s %s%s%s" % (aid, aname, cost, pos))
if not actions:
    print("  (no actions available)")
' 2>/dev/null || { echo "❌ Server error" >&2; exit 1; }
