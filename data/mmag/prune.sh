#!/usr/bin/env bash
# prune.sh – Archive working memory into episodic and clear the scratchpad
# Usage: bash prune.sh [--root <memory-root>]
#
# At session end:
#   1. Appends working/scratchpad.md content to episodic/YYYY-MM-DD.md
#   2. Clears working/scratchpad.md
#   3. Removes other stale working/*.md files (keeps snapshots/)

set -euo pipefail

ROOT="memory"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

WORKING_DIR="$ROOT/working"
EPISODIC_DIR="$ROOT/episodic"
SCRATCHPAD="$WORKING_DIR/scratchpad.md"
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%dT%H:%M:%S')
EPISODIC_FILE="$EPISODIC_DIR/$DATE.md"

if [ ! -d "$WORKING_DIR" ]; then
  echo "❌ Working memory directory not found: $WORKING_DIR" >&2
  echo "   Run: bash init.sh" >&2
  exit 1
fi

if [ ! -d "$EPISODIC_DIR" ]; then
  mkdir -p "$EPISODIC_DIR"
fi

# Archive scratchpad → episodic
if [ -f "$SCRATCHPAD" ] && [ -s "$SCRATCHPAD" ]; then
  echo "📦 Archiving working memory → $EPISODIC_FILE"
  {
    if [ ! -f "$EPISODIC_FILE" ]; then
      echo "# Episodic Memory — $DATE"
      echo ""
    fi
    echo "## [$TIMESTAMP] Session Archive (from working memory)"
    echo ""
    cat "$SCRATCHPAD"
    echo ""
  } >> "$EPISODIC_FILE"
  echo "" > "$SCRATCHPAD"
  echo "  ✅ Scratchpad archived and cleared."
else
  echo "  ℹ️  Scratchpad is empty. Nothing to archive."
fi

# Remove other stale working .md files (not in snapshots/)
stale_files=$(find "$WORKING_DIR" -maxdepth 1 -name "*.md" ! -name "scratchpad.md" ! -name "README.md" 2>/dev/null || true)
if [ -n "$stale_files" ]; then
  echo "🗑️  Removing stale working files..."
  while IFS= read -r f; do
    rm -f "$f"
    echo "  🗑️  Removed: $f"
  done <<< "$stale_files"
fi

echo ""
echo "✅ Working memory pruned. Session complete."
