#!/bin/bash
# type_in_window.sh — Focus a window and type text into it
# Usage: type_in_window.sh <window_name> <text> [--press-enter]

WINDOW_NAME="${1:-Terminal}"
TEXT="${2:-}"
PRESS_ENTER="${3:-}"

if [ -z "$TEXT" ]; then
  echo "Usage: type_in_window.sh <window_name> <text> [--press-enter]" >&2
  exit 1
fi

WIN=$(xdotool search --name "$WINDOW_NAME" 2>/dev/null | head -1)
if [ -z "$WIN" ]; then
  echo "ERROR: Window '$WINDOW_NAME' not found" >&2
  exit 1
fi

xdotool windowactivate --sync "$WIN"
sleep 0.3
xdotool type --clearmodifiers "$TEXT"

if [ "$PRESS_ENTER" = "--press-enter" ]; then
  sleep 0.1
  xdotool key Return
  echo "Typed and pressed Enter in '$WINDOW_NAME'"
else
  echo "Typed in '$WINDOW_NAME' (no Enter)"
fi
