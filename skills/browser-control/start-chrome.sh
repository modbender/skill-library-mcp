#!/bin/bash
# Start Chrome with remote debugging on Mac
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROMIUM_PATH="/Applications/Chromium.app/Contents/MacOS/Chromium"

if [ -f "$CHROME_PATH" ]; then
    "$CHROME_PATH" --remote-debugging-port=9222 &
elif [ -f "$CHROMIUM_PATH" ]; then
    "$CHROMIUM_PATH" --remote-debugging-port=9222 &
else
    echo "❌ Chrome/Chromium not found. Please install Google Chrome."
    exit 1
fi
echo "✅ Chrome started with remote debugging on port 9222"
