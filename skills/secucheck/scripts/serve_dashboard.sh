#!/bin/bash
# Generate dashboard and serve it
# Usage: ./serve_dashboard.sh [port] [lang]
# lang: ko, en, ja, zh (default: ko)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8766}"
LANG="${2:-ko}"
OUTPUT_DIR="$HOME/.openclaw/workspace"
OUTPUT_FILE="$OUTPUT_DIR/secucheck-report.html"

# Kill any existing server on this port
pkill -f "http.server $PORT" 2>/dev/null || true
sleep 0.5

# Generate dashboard (use bash explicitly - ClawHub may strip exec permissions)
bash "$SCRIPT_DIR/generate_dashboard.sh" "$OUTPUT_FILE" "$LANG" >/dev/null 2>&1

# Get local IP for the URL
LOCAL_IP=""
if command -v hostname &>/dev/null; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)192\.\d+\.\d+\.\d+' | head -1)
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ifconfig 2>/dev/null | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="localhost"
fi

# Start server in background (bind to 0.0.0.0)
cd "$OUTPUT_DIR"
nohup python3 -m http.server "$PORT" --bind 0.0.0.0 > /tmp/secucheck-server.log 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 1

# Check if server started
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "{"
    echo '  "status": "ok",'
    echo '  "url": "http://'"$LOCAL_IP"':'"$PORT"'/secucheck-report.html",'
    echo '  "local_url": "http://localhost:'"$PORT"'/secucheck-report.html",'
    echo '  "pid": '"$SERVER_PID"','
    echo '  "file": "'"$OUTPUT_FILE"'"'
    echo "}"
else
    echo '{"status": "error", "message": "Failed to start server"}'
    exit 1
fi
