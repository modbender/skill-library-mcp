#!/usr/bin/env bash
# YouTube Transcript Generator
# Downloads and cleans subtitles from any YouTube video
# Usage: bash get_transcript.sh "URL" [output_file] [language]
# By OpenClaw Lab — https://openclawlab.xyz

set -euo pipefail

URL="${1:?Usage: bash get_transcript.sh \"YOUTUBE_URL\" [output_file] [language] [timestamps]}"
LANG="${3:-en}"
TIMESTAMPS="${4:-}"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Extract video ID (works on macOS and Linux)
VIDEO_ID=$(python3 -c "
import re, sys
url = sys.argv[1]
m = re.search(r'(?:v=|youtu\.be/|/shorts/)([A-Za-z0-9_-]{11})', url)
print(m.group(1) if m else re.search(r'([A-Za-z0-9_-]{11})', url).group(1))
" "$URL" 2>/dev/null || echo "unknown")

OUTPUT="${2:-transcript_${VIDEO_ID}.txt}"

echo "Downloading subtitles for: $URL" >&2
echo "Video ID: $VIDEO_ID" >&2

# Try manual subs first, then auto-generated
SUBTITLE_FILE=""
for ATTEMPT in "write-sub" "write-auto-sub"; do
  yt-dlp \
    --skip-download \
    --"$ATTEMPT" \
    --sub-lang "$LANG" \
    --sub-format vtt \
    --convert-subs vtt \
    -o "$TMPDIR/subs" \
    "$URL" 2>/dev/null || true

  # Find the downloaded subtitle file
  FOUND=$(find "$TMPDIR" -name "*.vtt" -o -name "*.srt" | head -1)
  if [ -n "$FOUND" ]; then
    SUBTITLE_FILE="$FOUND"
    echo "Found subtitles ($ATTEMPT, $LANG)" >&2
    break
  fi
done

# If no English subs, try any language
if [ -z "$SUBTITLE_FILE" ]; then
  echo "No $LANG subtitles. Trying all languages..." >&2
  yt-dlp \
    --skip-download \
    --write-auto-sub \
    --sub-lang "en.*,fr,es,de,pt,ja,ko,zh" \
    --sub-format vtt \
    --convert-subs vtt \
    -o "$TMPDIR/subs" \
    "$URL" 2>/dev/null || true

  SUBTITLE_FILE=$(find "$TMPDIR" -name "*.vtt" -o -name "*.srt" | head -1)
fi

if [ -z "$SUBTITLE_FILE" ]; then
  echo "ERROR: No subtitles found for this video." >&2
  echo "Available subtitles:" >&2
  yt-dlp --list-subs "$URL" 2>/dev/null | tail -20 >&2
  exit 1
fi

# Clean VTT/SRT to plain text
python3 -c "
import re, sys

timestamps_mode = '$TIMESTAMPS' == 'timestamps'

with open('$SUBTITLE_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove WEBVTT header and metadata
content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
# Remove lines starting with NOTE or STYLE
content = re.sub(r'^(NOTE|STYLE).*?(\n\n|\Z)', '', content, flags=re.DOTALL | re.MULTILINE)

if timestamps_mode:
    # TIMESTAMPED MODE: preserve start times
    blocks = re.split(r'\n\n+', content.strip())
    seen = set()
    output_lines = []
    for block in blocks:
        lines = block.strip().split('\n')
        ts_match = re.search(r'(\d{2}:\d{2}:\d{2})[\.,]\d{3}\s*-->', block)
        text_lines = []
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+$', line): continue
            if re.match(r'\d{2}:\d{2}:\d{2}', line): continue
            if not line: continue
            line = re.sub(r'<[^>]+>', '', line)
            line = re.sub(r'\{[^}]+\}', '', line)
            line = re.sub(r'align:start position:\d+%', '', line)
            line = line.strip()
            if line:
                text_lines.append(line)
        text = ' '.join(text_lines)
        if not text: continue
        if ts_match:
            output_lines.append((ts_match.group(1), text))
        else:
            output_lines.append(('', text))

    # Merge overlapping auto-sub segments
    merged = []
    full_text = ''
    for ts, text in output_lines:
        # Find how much of this text is new (not in accumulated text)
        words = text.split()
        new_start = 0
        for i in range(len(words), 0, -1):
            chunk = ' '.join(words[:i])
            if chunk in full_text:
                new_start = i
                break
        new_words = ' '.join(words[new_start:])
        if new_words:
            full_text += ' ' + new_words
            if not merged or len(full_text.split()) % 25 < len(new_words.split()):
                merged.append(f'[{ts}] ' + new_words.strip() if ts else new_words.strip())
            else:
                merged[-1] += ' ' + new_words.strip()

    print('\n'.join(merged))
else:
    # CLEAN MODE: no timestamps, readable paragraphs
    content = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->.*\n', '', content)
    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\{[^}]+\}', '', content)
    content = re.sub(r'align:start position:\d+%', '', content)

    lines = [line.strip() for line in content.split('\n') if line.strip()]
    deduped = []
    prev = ''
    for line in lines:
        if line != prev:
            deduped.append(line)
            prev = line

    text = ' '.join(deduped)
    text = re.sub(r'\s+', ' ', text).strip()

    sentences = re.split(r'(?<=[.!?])\s+', text)
    paragraphs = []
    current = []
    for s in sentences:
        current.append(s)
        if len(current) >= 4:
            paragraphs.append(' '.join(current))
            current = []
    if current:
        paragraphs.append(' '.join(current))
    print('\n\n'.join(paragraphs))
" > "$OUTPUT"

LINES=$(wc -l < "$OUTPUT" | tr -d ' ')
WORDS=$(wc -w < "$OUTPUT" | tr -d ' ')
echo "" >&2
echo "Transcript saved to: $OUTPUT ($WORDS words, $LINES lines)" >&2

cat "$OUTPUT"
