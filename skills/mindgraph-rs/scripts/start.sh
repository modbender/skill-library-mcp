#!/bin/bash
# mindgraph-server start script
# Starts the server if not already running, or restarts if forced

PIDFILE=/tmp/mindgraph-server.pid
BINARY=/home/node/.openclaw/bin/mindgraph-server
LOGFILE=/tmp/mindgraph-server.log
CONFIG=/home/node/.openclaw/mindgraph.json

# Read config from mindgraph.json (kept separate from openclaw.json to avoid gateway validation errors)
TOKEN=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['token'])")
PORT=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['port'])")
DB_PATH=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['db_path'])")
BIND=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['bind'])")
DEFAULT_AGENT=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['default_agent'])")

# Check if already running
if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "mindgraph-server already running (PID $PID)"
    exit 0
  else
    rm -f "$PIDFILE"
  fi
fi

export MINDGRAPH_TOKEN="$TOKEN"
export MINDGRAPH_PORT="$PORT"
export MINDGRAPH_DB_PATH="$DB_PATH"
export MINDGRAPH_BIND="$BIND"
export MINDGRAPH_DEFAULT_AGENT="$DEFAULT_AGENT"

# Embeddings — load OPENAI_API_KEY from workspace .env if not already set
if [ -z "$OPENAI_API_KEY" ]; then
  OPENAI_API_KEY=$(grep -v '^#' "$(dirname "$0")/../../.env" 2>/dev/null | grep '^OPENAI_API_KEY=' | cut -d= -f2-)
  export OPENAI_API_KEY
fi
export MINDGRAPH_EMBEDDING_MODEL="text-embedding-3-small"

# Use nohup + setsid to fully detach from gateway process group.
# This ensures the server survives gateway restarts (which kill child processes).
nohup setsid "$BINARY" >> "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"
disown $!
echo "mindgraph-server started (PID $(cat $PIDFILE))"
