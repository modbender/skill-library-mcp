#!/bin/bash
# capture.sh — Take a screenshot of the full screen or a specific window
# Outputs the saved file path on the last line of stdout
set -e

# --- Defaults ---
OUTPUT=""
WINDOW_NAME=""
JSON_OUTPUT=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --window)
            WINDOW_NAME="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            echo "Usage: capture.sh [--window NAME] [--output PATH] [--json]"
            echo ""
            echo "Options:"
            echo "  --window NAME   Capture a specific window by name"
            echo "  --output PATH   Save screenshot to this path (default: /tmp/linux-desktop-capture-TIMESTAMP.png)"
            echo "  --json          Output result as JSON"
            exit 0
            ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            exit 1
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

# --- Default output path ---
if [ -z "$OUTPUT" ]; then
    OUTPUT="/tmp/linux-desktop-capture-$(date +%s).png"
fi

# --- Capture ---
if [ -n "$WINDOW_NAME" ]; then
    # Find the window ID by name
    WIN_ID=$(xdotool search --name "$WINDOW_NAME" | head -1)
    if [ -z "$WIN_ID" ]; then
        if $JSON_OUTPUT; then
            echo "{\"success\": false, \"output\": null, \"error\": \"Window not found: $WINDOW_NAME\"}"
        else
            echo "ERROR: Window not found: $WINDOW_NAME" >&2
        fi
        exit 1
    fi

    # Try import (ImageMagick) first for window-specific capture, fall back to scrot
    if command -v import &>/dev/null; then
        import -window "$WIN_ID" "$OUTPUT"
    else
        # Focus the window then use scrot -u (focused window)
        xdotool windowactivate --sync "$WIN_ID"
        sleep 0.3
        scrot -u "$OUTPUT"
    fi
else
    # Full screen capture
    scrot "$OUTPUT"
fi

# --- Output ---
if $JSON_OUTPUT; then
    echo "{\"success\": true, \"output\": \"$OUTPUT\", \"error\": null}"
else
    echo "Screenshot saved: $OUTPUT"
    echo "$OUTPUT"
fi
