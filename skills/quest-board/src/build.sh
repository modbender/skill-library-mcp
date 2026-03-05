#!/usr/bin/env bash
set -euo pipefail

# Quest Board — Build Script
# Reads quest-board-registry.json and generates quest-board.html

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$SCRIPT_DIR/template.html"

# Find workspace root
WS="${QUEST_BOARD_WORKSPACE:-$(cd "$SKILL_DIR/../.." && pwd)}"
REG="$WS/quest-board-registry.json"
OUT="$WS/quest-board.html"
TITLE="${QUEST_BOARD_TITLE:-Quest Board}"

if [[ ! -f "$REG" ]]; then
  echo "❌ Registry not found: $REG"
  echo "   Run 'bash $SKILL_DIR/src/init.sh' first."
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "❌ Template not found: $TEMPLATE"
  exit 1
fi

# Read registry data
DATA=$(cat "$REG")

# Read template and perform substitutions
# 1. Replace __TITLE__ with the configured title
# 2. Replace __REGISTRY_DATA__ with the JSON data
# 3. Replace __WORKSPACE__ with the workspace path

CONTENT=$(cat "$TEMPLATE")

# Use awk for safe multi-line substitution
CONTENT=$(echo "$CONTENT" | sed "s|__TITLE__|$TITLE|g")
CONTENT=$(echo "$CONTENT" | sed "s|__WORKSPACE__|$WS/|g")

# For __REGISTRY_DATA__, we need to handle multi-line JSON
# Write a temp file approach for safety
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

# Use awk to replace the placeholder with actual JSON data
awk -v data="$DATA" '{
  if (index($0, "__REGISTRY_DATA__") > 0) {
    sub(/__REGISTRY_DATA__/, "")
    print data
  } else {
    print
  }
}' <<< "$CONTENT" > "$TMPFILE"

cp "$TMPFILE" "$OUT"

echo "✅ Built: $OUT"
echo "   Title: $TITLE"
echo "   Registry: $REG"
