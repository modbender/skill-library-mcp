#!/bin/bash
# type.sh — Type text into the currently focused window
set -e

# --- Defaults ---
TEXT=""
DELAY=""
WINDOW_NAME=""
JSON_OUTPUT=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --delay)
            DELAY="$2"
            shift 2
            ;;
        --window)
            WINDOW_NAME="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            echo "Usage: type.sh [--delay MS] [--window NAME] [--json] TEXT"
            echo ""
            echo "Options:"
            echo "  --delay MS      Delay in milliseconds between keystrokes"
            echo "  --window NAME   Focus window before typing"
            echo "  --json          Output result as JSON"
            echo "  TEXT            The text to type (last positional argument)"
            exit 0
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2
            exit 1
            ;;
        *)
            TEXT="$1"
            shift
            ;;
    esac
done

# --- Check DISPLAY ---
if [ -z "$DISPLAY" ]; then
    if $JSON_OUTPUT; then
        echo '{"success": false, "output": null, "error": "DISPLAY not set. Run: export DISPLAY=:0"}'
    else
        echo "ERROR: DISPLAY not set. Run: export DISPLAY=:0" >&2
    fi
    exit 1
fi

# --- Validate text ---
if [ -z "$TEXT" ]; then
    MSG="No text provided"
    if $JSON_OUTPUT; then
        echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
    else
        echo "ERROR: $MSG" >&2
    fi
    exit 1
fi

# --- Focus window if specified ---
if [ -n "$WINDOW_NAME" ]; then
    WIN_ID=$(xdotool search --name "$WINDOW_NAME" | head -1)
    if [ -z "$WIN_ID" ]; then
        MSG="Window not found: $WINDOW_NAME"
        if $JSON_OUTPUT; then
            echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
        else
            echo "ERROR: $MSG" >&2
        fi
        exit 1
    fi
    xdotool windowfocus --sync "$WIN_ID"
    sleep 0.2
fi

# --- Type text ---
CMD="xdotool type --clearmodifiers"
if [ -n "$DELAY" ]; then
    CMD="$CMD --delay $DELAY"
fi

$CMD -- "$TEXT"

# --- Output ---
CHAR_COUNT=${#TEXT}
if $JSON_OUTPUT; then
    echo "{\"success\": true, \"output\": \"Typed $CHAR_COUNT characters\", \"error\": null}"
else
    echo "Typed $CHAR_COUNT characters"
fi
