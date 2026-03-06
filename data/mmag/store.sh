#!/usr/bin/env bash
# store.sh – Append a timestamped memory entry to a specific MMAG layer
# Usage: bash store.sh <layer> "<content>" [--label <label>] [--root <memory-root>]
#
# Layers: conversational | long-term | episodic | sensory | working

set -euo pipefail

VALID_LAYERS=("conversational" "long-term" "episodic" "sensory" "working")
ROOT="memory"
LAYER=""
CONTENT=""
LABEL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    conversational|long-term|episodic|sensory|working)
      LAYER="$1"
      shift
      ;;
    --label)
      LABEL="$2"
      shift 2
      ;;
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      if [ -z "$CONTENT" ]; then
        CONTENT="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$LAYER" ]; then
  echo "❌ Error: layer is required." >&2
  echo "   Usage: bash store.sh <layer> \"<content>\" [--label <label>]" >&2
  echo "   Layers: conversational | long-term | episodic | sensory | working" >&2
  exit 1
fi

if [ -z "$CONTENT" ]; then
  echo "❌ Error: content is required." >&2
  exit 1
fi

LAYER_DIR="$ROOT/$LAYER"
if [ ! -d "$LAYER_DIR" ]; then
  echo "⚠️  Layer directory not found. Run: bash init.sh" >&2
  exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%dT%H:%M:%S')
DATE=$(date '+%Y-%m-%d')

# Determine target file based on layer
case "$LAYER" in
  conversational)
    # Use today's session file
    SESSION_FILE="$LAYER_DIR/$DATE.md"
    TARGET_FILE="$SESSION_FILE"
    ;;
  episodic)
    # Daily log
    TARGET_FILE="$LAYER_DIR/$DATE.md"
    ;;
  long-term)
    LABEL_SLUG="${LABEL:-profile}"
    LABEL_SLUG=$(echo "$LABEL_SLUG" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
    TARGET_FILE="$LAYER_DIR/$LABEL_SLUG.md"
    ;;
  sensory)
    TARGET_FILE="$LAYER_DIR/context-$DATE.md"
    ;;
  working)
    TARGET_FILE="$LAYER_DIR/scratchpad.md"
    ;;
esac

# Write the entry
{
  if [ ! -f "$TARGET_FILE" ]; then
    # Create file with header
    echo "# ${LAYER^} Memory — $DATE"
    echo ""
  fi
  echo "## [$TIMESTAMP]${LABEL:+ — $LABEL}"
  echo ""
  echo "$CONTENT"
  echo ""
} >> "$TARGET_FILE"

echo "✅ Stored to $LAYER layer → $TARGET_FILE"
