#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.keepmyclaw"
CONFIG_FILE="$CONFIG_DIR/config"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config not found. Run setup.sh first." >&2; exit 1
fi
source "$CONFIG_FILE"

KEEP="${1:-30}"

echo "=== ClawKeeper Prune ==="
echo "Keeping latest ${KEEP} backup(s) for ${CLAWKEEPER_AGENT_NAME}"
echo

TMPFILE="$(mktemp)"
trap 'rm -f "$TMPFILE"' EXIT

HTTP_CODE="$(curl -s -o "$TMPFILE" -w '%{http_code}' \
    -H "Authorization: Bearer ${CLAWKEEPER_API_KEY}" \
    "${CLAWKEEPER_API_URL}/v1/agents/${CLAWKEEPER_AGENT_NAME}/backups")"

if [[ "$HTTP_CODE" -lt 200 || "$HTTP_CODE" -ge 300 ]]; then
    echo "✗ API error (HTTP ${HTTP_CODE})" >&2
    cat "$TMPFILE" >&2
    exit 1
fi

# Get sorted backup IDs (oldest first)
IDS="$(python3 -c "
import sys, json
data = json.load(open('$TMPFILE'))
backups = data if isinstance(data, list) else data.get('backups', data.get('data', []))
# Sort by created_at ascending (oldest first)
backups.sort(key=lambda b: b.get('created_at', b.get('timestamp', '')))
for b in backups:
    print(b.get('id', ''))
" 2>/dev/null)"

if [[ -z "$IDS" ]]; then
    echo "No backups found."
    exit 0
fi

TOTAL="$(echo "$IDS" | wc -l | tr -d ' ')"
if [[ "$TOTAL" -le "$KEEP" ]]; then
    echo "Only ${TOTAL} backup(s) exist. Nothing to prune."
    exit 0
fi

DELETE_COUNT=$((TOTAL - KEEP))
TO_DELETE="$(echo "$IDS" | head -n "$DELETE_COUNT")"

echo "Deleting ${DELETE_COUNT} old backup(s)..."
ERRORS=0
while IFS= read -r bid; do
    [[ -z "$bid" ]] && continue
    DEL_CODE="$(curl -s -o /dev/null -w '%{http_code}' \
        -X DELETE \
        -H "Authorization: Bearer ${CLAWKEEPER_API_KEY}" \
        "${CLAWKEEPER_API_URL}/v1/agents/${CLAWKEEPER_AGENT_NAME}/backups/${bid}")"
    if [[ "$DEL_CODE" -ge 200 && "$DEL_CODE" -lt 300 ]]; then
        echo "  ✗ ${bid}"
    else
        echo "  ⚠ Failed to delete ${bid} (HTTP ${DEL_CODE})" >&2
        ERRORS=$((ERRORS + 1))
    fi
done <<< "$TO_DELETE"

echo
if [[ "$ERRORS" -gt 0 ]]; then
    echo "✓ Pruned with ${ERRORS} error(s). ${KEEP} backup(s) should remain."
else
    echo "✓ Pruned. ${KEEP} backup(s) remaining."
fi
