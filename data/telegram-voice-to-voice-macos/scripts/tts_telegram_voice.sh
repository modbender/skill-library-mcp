#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   tts_telegram_voice.sh "text..." [voiceName]
# Outputs: path to .ogg (opus) on stdout.

TEXT="${1:-}"
VOICE="${2:-SYSTEM}"

if [[ -z "${TEXT}" ]]; then
  echo "ERROR: text required" >&2
  exit 2
fi

if ! command -v say >/dev/null 2>&1; then
  echo "ERROR: say not found" >&2
  exit 3
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not found" >&2
  exit 4
fi

OUT_DIR="${HOME}/.openclaw/workspace/voice_out"
mkdir -p "${OUT_DIR}"

# Use a timestamp + random suffix to avoid collisions without requiring python.
TS="$(date +%s)-${RANDOM}"
AIFF="${OUT_DIR}/tts-${TS}.aiff"
OGG="${OUT_DIR}/tts-${TS}.ogg"

# Create AIFF via macOS TTS.
# If VOICE=SYSTEM, use the current system voice.
# Some macOS versions are picky about data-format flags; keep it simple.
if [[ "${VOICE}" == "SYSTEM" ]]; then
  say -o "${AIFF}" "${TEXT}"
else
  say -v "${VOICE}" -o "${AIFF}" "${TEXT}"
fi

# Convert to OGG/Opus suitable for Telegram voice notes.
ffmpeg -hide_banner -loglevel error -y \
  -i "${AIFF}" \
  -c:a libopus -b:a 32k -vbr on -compression_level 10 \
  "${OGG}"

rm -f "${AIFF}"

echo "${OGG}"
