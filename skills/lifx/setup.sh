#!/bin/bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
API="https://api.lifx.com/v1"

usage() {
  echo "Usage: setup.sh <LIFX_TOKEN>"
  echo ""
  echo "Discovers your LIFX lights, groups, and scenes, then generates"
  echo "a personalized SKILL.md with your device context."
  echo ""
  echo "Get your token at: https://cloud.lifx.com/settings"
  exit 1
}

[[ $# -lt 1 ]] && usage
TOKEN="$1"

echo "🔍 Discovering lights..."
LIGHTS=$(curl -sf -H "Authorization: Bearer $TOKEN" "$API/lights/all") || {
  echo "❌ Failed to connect to LIFX API. Check your token." >&2
  exit 1
}

echo "🔍 Discovering scenes..."
SCENES=$(curl -sf -H "Authorization: Bearer $TOKEN" "$API/scenes") || {
  echo "❌ Failed to fetch scenes." >&2
  exit 1
}

# Save token
echo "$TOKEN" > "$SKILL_DIR/.lifx-token"
chmod 600 "$SKILL_DIR/.lifx-token"
echo "🔑 Token saved to .lifx-token"

# Generate device context
CONTEXT=$(python3 -c "
import json, sys

lights = json.loads(sys.argv[1])
scenes = json.loads(sys.argv[2])

location = lights[0]['location']['name'] if lights else 'Unknown'

# Gather groups
groups = {}
for l in lights:
    g = l['group']
    if g['id'] not in groups:
        groups[g['id']] = {'name': g['name'], 'lights': []}
    mz = l['product']['capabilities'].get('has_multizone', False)
    groups[g['id']]['lights'].append({
        'label': l['label'],
        'id': l['id'],
        'multizone': mz,
        'product': l['product']['name']
    })

total = len(lights)
num_groups = len(groups)
num_scenes = len(scenes)
has_multizone = any(l['multizone'] for g in groups.values() for l in g['lights'])

lines = []
if has_multizone:
    mz_lights = [l for g in groups.values() for l in g['lights'] if l['multizone']]
    lines.append(f'Location: **{location}** — {total} lights, {num_groups} rooms, {num_scenes} scenes, {len(mz_lights)} multi-zone device(s).')
else:
    lines.append(f'Location: **{location}** — {total} lights, {num_groups} rooms, {num_scenes} scenes.')

lines.append('')
lines.append('### Rooms and Lights')
lines.append('')
lines.append('| Room | Group ID | Lights |')
lines.append('|------|----------|--------|')
for gid, g in sorted(groups.items(), key=lambda x: x[1]['name']):
    light_list = ', '.join(
        f\"{l['label']}{'  ⚡multizone' if l['multizone'] else ''}\"
        for l in g['lights']
    )
    lines.append(f\"| {g['name']} | \`{gid}\` | {light_list} |\")

lines.append('')
lines.append('### Scenes')
lines.append('')
lines.append('| Scene | UUID |')
lines.append('|-------|------|')
for s in sorted(scenes, key=lambda x: x.get('name', '')):
    lines.append(f\"| {s['name']} | \`{s['uuid']}\` |\")

if has_multizone:
    lines.append('')
    lines.append('### Multi-zone Devices')
    lines.append('')
    for l in mz_lights:
        lines.append(f\"- **{l['label']}** (\`id:{l['id']}\`) — supports zone-based gradients\")

print('\n'.join(lines))
" "$LIGHTS" "$SCENES")

# Generate SKILL.md from template
TEMPLATE=$(cat "$SKILL_DIR/SKILL.md.template")
echo "${TEMPLATE/\{\{DEVICE_CONTEXT\}\}/$CONTEXT}" > "$SKILL_DIR/SKILL.md"

# Count what we found
NUM_LIGHTS=$(echo "$LIGHTS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
NUM_SCENES=$(echo "$SCENES" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

echo ""
echo "✅ Setup complete!"
echo "   📍 $(echo "$LIGHTS" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['location']['name'])")"
echo "   💡 $NUM_LIGHTS lights discovered"
echo "   🎨 $NUM_SCENES scenes found"
echo "   📄 SKILL.md generated with your device context"
echo ""
echo "Install the skill by copying this directory into your OpenClaw skills folder:"
echo "   cp -r $SKILL_DIR /path/to/openclaw/workspace/skills/lifx"
