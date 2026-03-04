#!/bin/bash
# video-download-faas/scripts/kill-download.sh
# Kill background video download process

SESSION_ID="$1"
FORCE="${2:-false}"

if [ -z "$SESSION_ID" ]; then
    echo "Error: Session ID required"
    echo "Usage: kill-download.sh <session_id> [--force]"
    echo ""
    echo "Active sessions:"
    for pid_file in /tmp/video_dl_*.pid; do
        if [ -f "$pid_file" ]; then
            SESSION_NAME=$(basename "$pid_file" .pid)
            PID=$(cat "$pid_file")
            if kill -0 "$PID" 2>/dev/null; then
                echo "  - $SESSION_NAME (PID: $PID)"
            fi
        fi
    done
    exit 1
fi

SESSION_FILE="/tmp/${SESSION_ID}.session"
PID_FILE="/tmp/${SESSION_ID}.pid"
LOG_FILE="/tmp/${SESSION_ID}.log"

if [ ! -f "$PID_FILE" ]; then
    echo "Error: Process not found for session: $SESSION_ID"
    exit 1
fi

PID=$(cat "$PID_FILE")

# Check if process exists
if ! kill -0 "$PID" 2>/dev/null; then
    echo "Process already terminated (PID: $PID)"
    rm -f "$SESSION_FILE" "$PID_FILE" "$LOG_FILE"
    exit 0
fi

echo "Stopping download process..."
echo "Session: $SESSION_ID"
echo "PID: $PID"

if [ "$FORCE" = "--force" ]; then
    # Force kill
    kill -9 "$PID" 2>/dev/null
    echo "✅ Force killed process $PID"
else
    # Graceful kill
    kill "$PID" 2>/dev/null
    sleep 2
    
    # Check if still running
    if kill -0 "$PID" 2>/dev/null; then
        echo "Process still running, forcing kill..."
        kill -9 "$PID" 2>/dev/null
    fi
    echo "✅ Process stopped"
fi

# Cleanup
rm -f "$SESSION_FILE" "$PID_FILE" "$LOG_FILE"

echo ""
echo "Session cleaned up"
