#!/usr/bin/env bash
# transcribe.sh — Download transcript for a single Bilibili video
# Strategy: Try B站 AI subtitles first (instant), fallback to whisper (slow)
# Usage: transcribe.sh <URL> <output_dir> [language] [cookies_arg]
# Output: <output_dir>/.raw/<BV号>_<标题>.txt + <output_dir>/<BV号>_<标题>.meta.json
set -euo pipefail

URL="$1"
OUT_DIR="$2"
LANG="${3:-zh}"
COOKIES="${4:-}"
SEGMENT_DURATION=600  # 10 minutes per chunk (whisper fallback)

WHISPER="${WHISPER_CLI:-whisper-cli}"
MODEL="${WHISPER_MODEL:-$HOME/.whisper-cpp/ggml-small.bin}"

mkdir -p "$OUT_DIR"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Extract video ID
VIDEO_ID=$(echo "$URL" | grep -oE 'BV[a-zA-Z0-9]+' || echo "video_$(date +%s)")

# Helper: sanitize string for use in filenames
sanitize() {
  echo "$1" | sed 's/[\/\\:*?"<>|]/_/g' | sed 's/  */ /g' | head -c 120
}

# Helper: convert SRT to plain text
srt_to_txt() {
  # Strip sequence numbers, timestamps, and blank lines; keep only text
  sed '/^[0-9]*$/d; /^[0-9][0-9]:[0-9][0-9]:/d; /^$/d' "$1"
}

# --- [0] Fetch metadata & determine filename ---
echo "[0] Fetching metadata: $VIDEO_ID"
META_ARGS=(--dump-json --no-download "$URL")
[ -n "$COOKIES" ] && META_ARGS+=($COOKIES)
META_JSON=$(yt-dlp "${META_ARGS[@]}" 2>/dev/null | head -1 || echo "{}")

TITLE=""
FILE_BASE="$VIDEO_ID"

if [ -n "$META_JSON" ] && [ "$META_JSON" != "{}" ]; then
  TITLE=$(echo "$META_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title',''))" 2>/dev/null || echo "")
fi

if [ -n "$TITLE" ]; then
  SAFE_TITLE=$(sanitize "$TITLE")
  FILE_BASE="${VIDEO_ID}_${SAFE_TITLE}"
  echo "  Title: $TITLE"
fi

# Raw transcripts go in .raw/ subdirectory
RAW_DIR="$OUT_DIR/.raw"
mkdir -p "$RAW_DIR"

# Skip if main dir already has the file (fully processed)
# Note: if only .raw/ exists but not main dir, we still process (to copy or clean)
if [ -f "$OUT_DIR/${FILE_BASE}.txt" ]; then
  echo "SKIP (already in main dir): $FILE_BASE"
  exit 0
fi

# Save metadata
if [ -n "$META_JSON" ] && [ "$META_JSON" != "{}" ]; then
  echo "$META_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
out = {
  'bvid': d.get('id',''),
  'title': d.get('title',''),
  'uploader': d.get('uploader',''),
  'uploader_id': d.get('uploader_id',''),
  'description': d.get('description',''),
  'duration': d.get('duration',0),
  'upload_date': d.get('upload_date',''),
  'view_count': d.get('view_count',0),
  'like_count': d.get('like_count',0),
  'tags': d.get('tags',[]),
  'url': d.get('webpage_url',''),
  'filename_base': '$FILE_BASE'
}
json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
" > "$OUT_DIR/${FILE_BASE}.meta.json" 2>/dev/null
fi

OUTFILE="$RAW_DIR/${FILE_BASE}.txt"

# --- [1] Try B站 AI subtitles first (instant) ---
echo "[1] Trying B站 AI subtitles..."
SUB_ARGS=(--write-subs --sub-langs "ai-zh" --skip-download -o "$TMPDIR/sub" "$URL")
[ -n "$COOKIES" ] && SUB_ARGS+=($COOKIES)

if yt-dlp "${SUB_ARGS[@]}" 2>/dev/null && [ -f "$TMPDIR/sub.ai-zh.srt" ]; then
  srt_to_txt "$TMPDIR/sub.ai-zh.srt" > "$OUTFILE"
  # AI subtitles are clean enough - copy directly to main dir (skip cleaning)
  cp "$OUTFILE" "$OUT_DIR/${FILE_BASE}.txt"
  WORDCOUNT=$(wc -c < "$OUTFILE")
  echo "Done (AI subtitles, clean): $OUTFILE ($WORDCOUNT bytes)"
  exit 0
fi

echo "  No AI subtitles available, falling back to whisper..."

# --- [2] Fallback: Download audio ---
echo "[2] Downloading audio: $URL"
YT_ARGS=(-f "bestaudio" --extract-audio --audio-format wav --audio-quality 0 -o "$TMPDIR/audio.%(ext)s")
[ -n "$COOKIES" ] && YT_ARGS+=($COOKIES)
yt-dlp "${YT_ARGS[@]}" "$URL" 2>&1

AUDIO="$TMPDIR/audio.wav"
if [ ! -f "$AUDIO" ]; then
  SRC=$(ls "$TMPDIR"/audio.* 2>/dev/null | head -1)
  [ -z "$SRC" ] && { echo "ERROR: No audio downloaded"; exit 1; }
  ffmpeg -i "$SRC" -ar 16000 -ac 1 "$AUDIO" -y -loglevel error
fi

# Ensure 16kHz mono for whisper.cpp
AUDIO_16K="$TMPDIR/audio_16k.wav"
ffmpeg -i "$AUDIO" -ar 16000 -ac 1 "$AUDIO_16K" -y -loglevel error 2>/dev/null || AUDIO_16K="$AUDIO"

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO_16K" | cut -d. -f1)
NUM_PARTS=$(( (DURATION + SEGMENT_DURATION - 1) / SEGMENT_DURATION ))

# --- [3] Split & Transcribe ---
echo "[3] Splitting into $NUM_PARTS segments, transcribing with whisper..."
for i in $(seq 0 $((NUM_PARTS - 1))); do
  START=$((i * SEGMENT_DURATION))
  ffmpeg -i "$AUDIO_16K" -ss "$START" -t "$SEGMENT_DURATION" \
    -c copy "$TMPDIR/part_${i}.wav" -y -loglevel error
  echo "  Transcribing part $((i+1))/$NUM_PARTS..."
  "$WHISPER" -m "$MODEL" -f "$TMPDIR/part_${i}.wav" -l "$LANG" -otxt -of "$TMPDIR/part_${i}" -np 2>/dev/null
done

# --- [4] Merge ---
echo "[4] Merging transcript"
cat "$TMPDIR"/part_*.txt > "$OUTFILE" 2>/dev/null

WORDCOUNT=$(wc -c < "$OUTFILE")
echo "Done (whisper): $OUTFILE ($WORDCOUNT bytes)"
