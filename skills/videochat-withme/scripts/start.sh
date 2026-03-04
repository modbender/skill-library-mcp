#!/bin/bash
# Start videochat-withme service
set -e
cd "$(dirname "$0")"

PLIST_LABEL="com.openclaw.videochat-withme"
PORT=${PORT:-8766}

# If launchd service is installed, use it
if launchctl list "$PLIST_LABEL" >/dev/null 2>&1; then
  launchctl start "$PLIST_LABEL"
  echo "✅ Started via launchd"
  exit 0
fi

# Fallback: direct run (first time before setup.sh)
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 required. Run setup.sh first."; exit 1; }
command -v ffmpeg  >/dev/null 2>&1 || { echo "❌ ffmpeg required. Run setup.sh first."; exit 1; }

pip3 install --break-system-packages -q fastapi uvicorn python-multipart httpx edge-tts 2>/dev/null || \
  pip3 install -q fastapi uvicorn python-multipart httpx edge-tts

exec python3 server.py
