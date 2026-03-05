#!/bin/bash
# gumroad-stats.sh — Quick stats summary

set -e

CREDS_FILE="${HOME}/.config/gumroad/credentials.json"

if [[ ! -f "$CREDS_FILE" ]]; then
  echo "Error: Credentials not found at $CREDS_FILE"
  echo "Create with: {\"access_token\": \"YOUR_TOKEN\"}"
  exit 1
fi

TOKEN=$(grep -o '"access_token"[[:space:]]*:[[:space:]]*"[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)

if [[ -z "$TOKEN" ]]; then
  echo "Error: Could not read access_token from $CREDS_FILE"
  exit 1
fi

echo "=== Gumroad Stats ==="
echo ""

# Fetch products
PRODUCTS=$(curl -s "https://api.gumroad.com/v2/products" \
  -H "Authorization: Bearer $TOKEN")

if echo "$PRODUCTS" | grep -q '"success":false'; then
  echo "Error: API request failed"
  echo "$PRODUCTS"
  exit 1
fi

# Parse with basic tools (no jq dependency)
TOTAL=$(echo "$PRODUCTS" | grep -o '"id":"[^"]*"' | wc -l | tr -d ' ')
PUBLISHED=$(echo "$PRODUCTS" | grep -o '"published":true' | wc -l | tr -d ' ')

echo "Products: $TOTAL total, $PUBLISHED published"
echo ""

# Extract top products by sales (simple approach)
echo "Top Products by Sales:"
# Use Python if available for reliable JSON parsing
if command -v python3 &>/dev/null; then
  echo "$PRODUCTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
products = sorted(data.get('products', []), key=lambda x: x.get('sales_count', 0), reverse=True)
for p in products[:10]:
    sales = p.get('sales_count', 0)
    if sales > 0:
        rev = p.get('sales_usd_cents', 0) / 100
        print(f\"  - {p['name']}: {sales} sales, \${rev:.2f}\")
"
else
  echo "  (Install python3 for detailed breakdown)"
  echo "  Total published products: $PUBLISHED"
fi

echo ""
echo "Run ./gumroad-daily.sh to log metrics"
