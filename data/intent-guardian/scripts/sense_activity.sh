#!/bin/bash
# Sense active window on macOS using osascript (no dependencies required).
# Outputs a JSON line to stdout for each poll.

POLL_INTERVAL="${INTENT_GUARDIAN_POLL_INTERVAL:-5}"
LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
LOG_FILE="$LOG_DIR/activity_log.jsonl"

mkdir -p "$LOG_DIR"

get_active_window() {
    osascript -e '
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        set frontAppId to bundle identifier of first application process whose frontmost is true
    end tell
    tell application frontApp
        try
            set windowTitle to name of front window
        on error
            set windowTitle to "N/A"
        end try
    end tell
    return frontApp & "|" & frontAppId & "|" & windowTitle
    ' 2>/dev/null
}

while true; do
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    RAW=$(get_active_window)

    if [ -n "$RAW" ]; then
        APP_NAME=$(echo "$RAW" | cut -d'|' -f1)
        BUNDLE_ID=$(echo "$RAW" | cut -d'|' -f2)
        WINDOW_TITLE=$(echo "$RAW" | cut -d'|' -f3-)

        # Escape special JSON characters
        APP_NAME=$(echo "$APP_NAME" | sed 's/\\/\\\\/g; s/"/\\"/g')
        WINDOW_TITLE=$(echo "$WINDOW_TITLE" | sed 's/\\/\\\\/g; s/"/\\"/g')

        ENTRY="{\"ts\":\"$TIMESTAMP\",\"app\":\"$APP_NAME\",\"bundle\":\"$BUNDLE_ID\",\"title\":\"$WINDOW_TITLE\"}"
        echo "$ENTRY" >> "$LOG_FILE"
        echo "$ENTRY"
    fi

    sleep "$POLL_INTERVAL"
done
