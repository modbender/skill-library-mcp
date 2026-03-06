#!/bin/bash
# meeting-prep/scripts/auto-prep.sh — Check upcoming calendar events and prep meetings that qualify

set -euo pipefail

# --- CONFIG & ARGS ---
PREP_DIR="${PREP_DIR:-$HOME/.config/meeting-prep}"
CONFIG_FILE="$PREP_DIR/config.json"
HISTORY_FILE="$PREP_DIR/brief-history.json"
LOG_FILE="$PREP_DIR/prep-log.json"
PREP_SCRIPT="$(dirname "$0")/prep.sh"

MORNING_BRIEF=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --morning-brief) MORNING_BRIEF=true; shift ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
done

# --- LOGGING ---
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] (auto-prep) $1"
}

# --- MAIN LOGIC ---
log "Starting auto-prep cycle."

# Load config values
if [ ! -f "$CONFIG_FILE" ]; then
  log "ERROR: Config file not found at $CONFIG_FILE. Run setup.sh."
  exit 1
fi
LOOKAHEAD_HOURS=$(jq -r '.calendar.lookahead_hours' "$CONFIG_FILE")
PREP_WINDOW_START_HOURS=$(jq -r '.auto_prep.prep_window_start_hours' "$CONFIG_FILE")
PREP_WINDOW_END_HOURS=$(jq -r '.auto_prep.prep_window_end_hours' "$CONFIG_FILE")
EXCLUDE_KEYWORDS=$(jq -r '.calendar.event_filters.exclude_keywords | join(",")' "$CONFIG_FILE")

log "Config loaded: lookahead=${LOOKAHEAD_HOURS}h, prep window=${PREP_WINDOW_START_HOURS}h-${PREP_WINDOW_END_HOURS}h"

# Get upcoming events from gog
# In a real script, this would be a live `gog` call.
# For this placeholder, we'll use a mock JSON structure.
MOCK_EVENTS_JSON=$(cat <<-EOF
{
  "events": [
    {
      "id": "event123",
      "summary": "Client Pitch: Acme Corp",
      "start": "$(date -v+4H --iso-8601=seconds)",
      "attendees": ["you@example.com", "john.doe@acme.com"]
    },
    {
      "id": "event456",
      "summary": "Internal Sync",
      "start": "$(date -v+6H --iso-8601=seconds)",
      "attendees": ["you@example.com", "teammate@example.com"]
    },
    {
      "id": "event789",
      "summary": "Partnership Intro: BigCorp",
      "start": "$(date -v+22H --iso-8601=seconds)",
      "attendees": ["you@example.com", "jane.smith@bigcorp.io"]
    },
    {
      "id": "eventalreadyprepped",
      "summary": "Follow-up: Synergy Inc",
      "start": "$(date -v+8H --iso-8601=seconds)",
      "attendees": ["you@example.com", "contact@synergy.inc"]
    }
  ]
}
EOF
)

# Mock the history file for the "already prepped" event
jq -n '.events = {"eventalreadyprepped": "/path/to/brief.md"}' > "$HISTORY_FILE"


log "Fetching upcoming events..."
# UPCOMING_EVENTS=$(gog calendar list --start now --end "+${LOOKAHEAD_HOURS}h" --json)
UPCOMING_EVENTS="$MOCK_EVENTS_JSON"

EVENT_COUNT=$(echo "$UPCOMING_EVENTS" | jq '.events | length')
log "Found $EVENT_COUNT events in the next ${LOOKAHEAD_HOURS} hours."

PROCESSED_COUNT=0
PREPPED_COUNT=0

# Loop through events and decide whether to prep
echo "$UPCOMING_EVENTS" | jq -c '.events[]' | while read -r event; do
  PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
  
  EVENT_ID=$(echo "$event" | jq -r '.id')
  SUMMARY=$(echo "$event" | jq -r '.summary')
  START_TIME=$(echo "$event" | jq -r '.start')
  
  log "Processing event: '$SUMMARY' ($EVENT_ID)"

  # 1. Check if already prepped
  if jq -e ".events[\"$EVENT_ID\"]" "$HISTORY_FILE" > /dev/null; then
    log "  -> Skipping: Already prepped."
    continue
  fi

  # 2. Check time window
  EVENT_START_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S%z" "$START_TIME" "+%s")
  NOW_TS=$(date "+%s")
  HOURS_TO_EVENT=$(((EVENT_START_TS - NOW_TS) / 3600))
  
  if (( HOURS_TO_EVENT > PREP_WINDOW_START_HOURS || HOURS_TO_EVENT < PREP_WINDOW_END_HOURS )); then
    log "  -> Skipping: Event is at ${HOURS_TO_EVENT}h, outside window (${PREP_WINDOW_START_HOURS}h-${PREP_WINDOW_END_HOURS}h)."
    continue
  fi
  
  # 3. Check for external attendees (simple placeholder)
  HAS_EXTERNAL=$(echo "$event" | jq '[.attendees[] | select(contains("@example.com") | not)] | length > 0')
  if [ "$HAS_EXTERNAL" != "true" ]; then
    log "  -> Skipping: No external attendees found."
    continue
  fi
  
  # 4. Check for exclusion keywords
  SHOULD_EXCLUDE=false
  for keyword in $(echo "$EXCLUDE_KEYWORDS" | tr ',' ' '); do
    if [[ "${SUMMARY,,}" == *"$keyword"* ]]; then
      log "  -> Skipping: Summary contains excluded keyword '$keyword'."
      SHOULD_EXCLUDE=true
      break
    fi
  done
  [ "$SHOULD_EXCLUDE" = "true" ] && continue
  
  # If all checks pass, run prep
  log "  -> QUALIFIED. Running prep script for event ID: $EVENT_ID"
  PREPPED_COUNT=$((PREPPED_COUNT + 1))
  
  # Call the main prep script
  if bash "$PREP_SCRIPT" "$EVENT_ID"; then
    log "  -> Successfully prepped '$SUMMARY'."
  else
    log "  -> ERROR: Prep script failed for '$SUMMARY'."
  fi
done

log "Auto-prep cycle finished. Processed $PROCESSED_COUNT events, prepped $PREPPED_COUNT new meetings."

# Clean up mock history file
# In a real run, you wouldn't do this
[ -f "$HISTORY_FILE" ] && rm "$HISTORY_FILE"
echo '{"events":{}}' > "$HISTORY_FILE"

exit 0
