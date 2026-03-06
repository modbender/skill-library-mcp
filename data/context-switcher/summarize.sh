#!/usr/bin/env bash
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: current-context.json, snapshots/dnd-log.json
#   Local files written: none

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTEXT_FILE="$SKILL_DIR/current-context.json"
DND_LOG="$SKILL_DIR/snapshots/dnd-log.json"

if [[ ! -f "$CONTEXT_FILE" ]]; then
  echo "No active session found."
  exit 0
fi

if command -v python3 &>/dev/null; then
  python3 -c "
import json, sys
from datetime import datetime, timezone

try:
    with open('$CONTEXT_FILE') as f:
        ctx = json.load(f)
except Exception:
    print('Could not read context file.')
    sys.exit(0)

mode = ctx.get('current_mode', 'unknown')
activated = ctx.get('activated_at')
restore = ctx.get('restore_at')

print('Session Summary')
print('Mode: ' + str(mode))

if activated:
    try:
        start = datetime.fromisoformat(activated.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        elapsed = now - start
        minutes = int(elapsed.total_seconds() / 60)
        print('Active for: ' + str(minutes) + ' minutes')
    except Exception:
        pass

if restore:
    print('Scheduled restore: ' + str(restore))
"
fi

if [[ -f "$DND_LOG" ]]; then
  LOG_SIZE=$(wc -c < "$DND_LOG")
  if [[ "$LOG_SIZE" -gt 5 ]]; then
    echo ""
    echo "Logged during session:"
    cat "$DND_LOG"
  fi
fi

exit 0
