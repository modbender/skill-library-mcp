#!/bin/bash
# YaCy Search Script (RSS/XML API)
# Usage: yacy_search "query" [count]

YACY_DIR="${OPENCLAWSKILL_CONFIG_yacy_dir:-/home/q/.openclaw/workspace/yacy_search_server}"
PORT="${OPENCLAWSKILL_CONFIG_port:-8090}"

QUERY="$1"
COUNT="${2:-10}"

if [ -z "$QUERY" ]; then
  echo "Usage: yacy_search \"search query\" [count]"
  echo "Example: yacy_search \"open source search engine\" 5"
  exit 1
fi

# Check if YaCy is running
if ! pgrep -f "yacy" > /dev/null; then
  echo "Error: YaCy is not running. Start it with: yacy_start"
  exit 1
fi

# URL encode the query (Python method)
ENCODED_QUERY=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY" 2>/dev/null || printf '%s' "$QUERY")

# Use yacysearch.rss endpoint with maximumRecords
API_URL="http://localhost:$PORT/yacysearch.rss?query=$ENCODED_QUERY&maximumRecords=$COUNT"

echo "Searching YaCy for: $QUERY"
echo "---"

# Fetch the RSS feed and parse with Python for nice output
python3 - "$API_URL" "$COUNT" <<'PYEOF'
import sys, urllib.request, re, html
try:
    url = sys.argv[1]
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    data = urllib.request.urlopen(url, timeout=10).read().decode('utf-8', errors='ignore')
    # Extract items: <item> ... </item>
    items = re.findall(r'<item>(.*?)</item>', data, re.DOTALL | re.IGNORECASE)
    total = len(items)
    print(f"Total results: {total}\n")
    for i, item in enumerate(items[:max_count]):
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
        title = html.unescape(title_match.group(1).strip()) if title_match else "No title"
        # Extract link
        link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
        link = link_match.group(1).strip() if link_match else ""
        # Extract description/summary
        desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL | re.IGNORECASE)
        desc = html.unescape(desc_match.group(1).strip()) if desc_match else ""
        # Clean up description: remove CDATA and HTML tags
        desc = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', desc, flags=re.DOTALL)
        desc = re.sub(r'<[^>]+>', '', desc)
        desc = desc.replace('\n', ' ').strip()
        if desc and len(desc) > 200:
            desc = desc[:200] + "..."
        # Print result
        print(f"{i+1}. {title}")
        if link:
            print(f"   {link}")
        if desc:
            print(f"   {desc}")
        print()
except Exception as e:
    print(f"Error during search: {e}")
    sys.exit(1)
PYEOF

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo "Search failed. Check that YaCy is running and the API is accessible."
  exit $EXIT_CODE
fi
