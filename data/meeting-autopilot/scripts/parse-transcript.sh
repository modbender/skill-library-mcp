#!/usr/bin/env bash
# parse-transcript.sh — Parse VTT/SRT/TXT into normalized JSONL
# Usage: bash parse-transcript.sh <file_or_dash> [format]
# Output: JSONL to stdout, one object per segment
#   {"index":1,"timestamp":"00:01:23","speaker":"Alice","text":"We need to..."}
#
# If format is not provided, auto-detects from content.
# Accepts "-" or omit the file arg to read from stdin.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_jq

INPUT="${1:--}"
FORMAT="${2:-auto}"

# Read the full content
CONTENT="$(read_input "$INPUT")"
validate_transcript "$CONTENT"

# Auto-detect format if needed
if [ "$FORMAT" = "auto" ]; then
  FORMAT="$(detect_format "$CONTENT")"
fi

log_info "Detected format: $FORMAT"

# ── VTT Parser ────────────────────────────────────────────
parse_vtt() {
  local content="$1"
  # Use Python for robust VTT parsing, passing content via stdin
  printf '%s' "$content" | python3 -c '
import sys
import json
import re

content = sys.stdin.read()
lines = content.split("\n")

segments = []
index = 0
i = 0

# Skip WEBVTT header
while i < len(lines) and not re.match(r"\d{2}:\d{2}", lines[i]):
    i += 1

while i < len(lines):
    line = lines[i].strip()

    # Look for timestamp lines: 00:00:00.000 --> 00:00:05.000
    ts_match = re.match(r"(\d{2}:\d{2}:\d{2})[.\d]*\s*-->", line)
    if ts_match:
        timestamp = ts_match.group(1)
        i += 1
        text_lines = []
        while i < len(lines) and lines[i].strip():
            text_lines.append(lines[i].strip())
            i += 1

        full_text = " ".join(text_lines)

        # Extract speaker if present: "Speaker Name: text"
        speaker = ""
        speaker_match = re.match(r"^<?([^>:]{1,50})>?:\s*(.*)", full_text)
        if speaker_match:
            speaker = speaker_match.group(1).strip().strip("<>")
            full_text = speaker_match.group(2).strip()

        if full_text:
            index += 1
            segments.append({
                "index": index,
                "timestamp": timestamp,
                "speaker": speaker,
                "text": full_text
            })
    i += 1

for seg in segments:
    print(json.dumps(seg, ensure_ascii=False))
'
}

# ── SRT Parser ────────────────────────────────────────────
parse_srt() {
  local content="$1"
  printf '%s' "$content" | python3 -c '
import sys
import json
import re

content = sys.stdin.read()
# Split on double newlines (SRT blocks)
blocks = re.split(r"\n\s*\n", content.strip())

index = 0
for block in blocks:
    lines = block.strip().split("\n")
    if len(lines) < 3:
        continue

    # Line 1: sequence number
    # Line 2: timestamps
    ts_match = re.match(r"(\d{2}:\d{2}:\d{2})", lines[1])
    if not ts_match:
        continue

    timestamp = ts_match.group(1)
    text_lines = lines[2:]
    full_text = " ".join(l.strip() for l in text_lines if l.strip())

    # Strip HTML tags from SRT
    full_text = re.sub(r"<[^>]+>", "", full_text)

    # Try to extract speaker
    speaker = ""
    speaker_match = re.match(r"^<?([^>:]{1,50})>?:\s*(.*)", full_text)
    if speaker_match:
        speaker = speaker_match.group(1).strip().strip("<>")
        full_text = speaker_match.group(2).strip()

    if full_text:
        index += 1
        seg = {
            "index": index,
            "timestamp": timestamp,
            "speaker": speaker,
            "text": full_text
        }
        print(json.dumps(seg, ensure_ascii=False))
'
}

# ── Plain Text Parser ─────────────────────────────────────
parse_txt() {
  local content="$1"
  printf '%s' "$content" | python3 -c '
import sys
import json
import re

content = sys.stdin.read()
lines = content.strip().split("\n")

index = 0
for line in lines:
    line = line.strip()
    if not line:
        continue

    # Try patterns:
    # "Speaker Name: text"
    # "[00:01:23] Speaker Name: text"
    # "Speaker Name (00:01:23): text"

    timestamp = ""
    speaker = ""
    text = line

    # Pattern: [timestamp] Speaker: text
    m = re.match(r"\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*([^:]{1,50}):\s*(.*)", line)
    if m:
        timestamp = m.group(1)
        speaker = m.group(2).strip()
        text = m.group(3).strip()
    else:
        # Pattern: Speaker: text (no timestamp)
        m = re.match(r"^([A-Z][a-zA-Z\s.]{0,40}):\s+(.*)", line)
        if m:
            speaker = m.group(1).strip()
            text = m.group(2).strip()

    if text:
        index += 1
        seg = {
            "index": index,
            "timestamp": timestamp,
            "speaker": speaker,
            "text": text
        }
        print(json.dumps(seg, ensure_ascii=False))
'
}

# ── Dispatch ──────────────────────────────────────────────
case "$FORMAT" in
  vtt)
    parse_vtt "$CONTENT"
    ;;
  srt)
    parse_srt "$CONTENT"
    ;;
  txt|text|plain)
    parse_txt "$CONTENT"
    ;;
  *)
    die "Unknown format: $FORMAT" "Supported: vtt, srt, txt (or auto)"
    ;;
esac

log_ok "Parsed transcript ($FORMAT format)" >&2
