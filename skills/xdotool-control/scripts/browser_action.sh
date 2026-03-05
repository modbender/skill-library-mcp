#!/bin/bash
# browser_action.sh — Browser independence wrapper for Jim
# Gives Jim full browser control without needing the Chrome CDP relay.
# Usage:
#   browser_action.sh "https://url.com" screenshot
#   browser_action.sh "https://url.com" click 960 540
#   browser_action.sh "https://url.com" type "text to type"
#   browser_action.sh "" screenshot        # screenshot without navigation
#
# Returns: path to screenshot file, or "done" for click/type actions

URL="${1:-}"
ACTION="${2:-screenshot}"
ARG3="${3:-}"
ARG4="${4:-}"

# Dependency checks
for dep in xdotool scrot; do
  if ! command -v "$dep" &>/dev/null; then
    echo "ERROR: $dep not installed. Run: sudo apt-get install $dep" >&2
    exit 1
  fi
done

SNAP_FILE="/tmp/browser_action_$(date +%s).png"

# Find Chrome
WIN=$(xdotool search --name "Google Chrome" 2>/dev/null | head -1)
if [ -z "$WIN" ]; then
  echo "ERROR: Chrome not running. Start Chrome first." >&2
  exit 1
fi

# Focus Chrome
xdotool windowactivate --sync "$WIN"
sleep 0.3

# Navigate to URL if provided
if [ -n "$URL" ]; then
  xdotool key ctrl+t
  sleep 0.5
  xdotool key ctrl+l
  sleep 0.3
  xdotool type --clearmodifiers "$URL"
  xdotool key Return
  sleep 3
fi

case "$ACTION" in
  screenshot)
    scrot "$SNAP_FILE" 2>/dev/null
    echo "$SNAP_FILE"
    ;;

  screenshot_window)
    # Screenshot just the Chrome window area
    WIN_GEOM=$(xdotool getwindowgeometry "$WIN" 2>/dev/null)
    WIN_X=$(echo "$WIN_GEOM" | grep Position | awk -F'[,: ]' '{print $4}')
    WIN_Y=$(echo "$WIN_GEOM" | grep Position | awk -F'[,: ]' '{print $5}')
    WIN_W=$(echo "$WIN_GEOM" | grep Geometry | awk -F'x' '{print $1}' | awk '{print $2}')
    WIN_H=$(echo "$WIN_GEOM" | grep Geometry | awk -F'x' '{print $2}')
    scrot -a "${WIN_X},${WIN_Y},${WIN_W},${WIN_H}" "$SNAP_FILE" 2>/dev/null
    echo "$SNAP_FILE"
    ;;

  click)
    X="${ARG3:-960}"
    Y="${ARG4:-540}"
    xdotool mousemove "$X" "$Y" click 1
    sleep 0.5
    scrot "$SNAP_FILE" 2>/dev/null
    echo "clicked $X $Y — screenshot: $SNAP_FILE"
    ;;

  type)
    TEXT="$ARG3"
    if [ -z "$TEXT" ]; then
      echo "ERROR: type action requires text argument" >&2
      exit 1
    fi
    xdotool type --clearmodifiers "$TEXT"
    echo "typed into Chrome"
    ;;

  scroll_down)
    TIMES="${ARG3:-3}"
    for i in $(seq 1 "$TIMES"); do
      xdotool key Page_Down
      sleep 0.2
    done
    scrot "$SNAP_FILE" 2>/dev/null
    echo "scrolled down ${TIMES}x — screenshot: $SNAP_FILE"
    ;;

  back)
    xdotool key Alt+Left
    sleep 1
    scrot "$SNAP_FILE" 2>/dev/null
    echo "navigated back — screenshot: $SNAP_FILE"
    ;;

  new_tab)
    xdotool key ctrl+t
    echo "new tab opened"
    ;;

  close_tab)
    xdotool key ctrl+w
    echo "tab closed"
    ;;

  *)
    echo "ERROR: Unknown action '$ACTION'. Valid: screenshot, screenshot_window, click, type, scroll_down, back, new_tab, close_tab" >&2
    exit 1
    ;;
esac
