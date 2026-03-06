#!/usr/bin/env bash
# stop_server.sh — Gracefully stop the Qwen3-TTS server
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$SKILL_DIR/.server.pid"

if [ ! -f "$PIDFILE" ]; then
    echo "[INFO] No server running (no PID file)"
    exit 0
fi

PID=$(cat "$PIDFILE")

if kill -0 "$PID" 2>/dev/null; then
    echo "[INFO] Stopping server (PID $PID)..."
    kill "$PID"

    # Wait up to 10 seconds for graceful shutdown
    for i in $(seq 1 10); do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done

    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        echo "[WARN] Server did not stop gracefully, force killing..."
        kill -9 "$PID" 2>/dev/null || true
    fi

    rm -f "$PIDFILE"
    echo "[OK] Server stopped"
else
    echo "[INFO] Server not running (stale PID file)"
    rm -f "$PIDFILE"
fi
