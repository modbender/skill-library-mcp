#!/bin/bash
# scroll.sh — Scroll at the current mouse position or specified coordinates
set -e

# --- Defaults ---
DIRECTION=""
AMOUNT=3
X=""
Y=""
JSON_OUTPUT=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --direction)
            DIRECTION="$2"
            shift 2
            ;;
        --amount)
            AMOUNT="$2"
            shift 2
            ;;
        --x)
            X="$2"
            shift 2
            ;;
        --y)
            Y="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            echo "Usage: scroll.sh --direction up|down [--amount N] [--x X --y Y] [--json]"
            echo ""
            echo "Options:"
            echo "  --direction DIR   Scroll direction: up or down (required)"
            echo "  --amount N        Number of scroll ticks (default: 3)"
            echo "  --x X             Move mouse to X before scrolling"
            echo "  --y Y             Move mouse to Y before scrolling"
            echo "  --json            Output result as JSON"
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

# --- Validate direction ---
if [ -z "$DIRECTION" ]; then
    MSG="--direction is required (up or down)"
    if $JSON_OUTPUT; then
        echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
    else
        echo "ERROR: $MSG" >&2
    fi
    exit 1
fi

# Map direction to X11 button: 4 = scroll up, 5 = scroll down
case "$DIRECTION" in
    up)   SCROLL_BTN=4 ;;
    down) SCROLL_BTN=5 ;;
    *)
        MSG="Unknown direction: $DIRECTION (use up or down)"
        if $JSON_OUTPUT; then
            echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
        else
            echo "ERROR: $MSG" >&2
        fi
        exit 1
        ;;
esac

# --- Move mouse if coordinates given ---
if [ -n "$X" ] && [ -n "$Y" ]; then
    xdotool mousemove "$X" "$Y"
    sleep 0.05
fi

# --- Scroll ---
xdotool click --repeat "$AMOUNT" --delay 50 "$SCROLL_BTN"

# --- Output ---
if $JSON_OUTPUT; then
    echo "{\"success\": true, \"output\": \"Scrolled $DIRECTION $AMOUNT ticks\", \"error\": null}"
else
    echo "Scrolled $DIRECTION $AMOUNT ticks"
fi
