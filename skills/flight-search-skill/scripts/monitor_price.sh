#!/bin/bash
# Monitor flight prices and alert when they drop
# Usage: ./monitor_price.sh ORIGIN DEST DEPARTURE_DATE [RETURN_DATE]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SEARCH_SCRIPT="$SCRIPT_DIR/search_flights.sh"
MONITOR_FILE="$SKILL_DIR/.monitored_flights.json"
CONFIG_FILE="$SKILL_DIR/config.json"

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 ORIGIN DEST DEPARTURE_DATE [RETURN_DATE]"
    echo ""
    echo "Example:"
    echo "  $0 CNF BKK 2026-12-15"
    echo "  $0 CNF BKK 2026-12-15 2027-01-10"
    echo ""
    echo "This will:"
    echo "  1. Add flight to monitoring list"
    echo "  2. Store current best price"
    echo "  3. Check periodically for price drops"
    echo "  4. Alert if price drops >5%"
    exit 1
fi

ORIGIN="$1"
DESTINATION="$2"
DEPARTURE="$3"
RETURN="${4:-}"

# Read threshold from config.json (P2 fix: honor configuration)
if [ -f "$CONFIG_FILE" ]; then
    THRESHOLD_PERCENT=$(python3 -c "import json; f=open('$CONFIG_FILE'); config=json.load(f); print(config.get('alerts', {}).get('price_drop_threshold_percent', 5))" 2>/dev/null || echo "5")
else
    THRESHOLD_PERCENT=5
fi

# Create monitor ID
MONITOR_ID="${ORIGIN}-${DESTINATION}-${DEPARTURE}"
[ -n "$RETURN" ] && MONITOR_ID="${MONITOR_ID}-${RETURN}"

# Initialize monitor file if doesn't exist
if [ ! -f "$MONITOR_FILE" ]; then
    echo '{"monitored_flights": []}' > "$MONITOR_FILE"
fi

# Search current prices (SAFE - no eval)
echo "🔍 Checking current prices..." >&2

# P1 fix: Capture ONLY stdout (JSON), let stderr go to terminal
# Do NOT use 2>&1 here - it mixes progress messages into JSON!
# Exit code indicates success/failure
if ! RESULTS=$("$SEARCH_SCRIPT" "$ORIGIN" "$DESTINATION" "$DEPARTURE" ${RETURN:+"$RETURN"}); then
    # Command failed (non-zero exit code)
    # Stderr already shown to user (progress/error messages)
    echo "" >&2
    echo "❌ Failed to search flights" >&2
    echo "   Possible causes:" >&2
    echo "   • Invalid/missing config.json" >&2
    echo "   • API authentication error" >&2
    echo "   • Network connection issue" >&2
    echo "   • Invalid airport codes or dates" >&2
    echo "" >&2
    echo "   Run manually to debug:" >&2
    echo "   $SEARCH_SCRIPT $ORIGIN $DESTINATION $DEPARTURE ${RETURN:-}" >&2
    exit 1
fi

if [ -z "$RESULTS" ] || [ "$RESULTS" = "[]" ]; then
    echo "❌ No flights found for this route/date" >&2
    echo "   Try different dates or check airport codes" >&2
    exit 1
fi

# Extract best price (lowest fare from all results)
# P2 fix: Don't assume data[0] is cheapest - find minimum
BEST_PRICE=$(echo "$RESULTS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(min(data, key=lambda x: x['price'])['price'] if data else 0)")
CURRENCY=$(echo "$RESULTS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(min(data, key=lambda x: x['price'])['currency'] if data else 'BRL')")

if [ -z "$BEST_PRICE" ] || [ "$BEST_PRICE" = "0" ]; then
    echo "❌ Could not extract price" >&2
    exit 1
fi

echo "💰 Current best price: $BEST_PRICE $CURRENCY" >&2

# Add to monitored flights (SAFE - no heredoc injection)
# Pass data via command-line arguments instead of interpolating
python3 - "$MONITOR_FILE" "$MONITOR_ID" "$ORIGIN" "$DESTINATION" "$DEPARTURE" "${RETURN:-}" "$BEST_PRICE" "$CURRENCY" "$THRESHOLD_PERCENT" << 'PYEOF'
import json
import sys
from datetime import datetime

# Read arguments (SAFE - no shell interpolation)
monitor_file = sys.argv[1]
monitor_id = sys.argv[2]
origin = sys.argv[3]
dest = sys.argv[4]
departure = sys.argv[5]
return_date = sys.argv[6] if sys.argv[6] else None
best_price = float(sys.argv[7])
currency = sys.argv[8]
threshold_percent = int(sys.argv[9])

# Load existing data
try:
    with open(monitor_file, 'r') as f:
        data = json.load(f)
except:
    data = {"monitored_flights": []}

# Check if already monitoring
existing = [f for f in data["monitored_flights"] if f["id"] == monitor_id]

if existing:
    # Update existing
    existing[0]["last_price"] = best_price
    existing[0]["last_check"] = datetime.now().isoformat()
    existing[0]["check_count"] = existing[0].get("check_count", 0) + 1
    print(f"✅ Updated monitoring: {monitor_id}", file=sys.stderr)
else:
    # Add new
    data["monitored_flights"].append({
        "id": monitor_id,
        "origin": origin,
        "destination": dest,
        "departure_date": departure,
        "return_date": return_date,
        "initial_price": best_price,
        "last_price": best_price,
        "currency": currency,
        "threshold_percent": threshold_percent,
        "created_at": datetime.now().isoformat(),
        "last_check": datetime.now().isoformat(),
        "check_count": 1,
        "alerts_sent": 0
    })
    print(f"✅ Added to monitoring: {monitor_id}", file=sys.stderr)

# Save
with open(monitor_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"📊 Monitoring {len(data['monitored_flights'])} flights total", file=sys.stderr)
PYEOF

echo "" >&2
echo "🔔 Monitoring active!" >&2
echo "   • Check HEARTBEAT.md for periodic checks" >&2
echo "   • Alert threshold: $THRESHOLD_PERCENT% price drop" >&2
echo "   • View all: cat $MONITOR_FILE" >&2
