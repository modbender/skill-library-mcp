#!/bin/bash
# Screenshot wrapper script
# Usage: screenshot <url> [output-path]

SKILL_DIR="$HOME/.openclaw/workspace/skills/openclaw-browser"
SCRIPT="$SKILL_DIR/scripts/screenshot.js"

# Check if URL provided
if [ -z "$1" ]; then
    echo "Usage: screenshot <url> [output-path]"
    echo ""
    echo "Examples:"
    echo "  screenshot https://baidu.com"
    echo "  screenshot https://xiaohongshu.com /tmp/xhs.png"
    exit 1
fi

URL="$1"

# Default output path if not provided
if [ -z "$2" ]; then
    FILENAME=$(echo "$URL" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-50)
    OUTPUT="/tmp/${FILENAME}_$(date +%Y%m%d_%H%M%S).png"
else
    OUTPUT="$2"
fi

# Check if Chrome CDP is running
if ! curl -s http://127.0.0.1:9222/json/version >/devdev/null 2>&1; then
    echo "Error: Chrome CDP not available at http://127.0.0.1:9222"
    echo ""
    echo "Start Chrome with:"
    echo "  ~/chrome-install/opt/google/chrome/chrome \\"
    echo "    --remote-debugging-port=9222 \\"
    echo "    --remote-debugging-address=0.0.0.0 \\"
    echo "    --no-sandbox &"
    exit 1
fi

# Run screenshot
echo "Taking screenshot of $URL..."
node "$SCRIPT" "$URL" "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "Screenshot saved: $OUTPUT"
    ls -lh "$OUTPUT" 2>/dev/null || true
fi
