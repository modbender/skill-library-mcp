#!/usr/bin/env bash
# Transcribe speech in a video or audio file to text using local Whisper (no API key).
#
# Extracts audio from the video, runs whisper, outputs plain text transcript and
# SRT subtitle file. Both are written to the same directory as the input file.
#
# Usage: transcribe.sh <input> [language] [model]
#
# Args:
#   input:    Path to video or audio file (mp4, mov, mp3, m4a, wav, ...)
#   language: (optional) ISO-639-1 language code, e.g. "en", "zh", "ja"
#             Default: auto-detect
#   model:    (optional) Whisper model size: tiny|base|small|medium|large
#             Default: small (good balance of speed and accuracy)
#
# Output files (same directory as input):
#   <name>.txt  — plain text transcript
#   <name>.srt  — SRT subtitle file with timestamps
#
# Stdout: path to the .txt transcript file
#
# Requirements: whisper CLI  →  pip install openai-whisper
#               ffmpeg       →  brew install ffmpeg
#
# Exit codes: 0=success, 1=bad args/missing deps, 2=transcription error

set -euo pipefail

# ---------------------------------------------------------------------------
# Validate dependencies
# ---------------------------------------------------------------------------
MISSING=()
command -v ffmpeg &>/dev/null || MISSING+=("ffmpeg (brew install ffmpeg)")
command -v whisper &>/dev/null || MISSING+=("whisper (pip install openai-whisper)")

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "Error: Missing required tools:" >&2
  for m in "${MISSING[@]}"; do echo "  - $m" >&2; done
  exit 1
fi

# ---------------------------------------------------------------------------
# Validate arguments
# ---------------------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  echo "Usage: transcribe.sh <input> [language] [model]" >&2
  echo "  Examples:" >&2
  echo "    transcribe.sh video.mp4                  # auto-detect language" >&2
  echo "    transcribe.sh video.mp4 en               # force English" >&2
  echo "    transcribe.sh video.mp4 zh medium        # Chinese, medium model" >&2
  exit 1
fi

INPUT="$1"
LANGUAGE="${2:-}"
MODEL="${3:-small}"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: File not found: $INPUT" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Extract audio to temp wav (whisper works best with wav)
# ---------------------------------------------------------------------------
TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

AUDIO_WAV="${TMPDIR_WORK}/audio.wav"
echo "Extracting audio from: $INPUT" >&2
ffmpeg -y -loglevel error -i "$INPUT" \
  -ar 16000 -ac 1 -c:a pcm_s16le \
  "$AUDIO_WAV"

# ---------------------------------------------------------------------------
# Determine output directory and base name
# ---------------------------------------------------------------------------
INPUT_DIR="$(dirname "$INPUT")"
INPUT_BASE="$(basename "${INPUT%.*}")"
OUT_PREFIX="${INPUT_DIR}/${INPUT_BASE}"

# ---------------------------------------------------------------------------
# Run Whisper transcription
# ---------------------------------------------------------------------------
WHISPER_ARGS=("$AUDIO_WAV" "--model" "$MODEL" "--output_dir" "$INPUT_DIR" "--output_format" "all")

if [[ -n "$LANGUAGE" ]]; then
  WHISPER_ARGS+=("--language" "$LANGUAGE")
fi

echo "Transcribing with Whisper (model=$MODEL${LANGUAGE:+, lang=$LANGUAGE})..." >&2
whisper "${WHISPER_ARGS[@]}" 2>&1 | grep -v "^$" | sed 's/^/  [whisper] /' >&2

# Whisper names output after the input filename (audio.txt, audio.srt, etc.)
WHISPER_TXT="${INPUT_DIR}/audio.txt"
WHISPER_SRT="${INPUT_DIR}/audio.srt"

# Rename to match source video name
TXT_OUT="${OUT_PREFIX}.txt"
SRT_OUT="${OUT_PREFIX}.srt"

[[ -f "$WHISPER_TXT" ]] && mv "$WHISPER_TXT" "$TXT_OUT"
[[ -f "$WHISPER_SRT" ]] && mv "$WHISPER_SRT" "$SRT_OUT"

echo "Transcript: $TXT_OUT" >&2
[[ -f "$SRT_OUT" ]] && echo "Subtitles:  $SRT_OUT" >&2

# Output transcript path to stdout for pipeline use
echo "$TXT_OUT"
