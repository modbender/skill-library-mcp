#!/bin/bash
set -euo pipefail

API="https://api.lifx.com/v1"
TOKEN="${LIFX_TOKEN:-}"

# Load token from skill directory if not set
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -z "$TOKEN" && -f "$SKILL_DIR/.lifx-token" ]]; then
  TOKEN="$(cat "$SKILL_DIR/.lifx-token")"
fi

usage() {
  cat <<EOF
Usage: lifx-api.sh [--token TOKEN] <command> [args...]

Commands:
  discover                    Show lights by room with status
  list                        List all lights (JSON)
  groups                      List unique groups with IDs
  scenes                      List all scenes (JSON)
  toggle <selector>           Toggle light(s)
  state <selector> [json]     Set state (JSON body)
  scene <uuid>                Activate a scene
  group-toggle <group_id>     Toggle all lights in a group

Options:
  --token TOKEN               LIFX API token (or set LIFX_TOKEN env)
EOF
  exit 1
}

# Parse --token flag
while [[ $# -gt 0 ]]; do
  case "$1" in
    --token) TOKEN="$2"; shift 2 ;;
    --help|-h) usage ;;
    *) break ;;
  esac
done

[[ -z "$TOKEN" ]] && { echo "Error: LIFX_TOKEN not set and --token not provided" >&2; exit 1; }
[[ $# -lt 1 ]] && usage

CMD="$1"; shift

encode_selector() {
  echo "$1" | sed 's/|/%7C/g'
}

api() {
  local method="$1" endpoint="$2"; shift 2
  local url="${API}${endpoint}"
  local http_code
  local tmpfile
  tmpfile=$(mktemp)
  
  http_code=$(curl -s -o "$tmpfile" -w "%{http_code}" \
    -X "$method" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "$@" \
    "$url")
  
  local body
  body=$(<"$tmpfile")
  rm -f "$tmpfile"
  
  if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "$body"
    return 0
  else
    echo "HTTP $http_code: $body" >&2
    return 1
  fi
}

case "$CMD" in
  discover)
    api GET /lights/all | python3 -c "
import json, sys
lights = json.load(sys.stdin)
groups = {}
for l in lights:
    g = l['group']['name']
    if g not in groups: groups[g] = []
    groups[g].append(l)
for name in sorted(groups):
    print(f'📍 {name}')
    for l in groups[name]:
        power = '🟢' if l['power'] == 'on' else '⚫'
        bri = int(l.get('brightness', 0) * 100)
        c = l.get('color', {})
        if c.get('saturation', 0) < 0.1:
            color = f\"kelvin:{c.get('kelvin', 3500)}\"
        else:
            color = f\"hue:{int(c.get('hue', 0))} sat:{c.get('saturation', 0):.1f}\"
        mz = ' [multizone]' if l['product']['capabilities'].get('has_multizone') else ''
        print(f\"  {power} {l['label']} — {bri}% {color}{mz}\")
    print()
"
    ;;
  list)
    api GET /lights/all
    ;;
  groups)
    api GET /lights/all | jq -r '[.[] | {name: .group.name, id: .group.id}] | unique_by(.id) | .[] | "\(.id)\t\(.name)"'
    ;;
  scenes)
    api GET /scenes
    ;;
  toggle)
    [[ $# -lt 1 ]] && { echo "Usage: toggle <selector>" >&2; exit 1; }
    sel=$(encode_selector "$1")
    api POST "/lights/${sel}/toggle"
    ;;
  state)
    [[ $# -lt 1 ]] && { echo "Usage: state <selector> [json_body]" >&2; exit 1; }
    sel=$(encode_selector "$1"); shift
    body="${1:-{\}}"
    api PUT "/lights/${sel}/state" -d "$body"
    ;;
  scene)
    [[ $# -lt 1 ]] && { echo "Usage: scene <uuid>" >&2; exit 1; }
    api PUT "/scenes/scene_id:${1}/activate"
    ;;
  group-toggle)
    [[ $# -lt 1 ]] && { echo "Usage: group-toggle <group_id>" >&2; exit 1; }
    api POST "/lights/group_id:${1}/toggle"
    ;;
  *)
    echo "Unknown command: $CMD" >&2
    usage
    ;;
esac
