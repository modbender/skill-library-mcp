#!/bin/bash
# Start VEA server in tmux session
# Usage: ./start_server.sh [port]

PORT="${1:-8000}"
VEA_DIR="${VEA_DIR:-$HOME/vea}"
SESSION="vea-server"
SOCKET="/tmp/openclaw-tmux-sockets/openclaw.sock"

# Create socket directory if needed
mkdir -p "$(dirname "$SOCKET")"

# Check if session already exists
if tmux -S "$SOCKET" has-session -t "$SESSION" 2>/dev/null; then
    echo "VEA server already running in tmux session '$SESSION'"
    echo "To view: tmux -S $SOCKET attach -t $SESSION"
    echo "To kill: tmux -S $SOCKET kill-session -t $SESSION"
    exit 0
fi

# Start new session
echo "Starting VEA server on port $PORT..."
tmux -S "$SOCKET" new-session -d -s "$SESSION" \
    "cd $VEA_DIR && source .venv/bin/activate && python src/app.py --port $PORT; read"

sleep 2

# Verify it started
if curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
    echo "VEA server started successfully on http://localhost:$PORT"
    echo "View logs: tmux -S $SOCKET attach -t $SESSION"
else
    echo "Server starting... (may take a few seconds)"
    echo "Check: curl http://localhost:$PORT/"
fi
