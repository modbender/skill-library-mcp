#!/usr/bin/env bash
set -euo pipefail

# Piper Speak — Generate voice audio for OpenClaw delivery
# Usage: piper-speak.sh "<text>" [voice]
# Output: MP3 path ready for [[audio_as_voice]] delivery

TEXT="${1:?Usage: piper-speak.sh \"<text>\" [voice]}"
VOICE="${2:-en_US-kusal-medium}"
VOICES_DIR="${PIPER_VOICES_DIR:-$HOME/.local/share/piper-voices}"

# Also check common locations
if [[ ! -f "$VOICES_DIR/${VOICE}.onnx" ]]; then
  for alt_dir in "$HOME/Documents/resources/piper-voices" "/usr/share/piper-voices"; do
    if [[ -f "$alt_dir/${VOICE}.onnx" ]]; then
      VOICES_DIR="$alt_dir"
      break
    fi
  done
fi

if [[ ! -f "$VOICES_DIR/${VOICE}.onnx" ]]; then
  echo "❌ Voice not found: $VOICE" >&2
  echo "   Run: setup-piper.sh --voice $VOICE" >&2
  exit 1
fi

# Output to temp directory (OpenClaw media delivery compatible)
OUT_DIR="${TMPDIR:-/tmp}/tts-piper"
mkdir -p "$OUT_DIR"
OUT_WAV="$OUT_DIR/voice-$(date +%s%N | cut -c1-13).wav"
OUT_MP3="${OUT_WAV%.wav}.mp3"

# Generate speech
echo "$TEXT" | python3 -m piper --data-dir "$VOICES_DIR" -m "$VOICE" -f "$OUT_WAV" 2>/dev/null

# Convert to MP3
ffmpeg -y -loglevel error -i "$OUT_WAV" -codec:a libmp3lame -qscale:a 4 "$OUT_MP3"

# Cleanup WAV
rm -f "$OUT_WAV"

# Output MP3 path (agent copies this into reply)
echo "$OUT_MP3"
