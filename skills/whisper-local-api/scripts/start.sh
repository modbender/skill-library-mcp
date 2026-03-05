#!/usr/bin/env bash
set -euo pipefail

WHISPER_DIR="${WHISPER_DIR:-$HOME/whisper-local-api}"

if [ ! -f "$WHISPER_DIR/run_server.sh" ]; then
  echo "run_server.sh not found in $WHISPER_DIR"
  echo "Please run: bash scripts/bootstrap.sh"
  exit 1
fi

cd "$WHISPER_DIR"

# Check if port 9000 is open before starting
if lsof -i :9000 >/dev/null 2>&1; then
  echo "Warning: Port 9000 is already in use (possibly another Whisper instance running). Proceeding..."
fi

echo "Starting local, offline Whisper ASR safely..."
bash run_server.sh &
SERVER_PID=$!
echo "Whisper local API started with PID $SERVER_PID"
