#!/bin/bash
# 🧠 Mood setter — called by the morning cron, outputs today's mood context
# Gathers weather + news signals and picks a weighted random mood

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load config for location
LOCATION="London"
if [ -f "$SCRIPT_DIR/config.json" ]; then
    LOCATION=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('integrations',{}).get('weather',{}).get('location','London').split(',')[0])" 2>/dev/null || echo "London")
fi

echo "=== WEATHER ==="
# NETWORK: wttr.in weather API - public, no auth, read-only GET request
curl -s "wttr.in/${LOCATION}?format=%c+%t+%h+%w" 2>/dev/null || echo "weather unavailable"
echo ""
# NETWORK: wttr.in weather API - public, no auth, read-only GET request  
curl -s "wttr.in/${LOCATION}?format=3" 2>/dev/null || echo ""

echo ""
echo "=== WEATHER DETAIL ==="
# NETWORK: wttr.in weather API - public, no auth, read-only GET request
curl -s "wttr.in/${LOCATION}?0T" 2>/dev/null | head -15 || echo "unavailable"

echo ""
echo "=== GLOBAL NEWS ==="
# NETWORK: BBC RSS feed - public, no auth, read-only GET request
curl -s "https://feeds.bbci.co.uk/news/world/rss.xml" 2>/dev/null | grep -oP '(?<=<title>).*?(?=</title>)' | head -8 || echo "unavailable"

echo ""
echo "=== TECH/AI NEWS ==="
# NETWORK: Hacker News RSS feed - public, no auth, read-only GET request
curl -s "https://hnrss.org/frontpage" 2>/dev/null | grep -oP '(?<=<title>).*?(?=</title>)' | head -8 || echo "unavailable"

echo ""
echo "=== CURRENT MOOD FILE ==="
cat "$SCRIPT_DIR/today_mood.json" 2>/dev/null || echo "no mood set yet"
