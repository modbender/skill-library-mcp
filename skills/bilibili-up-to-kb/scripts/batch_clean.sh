#!/usr/bin/env bash
# batch_clean.sh — Clean ALL raw transcripts and output to main directory
# Usage: batch_clean.sh <kb_dir> [concurrency] [chunk_lines]
# Reads from: <kb_dir>/.raw/*.txt
# Writes to:  <kb_dir>/*.txt (clean, no suffix)
set -euo pipefail

DIR="$1"
CONCURRENCY="${2:-0}"  # 0 = all files in parallel
CHUNK_LINES="${3:-80}"

RAW_DIR="$DIR/.raw"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$RAW_DIR" ]; then
  echo "No .raw/ directory found in $DIR"
  exit 1
fi

# Build list of files to clean
TODO_FILE=$(mktemp)
trap 'rm -f "$TODO_FILE"' EXIT

for f in "$RAW_DIR"/*.txt; do
  [ -f "$f" ] || continue
  BASENAME=$(basename "$f")
  CLEAN="$DIR/$BASENAME"
  if [ -f "$CLEAN" ]; then
    echo "SKIP (already cleaned): $BASENAME"
  else
    echo "$f" >> "$TODO_FILE"
  fi
done

TOTAL=$(wc -l < "$TODO_FILE" | tr -d ' ')
echo "Cleaning $TOTAL transcripts with $CONCURRENCY parallel workers..."

if [ "$TOTAL" -eq 0 ]; then
  echo "Nothing to clean."
  exit 0
fi

export SCRIPT_DIR CHUNK_LINES DIR
clean_one() {
  INPUT="$1"
  BASENAME=$(basename "$INPUT")
  OUTPUT="$DIR/$BASENAME"
  echo "  Cleaning: $BASENAME"
  "$SCRIPT_DIR/clean_transcript.sh" "$INPUT" "$OUTPUT" "$CHUNK_LINES"
}
export -f clean_one

if [ "$CONCURRENCY" -eq 0 ]; then
  CONCURRENCY=$(wc -l < "$TODO_FILE" | tr -d ' ')
fi

cat "$TODO_FILE" | xargs -P "$CONCURRENCY" -I {} bash -c 'clean_one "$@"' _ {}

echo ""
echo "=== Batch clean complete: $TOTAL files ==="
