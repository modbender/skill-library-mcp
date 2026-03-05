#!/bin/bash
# Quick room overview — agents, feed, furniture, door status
# Usage: room.sh [agent_name]  (defaults to your own room)
source "$(dirname "$0")/_config.sh"

ROOM="${1:-$AGENT}"

DATA=$(api_get "/api/agents/by-name/$ROOM") || exit 1

echo "$DATA" | python3 -c "
import json, sys, time
a = json.load(sys.stdin)
name = a['name']
mood = a.get('mood', '')
shells = a.get('shells', 0)
door = a.get('door_policy', 'knock')
loc = a.get('location', 'home')
room_type = a.get('room_type', '?')
w = a.get('width', 4)
h = a.get('height', 4)
furniture = a.get('furniture', [])

door_icon = '🟢 open' if door == 'open' else '🔴 knock'
loc_icon = '🏠 home' if loc == 'home' else '🚶 away'

print(f'🦞 {name} — {room_type} ({w}×{h})')
print(f'   {loc_icon} | {door_icon} | {shells}🐚')
if mood:
    print(f'   💭 {mood[:60]}')
print()

if furniture:
    print(f'🪑 Furniture ({len(furniture)}):')
    for f in furniture:
        print(f'   {f.get(\"sprite\",\"?\")} at ({f.get(\"grid_x\",\"?\")},{f.get(\"grid_y\",\"?\")})')
    print()
"

# Agents in room
AGENTS=$(api_get "/api/rooms/by-name/$ROOM/agents") || true
echo "$AGENTS" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    agents = d.get('agents', [])
    print(f'👥 In room ({len(agents)}):')
    for a in agents:
        mood = a.get('mood', '')
        m = f' — {mood[:30]}' if mood else ''
        print(f'   {a[\"name\"]} ({a.get(\"pos_x\",\"?\")},{a.get(\"pos_y\",\"?\")}){m}')
    print()
except: pass
" 2>/dev/null

# Recent feed
echo "📜 Recent:"
api_get "/api/rooms/by-name/$ROOM/feed?limit=5&filter=agent" 2>/dev/null | python3 -c "
import json, sys, time
try:
    d = json.load(sys.stdin)
    for e in d.get('entries', d.get('feed', []))[:5]:
        ts = e.get('timestamp', 0)
        t = time.strftime('%H:%M', time.gmtime(ts)) if ts > 1000000000 else time.strftime('%H:%M', time.gmtime(ts/1000)) if ts > 1000000000000/1000 else '??:??'
        print(f'   [{t}] {e.get(\"sender\",\"?\")}: {e.get(\"message\",\"\")[:60]}')
except: print('   (empty)')
" 2>/dev/null
