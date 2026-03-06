#!/usr/bin/env bash
# Clean up old versions (with confirmation)
set -euo pipefail

WORKSPACE="${1:?Usage: cleanup.sh <workspace> <piece-id> [keep-count]}"
PIECE_ID="${2:?Provide piece ID}"
KEEP="${3:-3}"  # Keep last N versions by default

VERSION_DIR="$WORKSPACE/versions/$PIECE_ID"

[[ -d "$VERSION_DIR" ]] || { echo "❌ No versions found for: $PIECE_ID"; exit 1; }

TOTAL=$(ls -1 "$VERSION_DIR" | wc -l | tr -d ' ')
DELETE=$((TOTAL - KEEP))

if [[ $DELETE -le 0 ]]; then
  echo "✅ Nothing to clean. Only $TOTAL versions exist, keeping $KEEP."
  exit 0
fi

echo "⚠️  About to delete $DELETE old version(s) of $PIECE_ID"
echo "   Keeping: last $KEEP versions"
echo ""
echo "Will delete:"
ls -1t "$VERSION_DIR" | tail -n "$DELETE" | while read f; do
  echo "   - $f"
done
echo ""
read -p "Confirm deletion? (yes/no): " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
  echo "❌ Cancelled."
  exit 1
fi

# Delete oldest versions
ls -1t "$VERSION_DIR" | tail -n "$DELETE" | while read f; do
  rm "$VERSION_DIR/$f"
  echo "🗑️  Deleted: $f"
done

echo ""
echo "✅ Cleanup complete. Remaining versions: $KEEP"
