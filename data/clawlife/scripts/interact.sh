#!/bin/bash
# Interact with furniture (perform an action)
# Usage: interact.sh <action_id>
# List available actions: actions.sh
source "$(dirname "$0")/_config.sh"

ACTION="${1:?Usage: interact.sh <action_id>}"
ESC_ACTION=$(json_escape "$ACTION")
RESP=$(api_call POST "/api/agents/by-name/$AGENT/action" "{\"action_id\":\"$ESC_ACTION\"}") || exit 1
echo "$RESP" | python3 -c "
import json,sys
d = json.load(sys.stdin)
r = d.get('result',{})
print(f'✨ {r.get(\"message\", r.get(\"description\", \"Done\"))}')
shells = r.get('shells_earned') or r.get('shell_cost')
if shells: print(f'   {shells}🐚')
" 2>/dev/null || echo "✨ Done"
