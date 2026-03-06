#!/bin/bash
# video-download-faas/scripts/download.sh
# Start video download in background and return immediately

set -e

URL="$1"
OUTPUT_DIR="${2:-$HOME/Downloads}"
SESSION_NAME="video_dl_$(date +%s)_$$"

if [ -z "$URL" ]; then
    echo "Error: URL required"
    echo "Usage: download.sh <URL> [output_directory]"
    exit 1
fi

# Create output directory if not exists
mkdir -p "$OUTPUT_DIR"

# Generate unique session file
SESSION_FILE="/tmp/${SESSION_NAME}.session"
PID_FILE="/tmp/${SESSION_NAME}.pid"
LOG_FILE="/tmp/${SESSION_NAME}.log"

# Start download in background with nohup
# Force MP4 output format
nohup yt-dlp \
    --no-warnings \
    --progress \
    --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
    --merge-output-format mp4 \
    --recode-video mp4 \
    -o "${OUTPUT_DIR}/%(title)s.%(ext)s" \
    "$URL" > "$LOG_FILE" 2>&1 &

# Save PID
PID=$!
echo $PID > "$PID_FILE"

# Save session info
cat > "$SESSION_FILE" <<EOF
{
  "session_id": "$SESSION_NAME",
  "pid": $PID,
  "url": "$URL",
  "output_dir": "$OUTPUT_DIR",
  "log_file": "$LOG_FILE",
  "pid_file": "$PID_FILE",
  "status": "running",
  "started_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

# Return immediately with session info
echo "✅ Download started in background"
echo ""
echo "Session ID: $SESSION_NAME"
echo "PID: $PID"
echo "Log: $LOG_FILE"
echo ""
echo "To check status: check-status.sh $SESSION_NAME"
echo "To kill: kill-download.sh $SESSION_NAME"
