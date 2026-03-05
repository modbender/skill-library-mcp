#!/usr/bin/env bash
set -euo pipefail

# ElevenLabs Realtime STT (WebSocket) streamer
# Requires: ffmpeg, websocat, python3

if ! command -v websocat >/dev/null 2>&1; then
  echo "Error: websocat is required. Install: brew install websocat" >&2
  exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Error: ffmpeg is required. Install: brew install ffmpeg" >&2
  exit 1
fi

if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  echo "Error: ELEVENLABS_API_KEY not set" >&2
  exit 1
fi

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Usage: $(basename "$0") /path/to/audio.ogg" >&2
  exit 1
fi

MODEL_ID="scribe_v2_realtime"
AUDIO_FORMAT="pcm_16000" # 16k mono PCM
CHUNK_MS="200"

WS_URL="wss://api.elevenlabs.io/v1/speech-to-text/realtime?model_id=${MODEL_ID}&audio_format=${AUDIO_FORMAT}&include_timestamps=true"

# Convert to raw PCM and stream as base64 JSON chunks
python3 - <<'PY' "$FILE" "$CHUNK_MS" | \
  websocat "$WS_URL" -t -H "xi-api-key: ${ELEVENLABS_API_KEY}"
import sys, base64, json, subprocess

file_path = sys.argv[1]
chunk_ms = int(sys.argv[2])

# PCM 16k mono 16‑bit
sample_rate = 16000
bytes_per_sample = 2
bytes_per_ms = int(sample_rate * bytes_per_sample / 1000)
chunk_bytes = bytes_per_ms * chunk_ms

# ffmpeg -> raw PCM
cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error",
    "-i", file_path,
    "-ac", "1", "-ar", str(sample_rate), "-f", "s16le", "pipe:1"
]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

# Stream chunks (commit on final chunk)
chunk = proc.stdout.read(chunk_bytes)
while chunk:
    next_chunk = proc.stdout.read(chunk_bytes)
    commit = False if next_chunk else True
    b64 = base64.b64encode(chunk).decode("ascii")
    msg = {
        "message_type": "input_audio_chunk",
        "audio_base_64": b64,
        "commit": commit,
        "sample_rate": sample_rate,
    }
    print(json.dumps(msg), flush=True)
    chunk = next_chunk
PY
