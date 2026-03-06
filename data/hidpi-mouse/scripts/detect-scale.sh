#!/bin/bash
# Detect HiDPI scale factor for xdotool coordinate conversion
# Works across different screen resolutions and DPI settings
#
# The scale factor converts Claude's displayed image coordinates to xdotool screen coordinates
# Formula: xdotool_coord = claude_display_coord × scale_factor

set -e

DISPLAY="${DISPLAY:-:1}"
export DISPLAY
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

CACHE_FILE="/tmp/hidpi_scale_cache"
CONFIG_FILE="$HOME/.config/hidpi-mouse/scale.conf"

# Check for user-configured scale (highest priority)
if [[ -f "$CONFIG_FILE" ]]; then
    SCALE=$(cat "$CONFIG_FILE" | grep -E '^[0-9]+\.?[0-9]*$' | head -1)
    if [[ -n "$SCALE" ]]; then
        echo "$SCALE"
        exit 0
    fi
fi

# Check cache (valid for 1 hour)
if [[ -f "$CACHE_FILE" ]]; then
    CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)))
    if [[ $CACHE_AGE -lt 3600 ]]; then
        cat "$CACHE_FILE"
        exit 0
    fi
fi

# Get screen resolution
SCREEN_RES=$(xdpyinfo 2>/dev/null | grep dimensions | awk '{print $2}')
if [[ -z "$SCREEN_RES" ]]; then
    SCREEN_RES=$(xrandr 2>/dev/null | grep -E '\*' | head -1 | awk '{print $1}')
fi

if [[ -z "$SCREEN_RES" ]]; then
    echo "2.0"  # Safe default
    exit 0
fi

SCREEN_W=$(echo "$SCREEN_RES" | cut -d'x' -f1)
SCREEN_H=$(echo "$SCREEN_RES" | cut -d'x' -f2)

# Get DPI setting
XFT_DPI=$(xrdb -query 2>/dev/null | grep -i "Xft.dpi" | awk '{print $2}' | head -1)
XFT_DPI=${XFT_DPI:-96}

# Calculate scale factor
# Claude typically displays images with max width around 2000px (for normal DPI)
# But the actual display size varies based on screen DPI and resolution

# Base calculation: how much Claude shrinks the image
# Claude's max display width depends on the viewport
if [[ "$SCREEN_W" -ge 3000 ]]; then
    # 4K/HiDPI screens (like 3024x1772)
    # Claude displays at roughly 1454px width in these cases
    CLAUDE_DISPLAY_W=1454
elif [[ "$SCREEN_W" -ge 2500 ]]; then
    # 2.5K screens
    CLAUDE_DISPLAY_W=1600
elif [[ "$SCREEN_W" -ge 1920 ]]; then
    # Full HD screens
    CLAUDE_DISPLAY_W=1800
else
    # Smaller screens
    CLAUDE_DISPLAY_W=1600
fi

# Additional DPI factor for HiDPI displays
DPI_FACTOR=1.0
if [[ "$XFT_DPI" -ge 192 ]]; then
    # 2x HiDPI (like macOS Retina)
    DPI_FACTOR=1.0  # Already accounted for in CLAUDE_DISPLAY_W
elif [[ "$XFT_DPI" -ge 144 ]]; then
    # 1.5x scaling
    DPI_FACTOR=1.0
fi

# Calculate final scale
SCALE=$(echo "scale=2; $SCREEN_W / $CLAUDE_DISPLAY_W * $DPI_FACTOR" | bc)

# Ensure reasonable bounds (1.0 to 4.0)
SCALE_INT=$(echo "$SCALE" | cut -d'.' -f1)
if [[ "$SCALE_INT" -lt 1 ]]; then
    SCALE="1.0"
elif [[ "$SCALE_INT" -gt 4 ]]; then
    SCALE="4.0"
fi

# Cache result
mkdir -p "$(dirname "$CACHE_FILE")" 2>/dev/null || true
echo "$SCALE" > "$CACHE_FILE"

echo "$SCALE"
