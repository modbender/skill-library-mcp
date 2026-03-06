#!/usr/bin/env bash
# snapshot.sh – Save a full timestamped snapshot of all MMAG memory layers
# Usage: bash snapshot.sh [--root <memory-root>]
#
# Creates: memory/working/snapshots/YYYY-MM-DDTHH-MM-SS.tar.gz
# Use this before a compression event to avoid losing context.

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

SNAPSHOTS_DIR="$ROOT/working/snapshots"
TIMESTAMP=$(date '+%Y-%m-%dT%H-%M-%S')
SNAPSHOT_FILE="$SNAPSHOTS_DIR/$TIMESTAMP.tar.gz"

if [ ! -d "$ROOT" ]; then
  echo "❌ Memory root not found: $ROOT" >&2
  echo "   Run: bash init.sh" >&2
  exit 1
fi

mkdir -p "$SNAPSHOTS_DIR"

echo "📸 Creating MMAG memory snapshot..."
echo "   Timestamp: $TIMESTAMP"
echo "   Layers: conversational, long-term, episodic, sensory, working (excl. snapshots/)"

# Create tarball of all layers, excluding the snapshots directory to avoid recursion
tar -czf "$SNAPSHOT_FILE" \
  --exclude="$ROOT/working/snapshots" \
  -C "$(dirname "$ROOT")" \
  "$(basename "$ROOT")" \
  2>/dev/null

SIZE=$(du -sh "$SNAPSHOT_FILE" | cut -f1)

echo ""
echo "✅ Snapshot saved: $SNAPSHOT_FILE ($SIZE)"

# Keep only the last 10 snapshots to avoid unbounded growth
SNAPSHOT_COUNT=$(find "$SNAPSHOTS_DIR" -name "*.tar.gz" | wc -l | tr -d ' ')
if [ "$SNAPSHOT_COUNT" -gt 10 ]; then
  echo "🧹 Pruning old snapshots (keeping latest 10)..."
  find "$SNAPSHOTS_DIR" -name "*.tar.gz" | sort | head -n $((SNAPSHOT_COUNT - 10)) | while read -r old; do
    rm -f "$old"
    echo "  🗑️  Removed: $old"
  done
fi
