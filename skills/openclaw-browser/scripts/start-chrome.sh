#!/bin/bash
# Start Chrome with CDP enabled for browser automation

CHROME_DIR="$HOME/chrome-install/opt/google/chrome"
USER_DATA_DIR="$HOME/.config/google-chrome-cdp"
CDP_PORT=9222

# Check if Chrome is already running with CDP
if curl -s http://127.0.0.1:$CDP_PORT/json/version >/dev/null 2>&1; then
    echo "Chrome with CDP is already running on port $CDP_PORT"
    curl -s http://127.0.0.1:$CDP_PORT/json/version | grep -E '"Browser"|"Protocol-Version"'
    exit 0
fi

# Ensure Chrome is installed
if [ ! -f "$CHROME_DIR/chrome" ]; then
    echo "Error: Chrome not found at $CHROME_DIR/chrome"
    echo "Please install Chrome first"
    exit 1
fi

# Create user data directory
mkdir -p "$USER_DATA_DIR"

echo "Starting Chrome with CDP on port $CDP_PORT..."
cd "$CHROME_DIR"

# Start Chrome with CDP
./chrome \
    --password-store=basic \
    --no-sandbox \
    --ignore-gpu-blocklist \
    --user-data-dir="$USER_DATA_DIR" \
    --no-first-run \
    --disable-search-engine-choice-screen \
    --simulate-outdated-no-au="Tue, 31 Dec 2099 23:59:59 GMT" \
    --default-search-provider-name="Baidu" \
    --default-search-provider-keyword="baidu.com" \
    --default-search-provider-search-url="https://www.baidu.com/s?wd={searchTerms}" \
    --restore-last-session=0 \
    --lang=zh-CN \
    --start-maximized \
    --remote-debugging-port=$CDP_PORT \
    --remote-debugging-address=0.0.0.0 \
    > /tmp/chrome-cdp.log 2>&1 &

CHROME_PID=$!
echo "Chrome started with PID: $CHROME_PID"

# Wait for CDP to be ready
echo -n "Waiting for CDP to be ready"
for i in {1..30}; do
    sleep 1
    if curl -s http://127.0.0.1:$CDP_PORT/json/version >/dev/null 2>&1; then
        echo ""
        echo "CDP is ready!"
        echo ""
        echo "Chrome DevTools Protocol:"
        curl -s http://127.0.0.1:$CDP_PORT/json/version | grep -E '"Browser"|"Protocol-Version"|"webSocketDebuggerUrl"'
        echo ""
        echo "Usage:"
        echo "  screenshot <url>        # Take screenshot"
        echo "  curl http://127.0.0.1:$CDP_PORT/json/version    # Check status"
        exit 0
    fi
    echo -n "."
done

echo ""
echo "Error: Chrome CDP failed to start"
echo "Check log: tail -f /tmp/chrome-cdp.log"
exit 1
