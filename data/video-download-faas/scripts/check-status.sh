#!/bin/bash
# video-download-faas/scripts/check-status.sh
# Check status of background video download

SESSION_ID="$1"

if [ -z "$SESSION_ID" ]; then
    # List all active sessions
    echo "Active download sessions:"
    echo "========================"
    for session_file in /tmp/video_dl_*.session; do
        if [ -f "$session_file" ]; then
            SESSION_NAME=$(basename "$session_file" .session)
            if [ -f "/tmp/${SESSION_NAME}.pid" ]; then
                PID=$(cat "/tmp/${SESSION_NAME}.pid")
                if kill -0 "$PID" 2>/dev/null; then
                    echo "✅ $SESSION_NAME (PID: $PID) - Running"
                else
                    echo "✅ $SESSION_NAME - Completed"
                fi
            fi
        fi
    done
    echo ""
    echo "Usage: check-status.sh <session_id>"
    exit 0
fi

SESSION_FILE="/tmp/${SESSION_ID}.session"
PID_FILE="/tmp/${SESSION_ID}.pid"
LOG_FILE="/tmp/${SESSION_ID}.log"

if [ ! -f "$SESSION_FILE" ]; then
    echo "Error: Session not found: $SESSION_ID"
    exit 1
fi

# Parse session info (simple grep/sed approach)
URL=$(grep '"url"' "$SESSION_FILE" | sed 's/.*"url": "\([^"]*\)".*/\1/')
OUTPUT_DIR=$(grep '"output_dir"' "$SESSION_FILE" | sed 's/.*"output_dir": "\([^"]*\)".*/\1/')
STARTED_AT=$(grep '"started_at"' "$SESSION_FILE" | sed 's/.*"started_at": "\([^"]*\)".*/\1/')

# Check if process is running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        STATUS="🟢 RUNNING"
        
        # Show progress from log
        if [ -f "$LOG_FILE" ]; then
            echo "$STATUS"
            echo "============"
            echo "Session: $SESSION_ID"
            echo "PID: $PID"
            echo "URL: $URL"
            echo "Output: $OUTPUT_DIR"
            echo "Started: $STARTED_AT"
            echo ""
            echo "Recent progress:"
            tail -5 "$LOG_FILE" | grep -E "(download|progress|ETA)" || tail -3 "$LOG_FILE"
        fi
    else
        STATUS="✅ COMPLETED"
        echo "$STATUS"
        echo "============"
        echo "Session: $SESSION_ID"
        echo "URL: $URL"
        echo "Output: $OUTPUT_DIR"
        echo "Started: $STARTED_AT"
        echo ""
        
        # Show downloaded files
        echo "Downloaded files:"
        ls -lh "$OUTPUT_DIR"/*.{mp4,mkv,webm,mp3} 2>/dev/null | tail -5 || echo "No video files found in $OUTPUT_DIR"
        
        # Cleanup
        rm -f "$SESSION_FILE" "$PID_FILE" "$LOG_FILE"
    fi
else
    echo "⚠️  Session info incomplete"
fi
