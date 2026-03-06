#!/bin/bash
# Capture a screenshot and output base64 for vision model analysis.
# The screenshot is NOT persisted -- only the semantic summary should be stored.

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
TEMP_FILE=$(mktemp /tmp/intent_guardian_screen_XXXXXX.png)

mkdir -p "$LOG_DIR"

cleanup() {
    rm -f "$TEMP_FILE"
}
trap cleanup EXIT

if [[ "$(uname)" == "Darwin" ]]; then
    screencapture -x -C "$TEMP_FILE" 2>/dev/null
elif command -v scrot &>/dev/null; then
    scrot "$TEMP_FILE" 2>/dev/null
elif command -v gnome-screenshot &>/dev/null; then
    gnome-screenshot -f "$TEMP_FILE" 2>/dev/null
else
    echo '{"error": "No screenshot tool available"}'
    exit 1
fi

if [ ! -s "$TEMP_FILE" ]; then
    echo '{"error": "Screenshot capture failed"}'
    exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
B64=$(base64 < "$TEMP_FILE" | tr -d '\n')
SIZE=$(wc -c < "$TEMP_FILE" | tr -d ' ')

cat <<EOF
{"ts": "$TIMESTAMP", "type": "screenshot", "size_bytes": $SIZE, "base64": "$B64"}
EOF
