#!/usr/bin/env bash
# Create new writing piece with ID and tracking
set -euo pipefail

WORKSPACE="${1:?Usage: new-piece.sh <workspace> <type> <title>}"
TYPE="${2:?Types: article, email, tweet, doc, book, other}"
TITLE="${3:?Provide a title}"

# Generate ID: type-YYYYMMDD-HHMMSS
ID="${TYPE}-$(date +%Y%m%d-%H%M%S)"
PIECE_DIR="$WORKSPACE/pieces/$ID"

mkdir -p "$PIECE_DIR"

# Create metadata
cat > "$PIECE_DIR/meta.json" << EOF
{
  "id": "$ID",
  "type": "$TYPE",
  "title": "$TITLE",
  "created": "$(date -Iseconds)",
  "status": "draft",
  "versions": [],
  "audits": []
}
EOF

# Create empty content file
touch "$PIECE_DIR/content.md"

# Create brief template
cat > "$PIECE_DIR/brief.md" << 'EOF'
# Brief

## Audience
<!-- Who reads this? -->

## Purpose
<!-- Inform, persuade, entertain, instruct? -->

## Tone
<!-- Formal, casual, technical? -->

## Length
<!-- Target word count or "short"/"long" -->

## Key Points
<!-- Must include these -->
EOF

# Update index
jq --arg id "$ID" --arg title "$TITLE" --arg type "$TYPE" \
  '.pieces += [{"id": $id, "title": $title, "type": $type, "created": now | todate}]' \
  "$WORKSPACE/index.json" > "$WORKSPACE/index.json.tmp" && \
  mv "$WORKSPACE/index.json.tmp" "$WORKSPACE/index.json"

echo "✅ Created piece: $ID"
echo "   $PIECE_DIR/content.md  — write here"
echo "   $PIECE_DIR/brief.md    — define requirements"
echo ""
echo "Edit with: ./scripts/edit.sh $WORKSPACE $ID"
