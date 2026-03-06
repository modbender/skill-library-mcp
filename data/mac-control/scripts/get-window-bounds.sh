#!/bin/bash
# Get window bounds for an application
# Usage: get-window-bounds.sh [AppName]
# If no app specified, gets frontmost window

APP_NAME="${1:-}"

if [ -z "$APP_NAME" ]; then
    # Get frontmost application's window
    osascript -e '
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set appName to name of frontApp
        tell frontApp
            set win to front window
            set {x, y} to position of win
            set {w, h} to size of win
        end tell
    end tell
    return "app:" & appName & " x:" & x & " y:" & y & " width:" & w & " height:" & h
    '
else
    # Get specific app's window
    osascript -e "
    tell application \"System Events\"
        tell process \"$APP_NAME\"
            set win to front window
            set {x, y} to position of win
            set {w, h} to size of win
        end tell
    end tell
    return \"x:\" & x & \" y:\" & y & \" width:\" & w & \" height:\" & h
    "
fi
