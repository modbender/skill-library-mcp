#!/usr/bin/env bash
# transcribe.sh — Convert audio to text using local Whisper (whisper.cpp)
# Usage: transcribe.sh <audio_file> [model_path]
# Output: prints transcript to stdout
# Supports: ogg, mp3, m4a, wav, flac (auto-converts to wav via ffmpeg)
#
# Environment variables:
#   WHISPER_BIN   — path to whisper binary (default: auto-detected via `which`)
#   WHISPER_MODEL — path to ggml model file (default: ~/.cache/whisper/ggml-base.en.bin)

set -euo pipefail

AUDIO_FILE="${1:-}"
MODEL="${2:-${WHISPER_MODEL:-$HOME/.cache/whisper/ggml-base.en.bin}}"
WHISPER_BIN="${WHISPER_BIN:-$(which whisper 2>/dev/null || echo whisper)}"
TMP_WAV="/tmp/voiceclaw_stt_$$.wav"

if [[ -z "$AUDIO_FILE" ]]; then
  echo "Usage: transcribe.sh <audio_file> [model_path]" >&2
  echo "  Env: WHISPER_BIN, WHISPER_MODEL" >&2
  exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "Error: file not found: $AUDIO_FILE" >&2
  exit 1
fi

if [[ ! -f "$MODEL" ]]; then
  echo "Error: Whisper model not found: $MODEL" >&2
  echo "Set WHISPER_MODEL=/path/to/ggml-base.en.bin to point to your model." >&2
  echo "See README.md for one-time model download instructions." >&2
  exit 1
fi

cleanup() { rm -f "$TMP_WAV"; }
trap cleanup EXIT

# Convert to 16kHz mono WAV (Whisper requirement) — local ffmpeg, no network
ffmpeg -i "$AUDIO_FILE" -ar 16000 -ac 1 "$TMP_WAV" -y -loglevel error

# Transcribe — local whisper binary, no network
"$WHISPER_BIN" -m "$MODEL" "$TMP_WAV" 2>/dev/null \
  | grep -E '^\[' \
  | sed 's/\[[0-9:. ->]*\]  *//' \
  | tr '\n' ' ' \
  | sed 's/^[[:space:]]*//' \
  | sed 's/[[:space:]]*$//'

echo  # final newline
