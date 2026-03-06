#!/usr/bin/env bash
# retrieve.sh – Search memories from one or all MMAG layers
# Usage: bash retrieve.sh <layer|all> [query] [--root <memory-root>]
#
# Layers: conversational | long-term | episodic | sensory | working | all
#
# Encrypted files (.md.enc) are transparently decrypted via decrypt.sh --stdout.
# Set MMAG_KEY or MMAG_KEY_FILE before searching encrypted layers.

set -euo pipefail

ROOT="memory"
LAYER=""
QUERY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      if [ -z "$LAYER" ]; then
        LAYER="$1"
      elif [ -z "$QUERY" ]; then
        QUERY="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$LAYER" ]; then
  echo "❌ Error: layer is required." >&2
  echo "   Usage: bash retrieve.sh <layer|all> [query]" >&2
  echo "   Layers: conversational | long-term | episodic | sensory | working | all" >&2
  exit 1
fi

VALID_LAYERS=("conversational" "long-term" "episodic" "sensory" "working")

search_layer() {
  local layer="$1"
  local dir="$ROOT/$layer"

  if [ ! -d "$dir" ]; then
    echo "⚠️  Layer not found: $layer (run bash init.sh)" >&2
    return
  fi

  local SKILL_DIR
  SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

  # Collect both plaintext and encrypted files
  local files
  files=$( (find "$dir" -name "*.md" ! -name "README.md" 2>/dev/null; find "$dir" -name "*.md.enc" 2>/dev/null) | sort || true)

  if [ -z "$files" ]; then
    echo "  (no entries in $layer)"
    return
  fi

  echo "─── $layer ───────────────────────────────────────"

  while IFS= read -r f; do
    local content label
    if [[ "$f" == *.md.enc ]]; then
      content=$(bash "$SKILL_DIR/decrypt.sh" --stdout --file "$f" 2>/dev/null || echo "[encrypted — set MMAG_KEY to decrypt]")
      label="🔒 $f"
    else
      content=$(cat "$f")
      label="📄 $f"
    fi

    if [ -z "$QUERY" ]; then
      echo ""
      echo "$label"
      echo "$content"
    else
      local matches
      matches=$(echo "$content" | grep -in "$QUERY" 2>/dev/null || true)
      if [ -n "$matches" ]; then
        echo ""
        echo "$label"
        echo "$content" | grep -in --color=never "$QUERY" | while IFS= read -r line; do
          echo "  $line"
        done
      fi
    fi
  done <<< "$files"
}

if [ "$LAYER" = "all" ]; then
  for l in "${VALID_LAYERS[@]}"; do
    search_layer "$l"
  done
else
  search_layer "$LAYER"
fi
