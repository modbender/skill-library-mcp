#!/bin/bash
# hotkey.sh — Send keyboard shortcuts/hotkeys
set -e

# --- Defaults ---
KEYS=""
JSON_OUTPUT=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            echo "Usage: hotkey.sh [--json] KEYS"
            echo ""
            echo "Options:"
            echo "  --json   Output result as JSON"
            echo "  KEYS     Key combination (e.g., ctrl+c, alt+F4, super+d, Return, Tab)"
            echo ""
            echo "Key names follow X11 conventions:"
            echo "  Return, Tab, Escape, BackSpace, Delete, Home, End,"
            echo "  Page_Up, Page_Down, F1-F12, super, ctrl, alt, shift"
            exit 0
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2
            exit 1
            ;;
        *)
            KEYS="$1"
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

# --- Validate keys ---
if [ -z "$KEYS" ]; then
    MSG="No key combination provided"
    if $JSON_OUTPUT; then
        echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
    else
        echo "ERROR: $MSG" >&2
    fi
    exit 1
fi

# --- Send key combination ---
xdotool key --clearmodifiers "$KEYS"

# --- Output ---
if $JSON_OUTPUT; then
    echo "{\"success\": true, \"output\": \"Sent hotkey: $KEYS\", \"error\": null}"
else
    echo "Sent hotkey: $KEYS"
fi
