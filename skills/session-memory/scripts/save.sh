#!/bin/bash
# Save a memory entry
# Usage: ./save.sh "topic" "content" [tags...]

set -e

TOPIC="${1:?Usage: $0 \"topic\" \"content\" [tags...]}"
CONTENT="${2:?Usage: $0 \"topic\" \"content\" [tags...]}"
shift 2
TAGS="$*"

MEMORY_DIR="${AGENT_MEMORY_DIR:-$HOME/.agent-memory}"
YEAR=$(date -u +%Y)
MONTH=$(date -u +%m)
DAY=$(date -u +%d)

# Ensure directory exists
mkdir -p "$MEMORY_DIR/$YEAR/$MONTH"

# Build JSON safely with node (no manual escaping)
node -e "
const entry = {
  ts: Date.now(),
  topic: process.argv[1],
  content: process.argv[2],
  tags: process.argv[3] ? process.argv[3].split(' ').filter(Boolean) : []
};
process.stdout.write(JSON.stringify(entry) + '\n');
" "$TOPIC" "$CONTENT" "$TAGS" >> "$MEMORY_DIR/$YEAR/$MONTH/$DAY.jsonl"

echo "✓ Memory saved: [$TOPIC] $(echo "$CONTENT" | head -c 80)"
