#!/bin/bash
# LotBot Avatar Kiosk Launcher
# Starts the avatar server and opens Chrome in kiosk mode

AVATAR_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$AVATAR_DIR/kiosk.log"

echo "$(date) — Starting LotBot Avatar Kiosk" >> "$LOG_FILE"

# Start the avatar server in background
cd "$AVATAR_DIR"
npm start >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$(date) — Server started (PID: $SERVER_PID)" >> "$LOG_FILE"

# Wait for server to be ready
for i in {1..30}; do
  if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "$(date) — Server ready" >> "$LOG_FILE"
    break
  fi
  sleep 1
done

# Detect ZenScreen position dynamically
# Look for the 1080-wide display (ZenScreen MB166CR is 1920x1080 in portrait = 1080x1920)
ZENSCREEN_POS=$(osascript -e '
use framework "AppKit"
set screens to current application'\''s NSScreen'\''s screens()
-- Main screen height (for coordinate conversion: NSScreen is bottom-left, Chrome needs top-left)
set mainH to item 2 of item 2 of (item 1 of screens)'\''s frame() as integer
repeat with s in screens
  set f to s'\''s frame()
  set w to item 1 of item 2 of f as integer
  set h to item 2 of item 2 of f as integer
  set nsX to item 1 of item 1 of f as integer
  set nsY to item 2 of item 1 of f as integer
  if w = 1080 and h = 1920 then
    -- Convert: top-left Y = mainHeight - (nsY + screenHeight)
    set tlY to mainH - (nsY + h)
    return (nsX as text) & "," & (tlY as text)
  end if
end repeat
return "0,0"
' 2>/dev/null)

# Default fallback
if [ -z "$ZENSCREEN_POS" ]; then
  ZENSCREEN_POS="0,0"
fi

WIN_X="${ZENSCREEN_POS%,*}"
WIN_Y="${ZENSCREEN_POS#*,}"
echo "$(date) — ZenScreen detected at position: ${WIN_X},${WIN_Y}" >> "$LOG_FILE"

# Open Chrome in kiosk mode
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --kiosk \
  --autoplay-policy=no-user-gesture-required \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --disable-translate \
  --no-first-run \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --user-data-dir="$HOME/.openclaw/browser/lotbot-kiosk" \
  --window-position=${WIN_X},${WIN_Y} \
  --window-size=1080,1920 \
  http://localhost:5173 >> "$LOG_FILE" 2>&1 &

CHROME_PID=$!
echo "$(date) — Chrome kiosk started (PID: $CHROME_PID)" >> "$LOG_FILE"

# Move Chrome window to ZenScreen via AppleScript (backup)
sleep 3
osascript -e "
tell application \"System Events\"
  tell process \"Google Chrome\"
    set position of window 1 to {${WIN_X}, ${WIN_Y}}
    set size of window 1 to {1080, 1920}
  end tell
end tell
" >> "$LOG_FILE" 2>&1
echo "$(date) — Window moved to ZenScreen (${WIN_X},${WIN_Y})" >> "$LOG_FILE"

# Wait for Chrome to exit, then kill server
wait $CHROME_PID
kill $SERVER_PID 2>/dev/null
echo "$(date) — Kiosk stopped" >> "$LOG_FILE"
