#!/bin/bash
# click.sh — Move mouse and click at coordinates, optionally relative to a window
set -e

# --- Defaults ---
X=""
Y=""
BUTTON="left"
DOUBLE=false
WINDOW_NAME=""
JSON_OUTPUT=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --x)
            X="$2"
            shift 2
            ;;
        --y)
            Y="$2"
            shift 2
            ;;
        --button)
            BUTTON="$2"
            shift 2
            ;;
        --double)
            DOUBLE=true
            shift
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
            echo "Usage: click.sh --x X --y Y [--button left|right|middle] [--double] [--window NAME] [--json]"
            echo ""
            echo "Options:"
            echo "  --x X           X coordinate"
            echo "  --y Y           Y coordinate"
            echo "  --button TYPE   Button: left (default), right, middle"
            echo "  --double        Double-click"
            echo "  --window NAME   Click relative to window position"
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

# --- Validate coordinates ---
if [ -z "$X" ] || [ -z "$Y" ]; then
    MSG="Both --x and --y are required"
    if $JSON_OUTPUT; then
        echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
    else
        echo "ERROR: $MSG" >&2
    fi
    exit 1
fi

# --- Map button name to xdotool button number ---
case "$BUTTON" in
    left)   BTN_NUM=1 ;;
    middle) BTN_NUM=2 ;;
    right)  BTN_NUM=3 ;;
    *)
        MSG="Unknown button: $BUTTON (use left, right, or middle)"
        if $JSON_OUTPUT; then
            echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
        else
            echo "ERROR: $MSG" >&2
        fi
        exit 1
        ;;
esac

# --- Window-relative click ---
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

    # Get window position
    GEOM=$(xdotool getwindowgeometry --shell "$WIN_ID")
    WIN_X=$(echo "$GEOM" | grep "^X=" | cut -d= -f2)
    WIN_Y=$(echo "$GEOM" | grep "^Y=" | cut -d= -f2)

    # Calculate absolute coordinates
    X=$((WIN_X + X))
    Y=$((WIN_Y + Y))
fi

# --- Move and click ---
xdotool mousemove "$X" "$Y"

if $DOUBLE; then
    xdotool click --repeat 2 --delay 50 "$BTN_NUM"
else
    xdotool click "$BTN_NUM"
fi

# Short pause to let UI respond
sleep 0.1

# --- Output ---
if $JSON_OUTPUT; then
    echo "{\"success\": true, \"output\": \"Clicked $BUTTON at ($X, $Y)\", \"error\": null}"
else
    echo "Clicked $BUTTON at ($X, $Y)"
fi
