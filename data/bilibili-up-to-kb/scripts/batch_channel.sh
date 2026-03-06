#!/usr/bin/env bash
# batch_channel.sh — Download ALL videos from a Bilibili UP主 and transcribe them IN PARALLEL
# Usage: batch_channel.sh <channel_url_or_uid> <output_dir> [language] [max_videos] [concurrency] [chunk_size]
#   chunk_size: Videos per fetch chunk (default 500) — increase if B站 still times out
set -euo pipefail

CHANNEL="$1"
OUT_DIR="$2"
LANG="${3:-zh}"
MAX="${4:-0}"        # 0 = all
CONCURRENCY="${5:-6}" # parallel download+transcribe jobs
CHUNK_SIZE="${6:-500}" # Fetch videos in chunks to avoid timeout

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Fetching video list from: $CHANNEL ==="

# Try without cookies first, fall back to cookies-from-browser
COOKIES_ARG=""
if ! yt-dlp --flat-playlist --print url "$CHANNEL" >/dev/null 2>&1; then
  echo "Direct access failed, trying with browser cookies..."
  COOKIES_ARG="--cookies-from-browser chrome"
fi

# Function to fetch video URLs in chunks (handles 1000+ video channels)
fetch_urls_chunked() {
  local chunk_start=1
  local chunk_end=$CHUNK_SIZE
  local all_urls=$(mktemp)
  
  while true; do
    echo "  Fetching videos $chunk_start-$chunk_end..."
    local chunk_urls=$(mktemp)
    
    # Try to fetch this chunk
    if yt-dlp $COOKIES_ARG --flat-playlist \
      --playlist-start $chunk_start \
      --playlist-end $chunk_end \
      --print url "$CHANNEL" > "$chunk_urls" 2>/dev/null; then
      
      local count=$(wc -l < "$chunk_urls" | tr -d ' ')
      if [ "$count" -eq 0 ]; then
        # No more videos
        break
      fi
      
      cat "$chunk_urls" >> "$all_urls"
      rm "$chunk_urls"
      
      # Respect MAX if set
      if [ "$MAX" -gt 0 ] && [ "$chunk_start" -ge "$MAX" ]; then
        break
      fi
      
      # Check if we got fewer than chunk size (last chunk)
      if [ "$count" -lt $CHUNK_SIZE ]; then
        break
      fi
      
      chunk_start=$((chunk_end + 1))
      chunk_end=$((chunk_start + CHUNK_SIZE - 1))
      
      # Cap at MAX if set
      if [ "$MAX" -gt 0 ] && [ "$chunk_end" -gt "$MAX" ]; then
        chunk_end=$MAX
      fi
    else
      echo "  Warning: Failed to fetch chunk $chunk_start-$chunk_end, retrying..."
      sleep 2
    fi
  done
  
  cat "$all_urls"
  rm -f "$all_urls"
}

# For small channels, use simple fetch; for large channels, use chunked
TOTAL_ESTIMATE=$(yt-dlp $COOKIES_ARG --flat-playlist --print id "$CHANNEL" 2>/dev/null | wc -l || echo "0")
URLS_FILE=$(mktemp)
FILTERED=$(mktemp)
trap 'rm -f "$URLS_FILE" "$FILTERED"' EXIT

if [ "$TOTAL_ESTIMATE" -gt 800 ]; then
  echo "Large channel detected (~$TOTAL_ESTIMATE videos), using chunked fetch..."
  fetch_urls_chunked > "$URLS_FILE"
else
  YT_DLP_ARGS=(--flat-playlist --print url "$CHANNEL")
  [ "$MAX" -gt 0 ] && YT_DLP_ARGS=(--flat-playlist --playlist-end "$MAX" --print url "$CHANNEL")
  yt-dlp $COOKIES_ARG "${YT_DLP_ARGS[@]}" > "$URLS_FILE" 2>/dev/null
fi

TOTAL=$(wc -l < "$URLS_FILE" | tr -d ' ')
echo "Found $TOTAL videos."

# Fetch UP主 name from first video to name the output directory
FIRST_URL=$(head -1 "$URLS_FILE")
if [ -n "$FIRST_URL" ]; then
  UPLOADER=$(yt-dlp --dump-json --no-download $COOKIES_ARG "$FIRST_URL" 2>/dev/null | head -1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('uploader',''))" 2>/dev/null || echo "")
  if [ -n "$UPLOADER" ]; then
    # Extract channel ID from URL
    CHAN_ID=$(echo "$CHANNEL" | grep -oE '[0-9]+' | tail -1)
    SAFE_UPLOADER=$(echo "$UPLOADER" | sed 's/[\/\\:*?"<>|]/_/g')
    NEW_DIR="$(dirname "$OUT_DIR")/${SAFE_UPLOADER}_${CHAN_ID}"
    if [ "$OUT_DIR" != "$NEW_DIR" ] && [ ! -d "$NEW_DIR" ]; then
      if [ -d "$OUT_DIR" ]; then
        mv "$OUT_DIR" "$NEW_DIR"
      fi
      OUT_DIR="$NEW_DIR"
    elif [ -d "$NEW_DIR" ]; then
      OUT_DIR="$NEW_DIR"
    fi
    echo "UP主: $UPLOADER → $OUT_DIR"
  fi
fi
mkdir -p "$OUT_DIR"

echo "Running $CONCURRENCY parallel transcriptions."

# Skip already-transcribed videos (check both BV号.txt and BV号_*.txt patterns)
while IFS= read -r url; do
  VIDEO_ID=$(echo "$url" | grep -oE 'BV[a-zA-Z0-9]+' || echo "")
  if [ -n "$VIDEO_ID" ]; then
    # Check if any file starting with this BV号 exists (main dir or .raw/)
    if ls "$OUT_DIR"/${VIDEO_ID}*.txt >/dev/null 2>&1 || ls "$OUT_DIR"/.raw/${VIDEO_ID}*.txt >/dev/null 2>&1; then
      echo "  SKIP (already exists): $VIDEO_ID"
      continue
    fi
  fi
  echo "$url" >> "$FILTERED"
done < "$URLS_FILE"

TODO=$(wc -l < "$FILTERED" | tr -d ' ')
echo "Skipped $((TOTAL - TODO)) already transcribed. Transcribing $TODO new videos."

# Parallel execution via xargs, passing cookies arg through
export COOKIES_ARG
cat "$FILTERED" | xargs -P "$CONCURRENCY" -I {} "$SCRIPT_DIR/transcribe.sh" "{}" "$OUT_DIR" "$LANG" "$COOKIES_ARG"

echo ""
echo "=== Batch complete: $TOTAL videos processed ==="
echo "Output directory: $OUT_DIR"

# Generate index.md from metadata
echo "=== Generating index.md ==="
"$SCRIPT_DIR/generate_index.sh" "$OUT_DIR"
