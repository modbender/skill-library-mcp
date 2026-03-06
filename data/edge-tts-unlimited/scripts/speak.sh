#!/usr/bin/env bash
# Edge TTS Unlimited — Free neural TTS with no limits
# Usage: speak.sh "text" -o output.mp3
#        speak.sh --file input.txt -v en-US-GuyNeural -r "+5%" -o output.mp3
set -euo pipefail

# Defaults
VOICE="en-US-GuyNeural"
RATE=""
OUTPUT=""
TEXT=""
INPUT_FILE=""
LIST_VOICES=false
LIST_FILTER=""

# Presets
declare -A PRESET_VOICE=(
  [news-us]="en-US-GuyNeural"
  [news-bbc]="en-GB-RyanNeural"
  [calm]="en-US-AndrewNeural"
  [fast]="en-US-ChristopherNeural"
)
declare -A PRESET_RATE=(
  [news-us]="+5%"
  [news-bbc]=""
  [calm]="-10%"
  [fast]="+20%"
)

# Find uv or pip
find_uv() {
  if command -v uv &>/dev/null; then echo "uv"; return; fi
  for p in /data/clawd/.local/bin/uv /home/node/.local/bin/uv ~/.local/bin/uv; do
    [[ -x "$p" ]] && echo "$p" && return
  done
  echo ""
}

UV=$(find_uv)

run_edge_tts() {
  if [[ -n "$UV" ]]; then
    "$UV" run --with edge-tts -- edge-tts "$@"
  elif command -v edge-tts &>/dev/null; then
    edge-tts "$@"
  elif command -v pip3 &>/dev/null; then
    pip3 install -q edge-tts &>/dev/null
    edge-tts "$@"
  else
    echo "Error: Need uv or pip to install edge-tts" >&2
    exit 1
  fi
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --file|-f) INPUT_FILE="$2"; shift 2 ;;
    --voice|-v) VOICE="$2"; shift 2 ;;
    --rate|-r) RATE="$2"; shift 2 ;;
    --output|-o) OUTPUT="$2"; shift 2 ;;
    --preset|-p)
      preset="$2"
      if [[ -n "${PRESET_VOICE[$preset]+x}" ]]; then
        VOICE="${PRESET_VOICE[$preset]}"
        RATE="${PRESET_RATE[$preset]}"
      else
        echo "Unknown preset: $preset (available: ${!PRESET_VOICE[*]})" >&2
        exit 1
      fi
      shift 2 ;;
    --list) LIST_VOICES=true; shift ;;
    --list-filter) LIST_VOICES=true; LIST_FILTER="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: speak.sh [TEXT] [OPTIONS]"
      echo "  TEXT                Text to speak (or use --file)"
      echo "  --file, -f FILE    Read text from file"
      echo "  --voice, -v NAME   Voice (default: en-US-GuyNeural)"
      echo "  --rate, -r RATE    Speed: \"+5%\", \"-10%\", etc."
      echo "  --preset, -p NAME  Preset: news-us, news-bbc, calm, fast"
      echo "  --output, -o FILE  Output path"
      echo "  --list             List voices"
      echo "  --list-filter STR  Filter voices"
      exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) TEXT="$1"; shift ;;
  esac
done

# List voices
if $LIST_VOICES; then
  if [[ -n "$LIST_FILTER" ]]; then
    run_edge_tts --list-voices 2>/dev/null | grep -i "$LIST_FILTER"
  else
    run_edge_tts --list-voices 2>/dev/null
  fi
  exit 0
fi

# Validate input
if [[ -z "$TEXT" && -z "$INPUT_FILE" ]]; then
  echo "Error: Provide text as argument or use --file" >&2
  exit 1
fi

if [[ -n "$INPUT_FILE" && ! -f "$INPUT_FILE" ]]; then
  echo "Error: File not found: $INPUT_FILE" >&2
  exit 1
fi

# Default output
if [[ -z "$OUTPUT" ]]; then
  OUTPUT="/tmp/tts-$(date +%s).mp3"
fi

# Build command
CMD=(--voice "$VOICE" --write-media "$OUTPUT")
[[ -n "$RATE" ]] && CMD+=(--rate "$RATE")

if [[ -n "$INPUT_FILE" ]]; then
  CMD+=(--file "$INPUT_FILE")
else
  CMD+=(--text "$TEXT")
fi

# Generate
run_edge_tts "${CMD[@]}" 2>/dev/null

if [[ -f "$OUTPUT" ]]; then
  SIZE=$(du -h "$OUTPUT" | cut -f1)
  echo "$OUTPUT ($SIZE)"
else
  echo "Error: Failed to generate audio" >&2
  exit 1
fi
