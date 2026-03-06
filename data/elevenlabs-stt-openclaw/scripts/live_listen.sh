#!/usr/bin/env bash
set -euo pipefail
set +m  # disable job control messages

# Live Listener: mic → ElevenLabs realtime STT → optional response/TTS
# Requires: ffmpeg, websocat, python3

MODE="toggle"          # toggle | always
TTS_ENGINE="elevenlabs" # elevenlabs | say | none
PUSH_KEY="Q"            # key to toggle start/stop
DEVICE=":0"            # avfoundation device string (macOS)
LANG_CODE=""           # optional language code
VOICE_ID="${ELEVENLABS_VOICE_ID:-WNxHBFUm0NC5fojx98kr}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --mode) MODE="$2"; shift 2 ;;
    --tts) TTS_ENGINE="$2"; shift 2 ;;
    --key) PUSH_KEY="$2"; shift 2 ;;
    --device) DEVICE="$2"; shift 2 ;;
    --lang) LANG_CODE="$2"; shift 2 ;;
    --voice-id) VOICE_ID="$2"; shift 2 ;;
    -h|--help)
      cat << EOF2
Usage: $(basename "$0") [options]

Options:
  --mode toggle|always        Toggle start/stop or always-on (default: toggle)
  --tts elevenlabs|say|none   TTS engine (default: elevenlabs)
  --key KEY                   Toggle key (default: Q)
  --device DEVICE             Mic device for ffmpeg (default: :0)
  --lang CODE                 Language code hint (optional)
  --voice-id ID               ElevenLabs voice ID for TTS
EOF2
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

for bin in websocat ffmpeg python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Error: $bin is required" >&2; exit 1; }
done

if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  echo "Error: ELEVENLABS_API_KEY not set" >&2
  exit 1
fi

export RT_DEVICE="$DEVICE"
export RT_LANG="$LANG_CODE"
export RT_TTS="$TTS_ENGINE"
export RT_VOICE_ID="$VOICE_ID"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STREAMER="$SCRIPT_DIR/_realtime_stream.py"

if [[ "$MODE" == "always" ]]; then
  python3 "$STREAMER"
  exit 0
fi

# Toggle mode
cleanup() {
  stty echo
  if [[ -n "${STREAM_PID:-}" ]]; then
    kill "$STREAM_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

stty -echo -icanon time 0 min 0

listening=0
echo "Press $PUSH_KEY to start/stop. Ctrl+C to exit."

while true; do
  IFS= read -r -n1 key
  if [[ -z "$key" ]]; then
    sleep 0.05
    continue
  fi
  key_up=$(printf "%s" "$key" | tr '[:lower:]' '[:upper:]')
  push_up=$(printf "%s" "$PUSH_KEY" | tr '[:lower:]' '[:upper:]')
  if [[ "$key_up" == "$push_up" ]]; then
    if [[ $listening -eq 0 ]]; then
      python3 "$STREAMER" &
      STREAM_PID=$!
      listening=1
      echo "Listening…" >&2
    else
      kill "$STREAM_PID" 2>/dev/null || true
      wait "$STREAM_PID" 2>/dev/null || true
      listening=0
      echo "Stopped listening." >&2
    fi
  fi
  sleep 0.05

done
