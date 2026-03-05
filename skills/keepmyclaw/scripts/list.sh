#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.keepmyclaw"
CONFIG_FILE="$CONFIG_DIR/config"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config not found. Run setup.sh first." >&2; exit 1
fi
source "$CONFIG_FILE"

AGENT="${1:-$CLAWKEEPER_AGENT_NAME}"

echo "=== Backups for ${AGENT} ==="
echo

TMPFILE="$(mktemp)"
trap 'rm -f "$TMPFILE"' EXIT

HTTP_CODE="$(curl -s -o "$TMPFILE" -w '%{http_code}' \
    -H "Authorization: Bearer ${CLAWKEEPER_API_KEY}" \
    "${CLAWKEEPER_API_URL}/v1/agents/${AGENT}/backups")"

if [[ "$HTTP_CODE" -lt 200 || "$HTTP_CODE" -ge 300 ]]; then
    echo "✗ API error (HTTP ${HTTP_CODE})" >&2
    cat "$TMPFILE" >&2
    exit 1
fi

python3 -c "
import sys, json
data = json.load(open('$TMPFILE'))
backups = data if isinstance(data, list) else data.get('backups', data.get('data', []))
if not backups:
    print('No backups found.')
    sys.exit(0)
for i, b in enumerate(backups, 1):
    bid = b.get('id', 'unknown')
    ts = b.get('created_at', b.get('timestamp', 'unknown'))
    size = b.get('size', 0)
    if size >= 1024*1024:
        size_str = f'{size/1024/1024:.1f} MB'
    elif size >= 1024:
        size_str = f'{size/1024:.1f} KB'
    elif size > 0:
        size_str = f'{size} B'
    else:
        size_str = ''
    line = f'  {i:3d}. {bid}  {ts}'
    if size_str:
        line += f'  ({size_str})'
    print(line)
print(f'\nTotal: {len(backups)} backup(s)')
"
