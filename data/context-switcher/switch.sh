#!/usr/bin/env bash
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: modes/*.md, current-context.json
#   Local files written: current-context.json, snapshots/pre-switch-state.json

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTEXT_FILE="$SKILL_DIR/current-context.json"
SNAPSHOTS_DIR="$SKILL_DIR/snapshots"
MODES_DIR="$SKILL_DIR/modes"

# Validate argument
if [[ $# -lt 1 ]]; then
  echo "Usage: switch.sh <mode> [duration_minutes]" >&2
  exit 1
fi

# Sanitize mode input — only allow known values
RAW_MODE="$1"
SAFE_MODE=$(printf '%s' "$RAW_MODE" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_-')

case "$SAFE_MODE" in
  work|focus|work_focus)
    MODE="work"
    MODE_FILE="$MODES_DIR/work.md"
    EMOJI="🧠"
    ;;
  personal|home|personal_time)
    MODE="personal"
    MODE_FILE="$MODES_DIR/personal.md"
    EMOJI="🏠"
    ;;
  creative|brainstorm|ideation)
    MODE="creative"
    MODE_FILE="$MODES_DIR/creative.md"
    EMOJI="🎨"
    ;;
  dnd|donotdisturb|do_not_disturb|silent)
    MODE="dnd"
    MODE_FILE=""
    EMOJI="🔕"
    ;;
  *)
    echo "Unknown mode: $SAFE_MODE. Valid modes: work, personal, creative, dnd" >&2
    exit 1
    ;;
esac

# Sanitize optional duration argument
DURATION_MINUTES=""
if [[ $# -ge 2 ]]; then
  RAW_DURATION="$2"
  # Only allow positive integers
  if [[ "$RAW_DURATION" =~ ^[0-9]+$ ]]; then
    DURATION_MINUTES="$RAW_DURATION"
  else
    echo "Invalid duration: must be a positive integer (minutes)" >&2
    exit 1
  fi
fi

# Create snapshots dir if needed
mkdir -p "$SNAPSHOTS_DIR"

# Save current state before switching
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [[ -f "$CONTEXT_FILE" ]]; then
  cp "$CONTEXT_FILE" "$SNAPSHOTS_DIR/pre-switch-state.json"
fi

# Calculate restore time if duration provided
RESTORE_AT=""
if [[ -n "$DURATION_MINUTES" ]]; then
  if command -v python3 &>/dev/null; then
    RESTORE_AT=$(python3 -c "
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
restore = now + timedelta(minutes=int('$DURATION_MINUTES'))
print(restore.strftime('%Y-%m-%dT%H:%M:%SZ'))
")
  fi
fi

# Write new context state
cat > "$CONTEXT_FILE" <<EOF
{
  "current_mode": "$MODE",
  "emoji": "$EMOJI",
  "activated_at": "$TIMESTAMP",
  "restore_at": "$RESTORE_AT",
  "restore_trigger": "$([ -n "$DURATION_MINUTES" ] && echo "timer_${DURATION_MINUTES}min" || echo "manual_or_calendar")",
  "duration_minutes": "$DURATION_MINUTES",
  "muted_channels": $([ "$MODE" = "dnd" ] && echo '["all"]' || ([ "$MODE" = "creative" ] && echo '["all"]' || ([ "$MODE" = "work" ] && echo '["personal","social","news"]' || echo '["work_slack","work_email","github"]'))),
  "session_notes": ""
}
EOF

# Output confirmation for OpenClaw to relay to user
echo "$EMOJI Switched to $MODE mode."

if [[ -n "$DURATION_MINUTES" ]]; then
  echo "Auto-restore in ${DURATION_MINUTES} minutes (at ${RESTORE_AT})."
fi

if [[ -n "$MODE_FILE" && -f "$MODE_FILE" ]]; then
  echo ""
  echo "Loading your $MODE profile..."
  cat "$MODE_FILE"
fi

exit 0
