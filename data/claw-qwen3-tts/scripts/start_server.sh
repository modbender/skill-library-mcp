#!/usr/bin/env bash
# start_server.sh — Launch the Qwen3-TTS FastAPI server
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$SKILL_DIR/.venv"
PIDFILE="$SKILL_DIR/.server.pid"
LOGFILE="$SKILL_DIR/server.log"
PORT="${TTS_PORT:-8880}"
HOST="${TTS_HOST:-127.0.0.1}"

# Check venv exists
if [ ! -d "$VENV" ]; then
    echo "[ERROR] Virtual environment not found. Run setup_env.sh first."
    exit 1
fi

# Check if already running
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[INFO] Server already running (PID $PID) on $HOST:$PORT"
        exit 0
    else
        echo "[WARN] Stale PID file found, removing..."
        rm -f "$PIDFILE"
    fi
fi

# Activate venv and start
source "$VENV/bin/activate"
cd "$SKILL_DIR/server"

echo "[INFO] Starting Qwen3-TTS server on $HOST:$PORT ..."
nohup python -m uvicorn tts_server:app \
    --host "$HOST" \
    --port "$PORT" \
    --log-level info \
    > "$LOGFILE" 2>&1 &

echo $! > "$PIDFILE"
echo "[OK] Server started (PID $!) — logs at $LOGFILE"

# Wait briefly and check it's actually running
sleep 2
if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[OK] Server is running"
else
    echo "[ERROR] Server failed to start. Check $LOGFILE"
    rm -f "$PIDFILE"
    exit 1
fi
