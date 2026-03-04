#!/usr/bin/env bash
# collect-photos.sh — Batch-download photos from a WhatsApp group via wacli.
#
# Usage: collect-photos.sh <group-jid> <after-date> <output-dir>
#
# Arguments:
#   group-jid   — WhatsApp group JID (e.g. 120363012345@g.us)
#   after-date  — Only photos after this date (YYYY-MM-DD)
#   output-dir  — Directory to save downloaded photos
#
# Output: JSON manifest on stdout — array of {id, sender, timestamp, filepath}
#
# Requires: wacli, jq

set -euo pipefail

GROUP_JID="${1:?Usage: collect-photos.sh <group-jid> <after-date> <output-dir>}"
AFTER_DATE="${2:?Usage: collect-photos.sh <group-jid> <after-date> <output-dir>}"
OUTPUT_DIR="${3:?Usage: collect-photos.sh <group-jid> <after-date> <output-dir>}"

# Ensure output dir exists
mkdir -p "$OUTPUT_DIR"

# 1. Search for image messages in the group after the given date
echo "[collect] Searching for images in $GROUP_JID after $AFTER_DATE..." >&2
MESSAGES_JSON=$(wacli messages search "*" \
  --chat "$GROUP_JID" \
  --type image \
  --after "$AFTER_DATE" \
  --limit 100 \
  --json 2>/dev/null)

# Parse message count
MSG_COUNT=$(echo "$MESSAGES_JSON" | jq 'length')
echo "[collect] Found $MSG_COUNT image messages" >&2

if [ "$MSG_COUNT" -eq 0 ]; then
  echo "[]"
  exit 0
fi

# 2. Download each photo and build manifest
MANIFEST="[]"
DOWNLOADED=0
FAILED=0

echo "$MESSAGES_JSON" | jq -c '.[]' | while IFS= read -r msg; do
  MSG_ID=$(echo "$msg" | jq -r '.id // .messageId // .ID')
  SENDER=$(echo "$msg" | jq -r '.sender // .from // .Sender // ""')
  TIMESTAMP=$(echo "$msg" | jq -r '.timestamp // .Timestamp // ""')

  if [ -z "$MSG_ID" ] || [ "$MSG_ID" = "null" ]; then
    echo "[collect] Skipping message with no ID" >&2
    continue
  fi

  echo "[collect] Downloading media for message $MSG_ID..." >&2
  DL_RESULT=$(wacli media download \
    --chat "$GROUP_JID" \
    --id "$MSG_ID" \
    --output "$OUTPUT_DIR" \
    --json 2>/dev/null) || {
    echo "[collect] Failed to download $MSG_ID, skipping" >&2
    FAILED=$((FAILED + 1))
    continue
  }

  # Try to extract the file path from download result
  FILEPATH=$(echo "$DL_RESULT" | jq -r '.path // .filePath // .file // ""' 2>/dev/null)

  # If JSON parsing fails, check if the output dir has a new file
  if [ -z "$FILEPATH" ] || [ "$FILEPATH" = "null" ]; then
    # Fallback: find most recently modified file in output dir
    FILEPATH=$(ls -t "$OUTPUT_DIR"/* 2>/dev/null | head -1)
  fi

  if [ -n "$FILEPATH" ] && [ -f "$FILEPATH" ]; then
    DOWNLOADED=$((DOWNLOADED + 1))
    echo "[collect] Downloaded: $FILEPATH" >&2
    # Append to manifest (output to stdout at the end)
    echo "{\"id\":\"$MSG_ID\",\"sender\":\"$SENDER\",\"timestamp\":\"$TIMESTAMP\",\"filepath\":\"$FILEPATH\"}"
  else
    echo "[collect] No file found for $MSG_ID" >&2
    FAILED=$((FAILED + 1))
  fi
done | jq -s '.'

echo "[collect] Done: downloaded files from $GROUP_JID" >&2
