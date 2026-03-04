#!/bin/bash
# AutoClipper Cron Launcher
# Add to crontab: 0 * * * * /path/to/this/script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Lock file to prevent overlapping runs
LOCK_FILE="$SKILL_DIR/logs/auto-clipper.lock"

# Check for existing process
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Already running (PID: $PID), exiting"
        exit 0
    fi
    rm "$LOCK_FILE"
fi

# Write our PID
echo $$ > "$LOCK_FILE"

# Run the clipper
cd "$SKILL_DIR"
python3 "$SCRIPT_DIR/auto_clipper.py" "$@"

# Cleanup
rm "$LOCK_FILE"