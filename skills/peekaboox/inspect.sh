#!/bin/bash
# inspect.sh — List open windows or get details about a specific window
# Outputs JSON for easy agent consumption
set -e

# --- Defaults ---
WINDOW_NAME=""
ACTIVE=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --window)
            WINDOW_NAME="$2"
            shift 2
            ;;
        --active)
            ACTIVE=true
            shift
            ;;
        --json)
            # Always JSON, accepted for consistency
            shift
            ;;
        -h|--help)
            echo "Usage: inspect.sh [--window NAME] [--active] [--json]"
            echo ""
            echo "Options:"
            echo "  --window NAME   Get details for a window matching NAME"
            echo "  --active        Get details for the currently focused window"
            echo "  --json          Output as JSON (default)"
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
    echo '{"success": false, "windows": [], "error": "DISPLAY not set. Run: export DISPLAY=:0"}'
    exit 1
fi

# --- Active window mode ---
if $ACTIVE; then
    WIN_ID_DEC=$(xdotool getactivewindow 2>/dev/null || true)
    if [ -z "$WIN_ID_DEC" ]; then
        echo '{"success": false, "windows": [], "error": "No active window found"}'
        exit 1
    fi
    WIN_ID=$(printf "0x%08x" "$WIN_ID_DEC")
    WIN_NAME=$(xdotool getactivewindow getwindowname 2>/dev/null || echo "unknown")
    WIN_CLASS=$(xprop -id "$WIN_ID_DEC" WM_CLASS 2>/dev/null | sed 's/.*= //' | tr -d '"' | cut -d',' -f2 | xargs 2>/dev/null || echo "unknown")
    GEOM=$(xdotool getactivewindow getwindowgeometry --shell 2>/dev/null || true)
    X=$(echo "$GEOM" | grep "^X=" | cut -d= -f2 || echo "0")
    Y=$(echo "$GEOM" | grep "^Y=" | cut -d= -f2 || echo "0")
    WIDTH=$(echo "$GEOM" | grep "^WIDTH=" | cut -d= -f2 || echo "0")
    HEIGHT=$(echo "$GEOM" | grep "^HEIGHT=" | cut -d= -f2 || echo "0")

    WIN_NAME_ESC=$(echo "$WIN_NAME" | sed 's/\\/\\\\/g; s/"/\\"/g')
    WIN_CLASS_ESC=$(echo "$WIN_CLASS" | sed 's/\\/\\\\/g; s/"/\\"/g')

    cat <<ENDJSON
{
  "success": true,
  "windows": [{
    "id": "$WIN_ID",
    "name": "$WIN_NAME_ESC",
    "class": "$WIN_CLASS_ESC",
    "x": ${X:-0},
    "y": ${Y:-0},
    "width": ${WIDTH:-0},
    "height": ${HEIGHT:-0}
  }],
  "error": null
}
ENDJSON
    exit 0
fi

# --- List windows using wmctrl ---
if ! command -v wmctrl &>/dev/null; then
    echo '{"success": false, "windows": [], "error": "wmctrl not installed. Run: bash install.sh"}'
    exit 1
fi

# Build window list into an array, then output as JSON
ENTRIES=()

while IFS= read -r line; do
    [ -z "$line" ] && continue

    WIN_ID=$(echo "$line" | awk '{print $1}')
    DESKTOP=$(echo "$line" | awk '{print $2}')
    X=$(echo "$line" | awk '{print $3}')
    Y=$(echo "$line" | awk '{print $4}')
    WIDTH=$(echo "$line" | awk '{print $5}')
    HEIGHT=$(echo "$line" | awk '{print $6}')
    # Window name is everything after the 7th field
    WIN_NAME=$(echo "$line" | awk '{for(i=8;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')

    # Get window class via xprop
    WIN_CLASS=$(xprop -id "$WIN_ID" WM_CLASS 2>/dev/null | sed 's/.*= //' | tr -d '"' | cut -d',' -f2 | xargs 2>/dev/null || echo "unknown")

    # Filter by window name if specified
    if [ -n "$WINDOW_NAME" ]; then
        if ! echo "$WIN_NAME" | grep -qi "$WINDOW_NAME"; then
            continue
        fi
    fi

    WIN_NAME_ESC=$(echo "$WIN_NAME" | sed 's/\\/\\\\/g; s/"/\\"/g')
    WIN_CLASS_ESC=$(echo "$WIN_CLASS" | sed 's/\\/\\\\/g; s/"/\\"/g')

    ENTRY=$(cat <<ENDENTRY
    {
      "id": "$WIN_ID",
      "name": "$WIN_NAME_ESC",
      "class": "$WIN_CLASS_ESC",
      "x": $X,
      "y": $Y,
      "width": $WIDTH,
      "height": $HEIGHT,
      "desktop": $DESKTOP
    }
ENDENTRY
)
    ENTRIES+=("$ENTRY")
done < <(wmctrl -lG 2>/dev/null)

# Output JSON
echo "{"
echo "  \"success\": true,"
echo "  \"windows\": ["

for i in "${!ENTRIES[@]}"; do
    if [ "$i" -gt 0 ]; then
        echo "    ,"
    fi
    echo "${ENTRIES[$i]}"
done

echo "  ],"
echo "  \"error\": null"
echo "}"
