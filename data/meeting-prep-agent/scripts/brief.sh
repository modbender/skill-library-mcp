#!/bin/bash
# meeting-prep/scripts/brief.sh — Output a formatted briefing doc

set -euo pipefail

# --- CONFIG & ARGS ---
PREP_DIR="${PREP_DIR:-$HOME/.config/meeting-prep}"
HISTORY_FILE="$PREP_DIR/brief-history.json"
BRIEFS_DIR="$PREP_DIR/briefs"

TARGET="$1" # Can be a meeting ID or a path to a brief file
FORMAT="${2:---format markdown}"
shift 2

# --- FUNCTIONS ---

# Find the brief file path from a meeting ID
get_brief_path_from_id() {
  local event_id="$1"
  jq -r ".events[\"$event_id\"]" "$HISTORY_FILE"
}

# --- MAIN LOGIC ---
if [ -z "$TARGET" ]; then
  echo "Usage: $0 <meeting_id | brief_filepath> [--format <markdown|text|telegram>]"
  echo "Example: $0 event123"
  echo "Example: $0 $BRIEFS_DIR/2026-02-11-client-pitch.md"
  exit 1
fi

BRIEF_PATH=""
if [ -f "$TARGET" ]; then
  BRIEF_PATH="$TARGET"
else
  BRIEF_PATH=$(get_brief_path_from_id "$TARGET")
  if [ -z "$BRIEF_PATH" ] || [ "$BRIEF_PATH" == "null" ] || [ ! -f "$BRIEF_PATH" ]; then
    echo "Error: Brief not found for target '$TARGET'."
    echo "You can run prep first: prep.sh '$TARGET'"
    exit 1
  fi
fi

echo "Displaying brief: $BRIEF_PATH"
echo "Format: $FORMAT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# In a real implementation, you might use tools like `glow` for markdown,
# or format specifically for telegram's markdown variant.
# This placeholder just cats the file.
case "$FORMAT" in
  --format\ markdown)
    # For CLI, you might use a markdown renderer like glow
    if command -v glow &> /dev/null; then
      glow "$BRIEF_PATH"
    else
      cat "$BRIEF_PATH"
    fi
    ;;
  --format\ text)
    # Simple conversion placeholder
    sed 's/### /## /g; s/## /# /g; s/# /== /g; s/\*//g' "$BRIEF_PATH"
    ;;
  --format\ telegram)
    # Telegram uses a specific markdown subset.
    # This is a placeholder; a real script would be more careful.
    # e.g., escape characters like '-'
    cat "$BRIEF_PATH"
    ;;
  *)
    echo "Unknown format: $FORMAT"
    cat "$BRIEF_PATH"
    ;;
esac
