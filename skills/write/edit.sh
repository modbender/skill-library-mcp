#!/usr/bin/env bash
# Edit a piece with ENFORCED versioning - copies before edit
set -euo pipefail

WORKSPACE="${1:?Usage: edit.sh <workspace> <piece-id> <new-content-file>}"
PIECE_ID="${2:?Provide piece ID}"
NEW_CONTENT="${3:?Provide path to new content file}"

PIECE_DIR="$WORKSPACE/pieces/$PIECE_ID"
CONTENT_FILE="$PIECE_DIR/content.md"
VERSION_DIR="$WORKSPACE/versions/$PIECE_ID"

[[ -d "$PIECE_DIR" ]] || { echo "❌ Piece not found: $PIECE_ID"; exit 1; }
[[ -f "$NEW_CONTENT" ]] || { echo "❌ New content file not found: $NEW_CONTENT"; exit 1; }

mkdir -p "$VERSION_DIR"

# Create version backup BEFORE edit
VERSION_NUM=$(ls -1 "$VERSION_DIR" 2>/dev/null | wc -l | tr -d ' ')
VERSION_NUM=$((VERSION_NUM + 1))
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION_FILE="$VERSION_DIR/v${VERSION_NUM}_${TIMESTAMP}.md"

# Copy current content to version archive
if [[ -s "$CONTENT_FILE" ]]; then
  cp "$CONTENT_FILE" "$VERSION_FILE"
  echo "📦 Backed up to: $VERSION_FILE"
fi

# Apply new content
cp "$NEW_CONTENT" "$CONTENT_FILE"

# Update metadata
jq --arg v "v${VERSION_NUM}_${TIMESTAMP}" --arg ts "$(date -Iseconds)" \
  '.versions += [{"version": $v, "timestamp": $ts}]' \
  "$PIECE_DIR/meta.json" > "$PIECE_DIR/meta.json.tmp" && \
  mv "$PIECE_DIR/meta.json.tmp" "$PIECE_DIR/meta.json"

WORD_COUNT=$(wc -w < "$CONTENT_FILE" | tr -d ' ')

echo "✅ Updated: $PIECE_ID"
echo "   Version: v$VERSION_NUM"
echo "   Words: $WORD_COUNT"
echo ""
echo "Restore previous: ./scripts/restore.sh $WORKSPACE $PIECE_ID v$((VERSION_NUM))"
