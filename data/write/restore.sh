#!/usr/bin/env bash
# Restore a previous version of a piece
set -euo pipefail

WORKSPACE="${1:?Usage: restore.sh <workspace> <piece-id> <version>}"
PIECE_ID="${2:?Provide piece ID}"
VERSION="${3:?Provide version (e.g., v1, v2)}"

PIECE_DIR="$WORKSPACE/pieces/$PIECE_ID"
VERSION_DIR="$WORKSPACE/versions/$PIECE_ID"
CONTENT_FILE="$PIECE_DIR/content.md"

[[ -d "$PIECE_DIR" ]] || { echo "❌ Piece not found: $PIECE_ID"; exit 1; }

# Find version file
VERSION_FILE=$(ls -1 "$VERSION_DIR" 2>/dev/null | grep "^${VERSION}_" | head -1)
[[ -n "$VERSION_FILE" ]] || { echo "❌ Version not found: $VERSION"; exit 1; }

FULL_PATH="$VERSION_DIR/$VERSION_FILE"

# Backup current before restore (meta-version)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$VERSION_DIR/pre-restore_${TIMESTAMP}.md"
cp "$CONTENT_FILE" "$BACKUP_FILE"

# Restore
cp "$FULL_PATH" "$CONTENT_FILE"

echo "✅ Restored $PIECE_ID to $VERSION"
echo "   Previous saved as: pre-restore_${TIMESTAMP}.md"
echo "   Current content now matches: $VERSION_FILE"
