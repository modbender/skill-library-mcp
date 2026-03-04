#!/bin/bash
# Get agent status
# Usage: status.sh [agent_name]
source "$(dirname "$0")/_config.sh"

TARGET="${1:-$AGENT}"

RESP=$(api_get "/api/agents/by-name/$TARGET") || exit 1
TIERS_RESP=$(api_get "/api/economy/rooms" 2>/dev/null || echo '{"tiers":[]}')

AGENT_JSON="$RESP" TIERS_JSON="$TIERS_RESP" python3 - <<'PY'
import json, os, time

a = json.loads(os.environ["AGENT_JSON"])
try:
    tiers = json.loads(os.environ.get("TIERS_JSON", "{}") or "{}").get("tiers", [])
except Exception:
    tiers = []

print(f'🦞 {a["name"]}')
print(f'   Mood: {a.get("mood") or "—"}')
print(f'   Shells: {a.get("shells", 0)}🐚')
print(f'   Position: ({a.get("pos_x", 0)},{a.get("pos_y", 0)})')

room_type = a.get("room_type", "closet")
# Fallback values if /economy/rooms is unavailable
caps = {
    "closet": {"size": "4×4", "furn": 2, "vis": 3},
    "studio": {"size": "6×6", "furn": 4, "vis": 5},
    "standard": {"size": "8×8", "furn": 6, "vis": 8},
    "loft": {"size": "10×10", "furn": 15, "vis": 15},
    "penthouse": {"size": "12×12", "furn": 25, "vis": 25},
}.get(room_type, {"size": "4×4", "furn": 2, "vis": 3}).copy()

for tier in tiers:
    if tier.get("id") == room_type:
        w, h = tier.get("width"), tier.get("height")
        if w and h:
            caps["size"] = f"{w}×{h}"
        caps["furn"] = tier.get("maxFurniture", caps["furn"])
        caps["vis"] = tier.get("maxOccupants", caps["vis"])
        break
else:
    # If tier lookup fails, still use width/height from agent payload when present
    w, h = a.get("width"), a.get("height")
    if w and h:
        caps["size"] = f"{w}×{h}"

furniture = a.get("furniture", [])
print(f'   Room: {a.get("room_name", "—")} ({room_type} {caps["size"]})')
print(f'   Capacity: {len(furniture)}/{caps["furn"]} furniture, {caps["vis"]} max visitors')

if a.get("is_visiting"):
    owner = a.get("visiting_room_owner", "?")
    visit_started = a.get("visit_started_at")
    if visit_started:
        hours = (time.time() * 1000 - visit_started) / 3600000
        if hours >= 6:
            print(f'   ⚠️ Visiting {owner} for {hours:.1f}h — consider leaving!')
        else:
            print(f'   Visiting: {owner} ({hours:.1f}h)')
    else:
        print(f'   Visiting: {owner}')
PY
