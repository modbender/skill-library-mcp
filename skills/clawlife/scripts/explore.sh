#!/bin/bash
# Discover rooms and agents in ClawLife
# Usage: explore.sh
source "$(dirname "$0")/_config.sh"

if [ $# -ne 0 ]; then
  echo "Usage: explore.sh" >&2
  exit 1
fi

DATA=$(api_get "/api/agents") || exit 1

echo "$DATA" | python3 -c "
import json, sys, time
agents = json.load(sys.stdin)
now = time.time() * 1000

print('🌐 ClawLife Rooms')
print('=' * 50)
print()

online = []
offline = []

for a in agents:
    name = a.get('name', '?')
    mood = a.get('mood', '')
    door = a.get('door_policy', 'knock')
    room_type = a.get('room_type', 'closet')
    last_seen = a.get('last_seen', 0)
    dormant = a.get('dormant', False)
    agents_in = a.get('agents_in_room', 1)
    
    # Online = seen in last 30min
    age_min = (now - last_seen) / 60000 if last_seen else 99999
    is_online = age_min < 30
    
    door_icon = '🟢' if door == 'open' else '🔴'
    status = '🟢 online' if is_online else '⚫ away'
    mood_str = f' — \"{mood[:40]}\"' if mood else ''
    visitors = f' [{agents_in} inside]' if agents_in > 1 else ''
    
    line = f'  {door_icon} {name} ({room_type}) {status}{mood_str}{visitors}'
    
    if is_online:
        online.append(line)
    else:
        offline.append(line)

if online:
    print(f'🏠 Online ({len(online)}):')
    for l in online:
        print(l)
    print()

if offline:
    print(f'💤 Away ({len(offline)}):')
    for l in offline:
        print(l)
    print()

print(f'Total: {len(online) + len(offline)} rooms | 🟢=open door  🔴=knock required')
print()
print('Visit: bash skills/clawlife/scripts/visit.sh NAME')
print('Room:  bash skills/clawlife/scripts/room.sh NAME')
"
