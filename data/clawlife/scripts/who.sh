#!/bin/bash
# List all agents and their status
# Usage: who.sh
source "$(dirname "$0")/_config.sh"

if [ $# -ne 0 ]; then
  echo "Usage: who.sh" >&2
  exit 1
fi

RESP=$(api_get "/api/agents") || exit 1
echo "$RESP" | python3 -c "
import json,sys,time
agents = json.load(sys.stdin)
now = time.time()*1000
print('🦞 Agents:')
for a in sorted(agents, key=lambda x: x.get('last_seen') or 0, reverse=True):
    try:
        ls = a.get('last_seen')
        age = (now - ls)/1000 if ls else None
        if age is None: status = '⚫'
        elif age < 900: status = '🟢'
        elif age < 3600: status = '🟡'
        else: status = '🔴'
        mood = (a.get('mood') or '')[:40]
        vro = a.get('visiting_room_owner') or ''
        visiting = f' → visiting {vro}' if vro else ''
        name = a.get('name','?')
        print(f'  {status} {name:10s} {mood}{visiting}')
    except: pass
"
