#!/bin/bash
# window.sh — Window management: focus, minimize, maximize, close, move, resize, list
set -e

# --- Defaults ---
ACTION=""
WINDOW_NAME=""
X=""
Y=""
WIDTH=""
HEIGHT=""
JSON_OUTPUT=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --action)
            ACTION="$2"
            shift 2
            ;;
        --window)
            WINDOW_NAME="$2"
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
        --width)
            WIDTH="$2"
            shift 2
            ;;
        --height)
            HEIGHT="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            echo "Usage: window.sh --action ACTION --window NAME [options] [--json]"
            echo ""
            echo "Actions:"
            echo "  focus      Focus/raise window"
            echo "  minimize   Minimize window"
            echo "  maximize   Maximize window"
            echo "  close      Close window"
            echo "  move       Move window (requires --x and --y)"
            echo "  resize     Resize window (requires --width and --height)"
            echo "  list       List all windows (alias for inspect.sh)"
            echo ""
            echo "Options:"
            echo "  --window NAME    Window name to match"
            echo "  --x X            X position (for move)"
            echo "  --y Y            Y position (for move)"
            echo "  --width W        Width (for resize)"
            echo "  --height H       Height (for resize)"
            echo "  --json           Output result as JSON"
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

# --- Validate action ---
if [ -z "$ACTION" ]; then
    MSG="--action is required"
    if $JSON_OUTPUT; then
        echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
    else
        echo "ERROR: $MSG" >&2
    fi
    exit 1
fi

# --- Handle list action (delegate to inspect.sh) ---
if [ "$ACTION" = "list" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if $JSON_OUTPUT; then
        exec bash "$SCRIPT_DIR/inspect.sh" --json
    else
        exec bash "$SCRIPT_DIR/inspect.sh"
    fi
fi

# --- Validate window name for all other actions ---
if [ -z "$WINDOW_NAME" ]; then
    MSG="--window is required for action: $ACTION"
    if $JSON_OUTPUT; then
        echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
    else
        echo "ERROR: $MSG" >&2
    fi
    exit 1
fi

# --- Perform action ---
case "$ACTION" in
    focus)
        # Try wmctrl first (fuzzy match), fall back to xdotool
        if command -v wmctrl &>/dev/null; then
            wmctrl -a "$WINDOW_NAME"
        else
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
            xdotool windowactivate "$WIN_ID"
        fi
        RESULT="Focused window: $WINDOW_NAME"
        ;;

    minimize)
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
        xdotool windowminimize "$WIN_ID"
        RESULT="Minimized window: $WINDOW_NAME"
        ;;

    maximize)
        if ! command -v wmctrl &>/dev/null; then
            MSG="wmctrl required for maximize. Run: bash install.sh"
            if $JSON_OUTPUT; then
                echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
            else
                echo "ERROR: $MSG" >&2
            fi
            exit 1
        fi
        wmctrl -r "$WINDOW_NAME" -b add,maximized_vert,maximized_horz
        RESULT="Maximized window: $WINDOW_NAME"
        ;;

    close)
        if command -v wmctrl &>/dev/null; then
            wmctrl -c "$WINDOW_NAME"
        else
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
            xdotool windowclose "$WIN_ID"
        fi
        RESULT="Closed window: $WINDOW_NAME"
        ;;

    move)
        if [ -z "$X" ] || [ -z "$Y" ]; then
            MSG="--x and --y are required for move"
            if $JSON_OUTPUT; then
                echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
            else
                echo "ERROR: $MSG" >&2
            fi
            exit 1
        fi
        if command -v wmctrl &>/dev/null; then
            wmctrl -r "$WINDOW_NAME" -e "0,$X,$Y,-1,-1"
        else
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
            xdotool windowmove "$WIN_ID" "$X" "$Y"
        fi
        RESULT="Moved window '$WINDOW_NAME' to ($X, $Y)"
        ;;

    resize)
        if [ -z "$WIDTH" ] || [ -z "$HEIGHT" ]; then
            MSG="--width and --height are required for resize"
            if $JSON_OUTPUT; then
                echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
            else
                echo "ERROR: $MSG" >&2
            fi
            exit 1
        fi
        if command -v wmctrl &>/dev/null; then
            wmctrl -r "$WINDOW_NAME" -e "0,-1,-1,$WIDTH,$HEIGHT"
        else
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
            xdotool windowsize "$WIN_ID" "$WIDTH" "$HEIGHT"
        fi
        RESULT="Resized window '$WINDOW_NAME' to ${WIDTH}x${HEIGHT}"
        ;;

    *)
        MSG="Unknown action: $ACTION (use focus, minimize, maximize, close, move, resize, list)"
        if $JSON_OUTPUT; then
            echo "{\"success\": false, \"output\": null, \"error\": \"$MSG\"}"
        else
            echo "ERROR: $MSG" >&2
        fi
        exit 1
        ;;
esac

# --- Output ---
if $JSON_OUTPUT; then
    echo "{\"success\": true, \"output\": \"$RESULT\", \"error\": null}"
else
    echo "$RESULT"
fi
