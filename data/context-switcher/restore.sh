#!/usr/bin/env bash
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: current-context.json, snapshots/pre-switch-state.json, snapshots/dnd-log.json
#   Local files written: current-context.json

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTEXT_FILE="$SKILL_DIR/current-context.json"
SNAPSHOTS_DIR="$SKILL_DIR/snapshots"
DND_LOG="$SNAPSHOTS_DIR/dnd-log.json"
PRE_SWITCH="$SNAPSHOTS_DIR/pre-switch-state.json"

# Check if there's an active context to restore from
if [[ ! -f "$CONTEXT_FILE" ]]; then
  echo "No active context found. Nothing to restore." >&2
  exit 0
fi

# Read current mode safely
if command -v python3 &>/dev/null; then
  CURRENT_MODE=$(python3 -c "
import json, sys
try:
    with open('$CONTEXT_FILE') as f:
        data = json.load(f)
    print(data.get('current_mode', 'unknown'))
except Exception as e:
    print('unknown')
")
else
  CURRENT_MODE="unknown"
fi

echo "Restoring from $CURRENT_MODE mode..."

# Restore previous state if snapshot exists
if [[ -f "$PRE_SWITCH" ]]; then
  cp "$PRE_SWITCH" "$CONTEXT_FILE"
  echo "Previous context restored."
else
  # No snapshot — reset to null state
  cat > "$CONTEXT_FILE" <<EOF
{
  "current_mode": null,
  "previous_mode": "$CURRENT_MODE",
  "activated_at": null,
  "restore_at": null,
  "restore_trigger": null,
  "muted_channels": [],
  "session_notes": ""
}
EOF
fi

# If restoring from DND, show log of what came in
if [[ "$CURRENT_MODE" = "dnd" && -f "$DND_LOG" ]]; then
  echo ""
  echo "📋 While you were in DND, here's what came in:"
  cat "$DND_LOG"
  # Clear the log after showing
  echo "[]" > "$DND_LOG"
fi

echo ""
echo "✅ Restored. Notifications re-enabled. Welcome back."

exit 0
