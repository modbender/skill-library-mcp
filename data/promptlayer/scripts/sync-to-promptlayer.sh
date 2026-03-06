#!/usr/bin/env bash
# Syncs recent session history to PromptLayer
# Run periodically via cron to log agent activity
set -euo pipefail

API_KEY="${PROMPTLAYER_API_KEY:?Set PROMPTLAYER_API_KEY}"
API_URL="https://api.promptlayer.com"
STATE_FILE="/home/ubuntu/clawd/scripts/.pl-sync-state.json"

# Initialize state file if missing
if [[ ! -f "$STATE_FILE" ]]; then
  echo '{"last_synced":"2026-02-18T00:00:00Z"}' > "$STATE_FILE"
fi

LAST_SYNCED=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['last_synced'])")
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "Syncing since: $LAST_SYNCED"
echo "Current time: $NOW"

# Update state immediately
python3 -c "import json; json.dump({'last_synced': '$NOW'}, open('$STATE_FILE', 'w'))"

echo "State updated. Agent will handle the actual logging via sessions_history."
echo "LAST_SYNCED=$LAST_SYNCED"
echo "NOW=$NOW"
