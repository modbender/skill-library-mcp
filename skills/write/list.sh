#!/usr/bin/env bash
# List all pieces and their versions
set -euo pipefail

WORKSPACE="${1:?Usage: list.sh <workspace> [piece-id]}"
PIECE_ID="${2:-}"

if [[ -n "$PIECE_ID" ]]; then
  # Show specific piece details
  PIECE_DIR="$WORKSPACE/pieces/$PIECE_ID"
  [[ -d "$PIECE_DIR" ]] || { echo "❌ Piece not found: $PIECE_ID"; exit 1; }
  
  echo "📄 $PIECE_ID"
  jq -r '"   Title: \(.title)\n   Type: \(.type)\n   Status: \(.status)\n   Created: \(.created)"' "$PIECE_DIR/meta.json"
  echo ""
  echo "   Versions:"
  ls -1 "$WORKSPACE/versions/$PIECE_ID" 2>/dev/null | while read v; do
    echo "     - $v"
  done || echo "     (none)"
  echo ""
  echo "   Audits:"
  ls -1 "$WORKSPACE/audits/$PIECE_ID" 2>/dev/null | while read a; do
    echo "     - $a"
  done || echo "     (none)"
else
  # List all pieces
  echo "📚 Writing Pieces"
  echo ""
  jq -r '.pieces[] | "  [\(.id)] \(.title) (\(.type))"' "$WORKSPACE/index.json"
  echo ""
  echo "Details: ./scripts/list.sh $WORKSPACE <piece-id>"
fi
