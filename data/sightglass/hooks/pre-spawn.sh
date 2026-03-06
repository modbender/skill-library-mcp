#!/usr/bin/env bash
set -euo pipefail

# Called before OpenClaw spawns a coding agent.
# Sets up session tracking and ensures the watcher is running.

PROJECT_DIR="${1:-$(pwd)}"
SESSION_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/sightglass/sessions"
mkdir -p "$SESSION_DIR"

# Record session start
SESSION_FILE="$SESSION_DIR/current"
cat > "$SESSION_FILE" <<EOF
{
  "start": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "start_epoch": $(date +%s),
  "project": "$PROJECT_DIR",
  "agent": "${OPENCLAW_AGENT:-unknown}"
}
EOF

echo "🔍 Sightglass: session started at $(date -u +%H:%M:%S)Z for $PROJECT_DIR"

# Ensure watcher is running
if ! pgrep -f "sightglass watch" &>/dev/null; then
  echo "🔍 Starting sightglass watcher..."
  sightglass watch --project "$PROJECT_DIR" &
  disown
fi
