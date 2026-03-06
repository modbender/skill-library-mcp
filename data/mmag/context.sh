#!/usr/bin/env bash
# context.sh – Assemble a merged LLM prompt context from all MMAG memory layers
# Usage: bash context.sh [--max-chars N] [--root <memory-root>]
#
# Priority order (highest to lowest, per MMAG paper):
#   1. Long-Term User Memory  → system-level context
#   2. Episodic Memory        → upcoming events & reminders
#   3. Sensory Memory         → current environmental context
#   4. Conversational Memory  → recent dialogue history
#   5. Working Memory         → current session scratchpad
#
# Encrypted files (.md.enc) are transparently decrypted via decrypt.sh --stdout.
# Set MMAG_KEY or MMAG_KEY_FILE before calling if long-term layer is encrypted.

set -euo pipefail

ROOT="memory"
MAX_CHARS=90000  # approx 90k chars (~22k tokens) default

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-chars)
      MAX_CHARS="$2"
      shift 2
      ;;
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

BUFFER=""
TOTAL=0

append_layer() {
  local layer="$1"
  local heading="$2"
  local dir="$ROOT/$layer"

  if [ ! -d "$dir" ]; then
    return
  fi

  # Collect both plaintext and encrypted files
  local files
  files=$( (find "$dir" -name "*.md" ! -name "README.md" 2>/dev/null; find "$dir" -name "*.md.enc" 2>/dev/null) | sort -r | head -5 || true)

  if [ -z "$files" ]; then
    return
  fi

  local SKILL_DIR
  SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

  local section=""
  section+="\\n### $heading\\n"

  while IFS= read -r f; do
    local content
    if [[ "$f" == *.md.enc ]]; then
      # Decrypt in-memory only — no plaintext written to disk
      content=$(bash "$SKILL_DIR/decrypt.sh" --stdout --file "$f" 2>/dev/null || echo "[encrypted — set MMAG_KEY to decrypt]")
    else
      content=$(cat "$f")
    fi
    section+="\\n$content\\n"
  done <<< "$files"

  local section_len=${#section}
  local remaining=$((MAX_CHARS - TOTAL))

  if [ "$remaining" -le 0 ]; then
    echo "⚠️  Max context size reached ($MAX_CHARS chars). Some layers omitted." >&2
    return
  fi

  if [ "$section_len" -gt "$remaining" ]; then
    # Truncate to remaining budget
    section="${section:0:$remaining}"
    section+="\\n... [TRUNCATED]"
    echo "⚠️  Layer '$layer' truncated to fit context budget." >&2
  fi

  BUFFER+="$section"
  TOTAL=$((TOTAL + ${#section}))
}

# Assemble in priority order
echo "<!-- MMAG Context Block | Generated: $(date '+%Y-%m-%dT%H:%M:%S') -->"
echo ""
echo "=== MMAG MEMORY CONTEXT ==="
echo ""

append_layer "long-term"      "LONG-TERM USER PROFILE [system]"
append_layer "episodic"       "EPISODIC MEMORY — Events & Reminders"
append_layer "sensory"        "SENSORY CONTEXT — Environment"
append_layer "conversational" "CONVERSATIONAL HISTORY"
append_layer "working"        "WORKING MEMORY — Current Session"

echo -e "$BUFFER"
echo ""
echo "=== END MMAG CONTEXT | chars: $TOTAL / $MAX_CHARS ==="
