#!/usr/bin/env bash
# speak.sh — Convert text to speech using local Piper TTS
# Usage: speak.sh "text to speak" [output_file.wav] [voice]
# Output: writes WAV to output_file, prints output path to stdout
# Available voices: en_US-amy-medium, en_US-joe-medium, en_US-lessac-medium,
#                   en_US-kusal-medium, en_US-danny-low,
#                   en_GB-alba-medium, en_GB-northern_english_male-medium
#
# Environment variables:
#   PIPER_BIN           — path to piper binary (default: auto-detected via `which`)
#   VOICECLAW_VOICES_DIR — path to folder containing *.onnx voice models
#                          (default: ~/.local/share/piper/voices)

set -euo pipefail

TEXT="${1:-}"
OUTPUT="${2:-/tmp/voiceclaw_tts_$$.wav}"
VOICE="${3:-en_US-lessac-medium}"
VOICES_DIR="${VOICECLAW_VOICES_DIR:-$HOME/.local/share/piper/voices}"
PIPER_BIN="${PIPER_BIN:-$(which piper 2>/dev/null || echo piper)}"

if [[ -z "$TEXT" ]]; then
  echo "Usage: speak.sh \"text\" [output.wav] [voice]" >&2
  echo "  Env: PIPER_BIN, VOICECLAW_VOICES_DIR" >&2
  exit 1
fi

# Sanitize voice name — allow only safe characters to prevent path traversal
VOICE=$(echo "$VOICE" | tr -cd 'a-zA-Z0-9_-')
if [[ -z "$VOICE" ]]; then
  echo "Error: voice name is empty after sanitization" >&2
  exit 1
fi

MODEL="$VOICES_DIR/$VOICE.onnx"
CONFIG="$VOICES_DIR/$VOICE.onnx.json"

if [[ ! -f "$MODEL" ]]; then
  echo "Error: voice model not found: $MODEL" >&2
  echo "Set VOICECLAW_VOICES_DIR=/path/to/voices/ or install piper voices." >&2
  echo "Available voices in $VOICES_DIR:" >&2
  ls "$VOICES_DIR"/*.onnx 2>/dev/null | xargs -n1 basename | sed 's/\.onnx$//' >&2 || echo "  (none found)" >&2
  exit 1
fi

# Generate WAV — local piper binary, no network
CONFIG_ARGS=()
[[ -f "$CONFIG" ]] && CONFIG_ARGS=(-c "$CONFIG")

echo "$TEXT" | "$PIPER_BIN" -m "$MODEL" "${CONFIG_ARGS[@]}" -f "$OUTPUT" 2>/dev/null

echo "$OUTPUT"
