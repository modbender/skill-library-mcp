#!/bin/bash
# Calibration script for hidpi-mouse skill
# Creates a calibration image and helps calculate the exact scale factor
#
# Usage: calibrate.sh [test|set <scale>|reset]

set -e

DISPLAY="${DISPLAY:-:1}"
export DISPLAY
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

CONFIG_DIR="$HOME/.config/hidpi-mouse"
CONFIG_FILE="$CONFIG_DIR/scale.conf"
CACHE_FILE="/tmp/hidpi_scale_cache"

show_help() {
    cat << 'EOF'
HiDPI Mouse Calibration Tool

USAGE:
    calibrate.sh              # Run interactive calibration
    calibrate.sh test         # Test current scale with a click
    calibrate.sh set <scale>  # Manually set scale factor (e.g., 2.08)
    calibrate.sh reset        # Reset to auto-detection
    calibrate.sh info         # Show current configuration

CALIBRATION PROCESS:
    1. Run this script (no arguments)
    2. It creates a calibration image with markers
    3. Look at the image in Claude and note the marker positions
    4. Enter the displayed coordinates when prompted
    5. Scale factor is calculated and saved

EOF
}

show_info() {
    echo "=== HiDPI Mouse Configuration ==="
    echo ""
    
    # Screen info
    SCREEN_RES=$(xdpyinfo 2>/dev/null | grep dimensions | awk '{print $2}')
    XFT_DPI=$(xrdb -query 2>/dev/null | grep -i "Xft.dpi" | awk '{print $2}')
    echo "Screen Resolution: $SCREEN_RES"
    echo "Xft.dpi: ${XFT_DPI:-96}"
    echo ""
    
    # Scale info
    if [[ -f "$CONFIG_FILE" ]]; then
        echo "Configured Scale: $(cat "$CONFIG_FILE") (from $CONFIG_FILE)"
    elif [[ -f "$CACHE_FILE" ]]; then
        echo "Cached Scale: $(cat "$CACHE_FILE") (auto-detected)"
    else
        echo "Scale: Not yet determined (will auto-detect)"
    fi
    echo ""
    
    # Test calculation
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    CURRENT_SCALE=$("$SCRIPT_DIR/detect-scale.sh")
    echo "Current Scale Factor: $CURRENT_SCALE"
    echo ""
    echo "Example: Display coord (500, 300) → xdotool ($((500 * ${CURRENT_SCALE%.*})), $((300 * ${CURRENT_SCALE%.*})))"
}

run_test() {
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    SCALE=$("$SCRIPT_DIR/detect-scale.sh")
    
    echo "Current scale: $SCALE"
    echo ""
    echo "Testing: Will click at screen center in 3 seconds..."
    echo "Watch where the click lands!"
    sleep 3
    
    # Get screen center
    SCREEN_RES=$(xdpyinfo | grep dimensions | awk '{print $2}')
    SCREEN_W=$(echo "$SCREEN_RES" | cut -d'x' -f1)
    SCREEN_H=$(echo "$SCREEN_RES" | cut -d'x' -f2)
    
    CENTER_X=$((SCREEN_W / 2))
    CENTER_Y=$((SCREEN_H / 2))
    
    echo "Clicking at screen center: ($CENTER_X, $CENTER_Y)"
    xdotool mousemove "$CENTER_X" "$CENTER_Y" click 1
    
    echo ""
    echo "If the click was off-target, run: calibrate.sh"
}

set_scale() {
    local SCALE="$1"
    
    # Validate
    if ! echo "$SCALE" | grep -qE '^[0-9]+\.?[0-9]*$'; then
        echo "Error: Invalid scale factor '$SCALE'"
        echo "Example: calibrate.sh set 2.08"
        exit 1
    fi
    
    mkdir -p "$CONFIG_DIR"
    echo "$SCALE" > "$CONFIG_FILE"
    rm -f "$CACHE_FILE"
    
    echo "Scale factor set to: $SCALE"
    echo "Saved to: $CONFIG_FILE"
}

reset_scale() {
    rm -f "$CONFIG_FILE" "$CACHE_FILE"
    echo "Scale configuration reset. Will use auto-detection."
}

run_calibration() {
    echo "=== HiDPI Mouse Calibration ==="
    echo ""
    
    # Create calibration image
    CAL_IMG="/tmp/hidpi_calibration.png"
    
    # Get screen resolution
    SCREEN_RES=$(xdpyinfo | grep dimensions | awk '{print $2}')
    SCREEN_W=$(echo "$SCREEN_RES" | cut -d'x' -f1)
    SCREEN_H=$(echo "$SCREEN_RES" | cut -d'x' -f2)
    
    echo "Screen Resolution: ${SCREEN_W}x${SCREEN_H}"
    echo ""
    
    # Create calibration image with markers at known positions
    # Markers at: (100,100), (500,500), (SCREEN_W-100, SCREEN_H-100)
    
    python3 << PYTHON
from PIL import Image, ImageDraw, ImageFont

w, h = $SCREEN_W, $SCREEN_H
img = Image.new('RGB', (w, h), 'white')
draw = ImageDraw.Draw(img)

# Draw grid
for x in range(0, w, 100):
    color = 'red' if x % 500 == 0 else 'lightgray'
    draw.line([(x, 0), (x, h)], fill=color, width=1)
for y in range(0, h, 100):
    color = 'red' if y % 500 == 0 else 'lightgray'
    draw.line([(0, y), (w, y)], fill=color, width=1)

# Draw markers with labels
markers = [
    (100, 100, 'A'),
    (500, 500, 'B'),
    (1000, 500, 'C'),
    (w//2, h//2, 'CENTER'),
]

for x, y, label in markers:
    # Draw crosshair
    draw.line([(x-20, y), (x+20, y)], fill='blue', width=3)
    draw.line([(x, y-20), (x, y+20)], fill='blue', width=3)
    draw.ellipse([(x-10, y-10), (x+10, y+10)], outline='blue', width=2)
    # Label
    draw.text((x+15, y-25), f'{label}\n({x},{y})', fill='blue')

# Title
draw.text((50, 30), f'Calibration Image - Screen: {w}x{h}', fill='black')
draw.text((50, 60), 'Find marker B (500,500) in Claude display, note its coordinates', fill='darkgreen')

img.save('$CAL_IMG')
print('Calibration image created: $CAL_IMG')
PYTHON

    echo ""
    echo "Calibration image saved to: $CAL_IMG"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Open $CAL_IMG in an image viewer or send to Claude"
    echo "2. Look at marker B which is at screen position (500, 500)"
    echo "3. Note where marker B appears in the DISPLAYED image coordinates"
    echo ""
    read -p "Where does marker B (500,500) appear in Claude's display? X coordinate: " DISPLAY_X
    read -p "Y coordinate: " DISPLAY_Y
    
    if [[ -z "$DISPLAY_X" || -z "$DISPLAY_Y" ]]; then
        echo "Calibration cancelled."
        exit 1
    fi
    
    # Calculate scale
    SCALE_X=$(echo "scale=3; 500 / $DISPLAY_X" | bc)
    SCALE_Y=$(echo "scale=3; 500 / $DISPLAY_Y" | bc)
    SCALE_AVG=$(echo "scale=2; ($SCALE_X + $SCALE_Y) / 2" | bc)
    
    echo ""
    echo "=== Calibration Results ==="
    echo "Scale X: $SCALE_X"
    echo "Scale Y: $SCALE_Y"
    echo "Average Scale: $SCALE_AVG"
    echo ""
    
    read -p "Save scale factor $SCALE_AVG? [Y/n] " CONFIRM
    if [[ "$CONFIRM" != "n" && "$CONFIRM" != "N" ]]; then
        set_scale "$SCALE_AVG"
    else
        echo "Not saved. To manually set: calibrate.sh set $SCALE_AVG"
    fi
}

# Main
case "${1:-}" in
    help|--help|-h)
        show_help
        ;;
    info)
        show_info
        ;;
    test)
        run_test
        ;;
    set)
        if [[ -z "$2" ]]; then
            echo "Error: Missing scale value"
            echo "Usage: calibrate.sh set <scale>"
            exit 1
        fi
        set_scale "$2"
        ;;
    reset)
        reset_scale
        ;;
    *)
        run_calibration
        ;;
esac
