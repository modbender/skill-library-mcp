#!/bin/bash
# find_and_click.sh — Scan a range of coordinates, snapshot, let Claude identify the target
# Usage: find_and_click.sh <window_name> <scan_region_description> <x_start> <x_end> <y> <step>
#
# Takes a strip screenshot of the scan region so Claude can visually identify
# the correct click target, then clicks it.

WINDOW_NAME="${1:-Google Chrome}"
LABEL="${2:-scan}"
Y="${5:-56}"
STEP="${6:-16}"

# Dependency checks
for dep in xdotool scrot; do
  if ! command -v "$dep" &>/dev/null; then
    echo "ERROR: $dep not installed. Run: sudo apt-get install $dep" >&2
    exit 1
  fi
done
if ! command -v convert &>/dev/null; then
  echo "NOTE: ImageMagick not installed — template matching unavailable. Install: sudo apt-get install imagemagick" >&2
fi

SNAP="/tmp/xdotool_${LABEL}_strip.png"

WIN=$(xdotool search --name "$WINDOW_NAME" 2>/dev/null | head -1)
if [ -z "$WIN" ]; then
  echo "ERROR: Window '$WINDOW_NAME' not found" >&2
  exit 1
fi

# Auto-detect screen width if not provided
read SCREEN_W SCREEN_H <<< $(xdotool getdisplaygeometry)
X_START="${3:-$((SCREEN_W - 320))}"
X_END="${4:-$SCREEN_W}"

xdotool windowactivate --sync "$WIN"
sleep 0.3

# Screenshot the strip
WIDTH=$((X_END - X_START))
scrot -a "$X_START,$((Y - 20)),$WIDTH,40" "$SNAP" 2>/dev/null
echo "Strip snapshot saved: $SNAP"
echo "Region: x=$X_START-$X_END, y=$((Y-20))-$((Y+20))"
echo ""
echo "Read $SNAP to identify target coordinates, then:"
echo "  xdotool mousemove <x> <y> click 1"
echo ""

# List candidate positions for reference
echo "Candidate X positions (step=$STEP):"
for ((x=X_START; x<=X_END; x+=STEP)); do
  echo "  x=$x y=$Y"
done
