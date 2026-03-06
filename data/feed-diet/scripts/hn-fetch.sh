#!/usr/bin/env bash
# hn-fetch.sh — Fetch stories from a Hacker News user account
# Outputs JSON lines: {"id":..., "title":..., "url":..., "score":..., "time":..., "type":"story"}
#
# Usage: ./hn-fetch.sh USERNAME [MAX_ITEMS] [SINCE_EPOCH]

set -euo pipefail
source "$(dirname "$0")/common.sh"

HN_API="https://hacker-news.firebaseio.com/v0"
USERNAME="${1:?Usage: hn-fetch.sh USERNAME [MAX_ITEMS] [SINCE_EPOCH]}"
MAX_ITEMS="${2:-200}"
SINCE_EPOCH="${3:-0}"

CACHE_FILE="${CACHE_DIR}/hn_${USERNAME}_items.jsonl"

# ─── Fetch user profile ──────────────────────────────────────────────
info "Fetching HN profile for '$USERNAME'..."
USER_JSON=$(safe_fetch "${HN_API}/user/${USERNAME}.json" 3 15) || {
  err "Could not fetch HN user '$USERNAME'. Check the username and try again."
  exit 1
}

# Validate user exists
USER_ID=$(json_get "$USER_JSON" "id")
if [ -z "$USER_ID" ] || [ "$USER_ID" = "None" ]; then
  err "HN user '$USERNAME' not found."
  exit 1
fi

KARMA=$(json_get "$USER_JSON" "karma")
info "Found user '$USER_ID' (karma: ${KARMA})"

# ─── Extract submitted item IDs ──────────────────────────────────────
SUBMITTED=$(json_get "$USER_JSON" "submitted")
if [ -z "$SUBMITTED" ] || [ "$SUBMITTED" = "[]" ] || [ "$SUBMITTED" = "" ]; then
  err "User '$USERNAME' has no submitted items."
  exit 1
fi

# Parse IDs into an array (take up to MAX_ITEMS * 3 to account for comments)
FETCH_LIMIT=$((MAX_ITEMS * 4))
IDS=($(echo "$SUBMITTED" | python3 -c "
import json, sys
ids = json.load(sys.stdin)
for i in ids[:${FETCH_LIMIT}]:
    print(i)
" 2>/dev/null))

TOTAL_IDS=${#IDS[@]}
info "Scanning up to ${TOTAL_IDS} items (looking for ${MAX_ITEMS} stories)..."

# ─── Fetch items, filtering for stories ──────────────────────────────
STORY_COUNT=0
FETCHED=0

# Clear cache file
> "$CACHE_FILE"

# Fetch in parallel batches of 10
BATCH_SIZE=10
for ((i = 0; i < TOTAL_IDS; i += BATCH_SIZE)); do
  [ "$STORY_COUNT" -ge "$MAX_ITEMS" ] && break

  # Launch batch
  BATCH_END=$((i + BATCH_SIZE))
  [ "$BATCH_END" -gt "$TOTAL_IDS" ] && BATCH_END=$TOTAL_IDS

  PIDS=()
  TMPFILES=()
  for ((j = i; j < BATCH_END; j++)); do
    ITEM_ID="${IDS[$j]}"
    TMPFILE=$(mktemp)
    TMPFILES+=("$TMPFILE")
    curl -sf --max-time 8 "${HN_API}/item/${ITEM_ID}.json" > "$TMPFILE" 2>/dev/null &
    PIDS+=($!)
  done

  # Wait for batch
  for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
  done

  # Process results
  for TMPFILE in "${TMPFILES[@]}"; do
    [ "$STORY_COUNT" -ge "$MAX_ITEMS" ] && rm -f "$TMPFILE" && continue
    
    if [ -s "$TMPFILE" ]; then
      ITEM_JSON=$(cat "$TMPFILE")
      
      # Extract fields using python3 for reliability
      RECORD=$(echo "$ITEM_JSON" | python3 -c "
import json, sys
try:
    item = json.load(sys.stdin)
    if item and item.get('type') == 'story' and item.get('title') and not item.get('deleted') and not item.get('dead'):
        ts = item.get('time', 0)
        if ts >= ${SINCE_EPOCH}:
            out = {
                'id': item['id'],
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'score': item.get('score', 0),
                'time': ts,
                'descendants': item.get('descendants', 0),
                'by': item.get('by', '')
            }
            print(json.dumps(out))
except:
    pass
" 2>/dev/null)

      if [ -n "$RECORD" ]; then
        echo "$RECORD" >> "$CACHE_FILE"
        STORY_COUNT=$((STORY_COUNT + 1))
      fi
    fi

    rm -f "$TMPFILE"
    FETCHED=$((FETCHED + 1))
    progress "$FETCHED" "$TOTAL_IDS" "HN items"
  done
done

progress_done

if [ "$STORY_COUNT" -eq 0 ]; then
  err "No stories found for user '$USERNAME'. They may only have comments."
  exit 1
fi

info "Found ${STORY_COUNT} stories for '$USERNAME'"

# Output the cached results
cat "$CACHE_FILE"
