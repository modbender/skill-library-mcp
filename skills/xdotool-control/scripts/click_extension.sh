#!/bin/bash
# click_extension.sh — Focus Chrome and click a named extension icon
# Usage: click_extension.sh "OpenClaw"  OR  click_extension.sh "Dawn"
#
# Strategy:
# 1. Find Chrome window
# 2. Focus it
# 3. Take toolbar screenshot
# 4. Click puzzle piece (unpinned menu) or scan pinned icon positions

EXT_NAME="${1:-OpenClaw}"
SNAP="/tmp/xdotool_toolbar_$(date +%s).png"

# Dependency checks
if ! command -v xdotool &>/dev/null; then
  echo "ERROR: xdotool not installed. Run: sudo apt-get install xdotool" >&2
  exit 1
fi
if ! command -v scrot &>/dev/null; then
  echo "ERROR: scrot not installed. Run: sudo apt-get install scrot" >&2
  exit 1
fi
# ImageMagick optional but useful for template matching
HAS_CONVERT=$(command -v convert &>/dev/null && echo "1" || echo "0")

# Find the tallest Chrome window (the main one with extensions, not VNC viewer)
# Taller window = more content = primary browser
WIN=""
MAX_H=0
while read w; do
  H=$(xdotool getwindowgeometry "$w" 2>/dev/null | awk '/Geometry/{split($2,a,"x"); print a[2]}')
  if [ -n "$H" ] && [ "$H" -gt "$MAX_H" ] 2>/dev/null; then
    MAX_H="$H"
    WIN="$w"
  fi
done < <(xdotool search --name "Google Chrome" 2>/dev/null)

# Fallback: take first if above fails
if [ -z "$WIN" ]; then
  WIN=$(xdotool search --name "Google Chrome" 2>/dev/null | head -1)
fi

if [ -z "$WIN" ]; then
  echo "ERROR: Chrome window not found" >&2
  exit 1
fi

echo "Using Chrome window: $WIN"

xdotool windowactivate --sync "$WIN"
sleep 0.4

# Auto-detect screen geometry
read SCREEN_W SCREEN_H <<< $(xdotool getdisplaygeometry)

# Derive toolbar Y from Chrome window position (not screen-global hardcode)
WIN_GEOM=$(xdotool getwindowgeometry "$WIN" 2>/dev/null)
# Position format: "  Position: 1066,51 (screen: 0)" → X=1066, Y=51
WIN_POS=$(echo "$WIN_GEOM" | grep "Position:" | grep -oP '\d+,\d+' | head -1)
WIN_X=$(echo "$WIN_POS" | cut -d, -f1)  # horizontal offset from left
WIN_Y=$(echo "$WIN_POS" | cut -d, -f2)  # vertical offset from top
WIN_W=$(echo "$WIN_GEOM" | awk '/Geometry/{split($2,a,"x"); print a[1]}')
# Chrome toolbar (address bar + extensions) is ~90px below window top
TOOLBAR_Y=$(( ${WIN_Y:-0} + 90 ))
CHROME_RIGHT=$(( ${WIN_X:-0} + ${WIN_W:-SCREEN_W} ))
echo "Screen: ${SCREEN_W}x${SCREEN_H}, Chrome at x=${WIN_X:-?} y=${WIN_Y:-?}, toolbar Y: $TOOLBAR_Y, Chrome right: $CHROME_RIGHT"

# Snapshot the toolbar right side for visual inspection
scrot -a "$((SCREEN_W-350)),0,350,72" "$SNAP" 2>/dev/null
echo "Toolbar snapshot: $SNAP"
echo "Read it with Claude to identify icon positions visually."
echo ""

# Attempt to click common extension icon positions (right to left)
# Most setups have pinned extensions starting ~150px from right edge
# Try: puzzle piece first (reveals unpinned list), then pinned positions

echo "Attempting click at puzzle-piece area (unpinned extensions)..."
xdotool mousemove "$((CHROME_RIGHT - 90))" $TOOLBAR_Y click 1
sleep 0.6

# Take another snap to see if extension list opened
scrot -a "$((SCREEN_W-400)),50,400,400" "/tmp/xdotool_extlist.png" 2>/dev/null
echo "Extension list snapshot: /tmp/xdotool_extlist.png"
echo "If the extension list opened, run:"
echo "  xdotool mousemove X Y click 1"
echo "where X,Y is the position of '$EXT_NAME' in the list."
