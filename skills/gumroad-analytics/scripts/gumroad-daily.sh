#!/bin/bash
# gumroad-daily.sh — Pull daily stats and log to memory

set -e

CREDS_FILE="${HOME}/.config/gumroad/credentials.json"
METRICS_DIR="${METRICS_DIR:-memory/metrics/gumroad}"
DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="$METRICS_DIR/$DATE.json"

if [[ ! -f "$CREDS_FILE" ]]; then
  echo "Error: Credentials not found at $CREDS_FILE"
  exit 1
fi

TOKEN=$(grep -o '"access_token"[[:space:]]*:[[:space:]]*"[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)

mkdir -p "$METRICS_DIR"

echo "Fetching Gumroad data for $DATE..."

# Fetch products
PRODUCTS=$(curl -s "https://api.gumroad.com/v2/products" \
  -H "Authorization: Bearer $TOKEN")

if echo "$PRODUCTS" | grep -q '"success":false'; then
  echo "Error: API request failed"
  exit 1
fi

# Fetch recent sales (last 30 days)
AFTER_DATE=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d "30 days ago" +%Y-%m-%d)
SALES=$(curl -s "https://api.gumroad.com/v2/sales?after=$AFTER_DATE" \
  -H "Authorization: Bearer $TOKEN")

# Count totals
TOTAL_PRODUCTS=$(echo "$PRODUCTS" | grep -o '"id":"[^"]*"' | wc -l | tr -d ' ')
PUBLISHED=$(echo "$PRODUCTS" | grep -o '"published":true' | wc -l | tr -d ' ')
RECENT_SALES=$(echo "$SALES" | grep -o '"id":"[^"]*"' | wc -l | tr -d ' ')

# Build JSON output (simple format for compatibility)
cat > "$OUTPUT_FILE" << EOF
{
  "date": "$DATE",
  "snapshot_time": "$(date +%H:%M)",
  "products_count": $TOTAL_PRODUCTS,
  "published_count": $PUBLISHED,
  "recent_sales_30d": $RECENT_SALES,
  "raw_products": $PRODUCTS,
  "raw_sales": $SALES
}
EOF

echo "✓ Logged to $OUTPUT_FILE"
echo "  Products: $TOTAL_PRODUCTS ($PUBLISHED published)"
echo "  Sales (30d): $RECENT_SALES"

# Compare to yesterday if exists
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
YESTERDAY_FILE="$METRICS_DIR/$YESTERDAY.json"

if [[ -f "$YESTERDAY_FILE" ]]; then
  YESTERDAY_SALES=$(grep -o '"recent_sales_30d":[0-9]*' "$YESTERDAY_FILE" | cut -d':' -f2)
  if [[ -n "$YESTERDAY_SALES" && "$RECENT_SALES" -gt "$YESTERDAY_SALES" ]]; then
    DIFF=$((RECENT_SALES - YESTERDAY_SALES))
    echo "  📈 +$DIFF new sales since yesterday!"
  fi
fi
