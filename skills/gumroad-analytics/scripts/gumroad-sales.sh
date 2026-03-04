#!/bin/bash
# gumroad-sales.sh — Export sales data with filters

set -e

CREDS_FILE="${HOME}/.config/gumroad/credentials.json"
AFTER=""
PRODUCT=""
FORMAT="table"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --after) AFTER="$2"; shift 2 ;;
    --product) PRODUCT="$2"; shift 2 ;;
    --json) FORMAT="json"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

TOKEN=$(grep -o '"access_token"[[:space:]]*:[[:space:]]*"[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)

# Build URL
URL="https://api.gumroad.com/v2/sales"
PARAMS=""
[[ -n "$AFTER" ]] && PARAMS="${PARAMS}&after=$AFTER"
[[ -n "$PRODUCT" ]] && PARAMS="${PARAMS}&product_id=$PRODUCT"
[[ -n "$PARAMS" ]] && URL="${URL}?${PARAMS:1}"

SALES=$(curl -s "$URL" -H "Authorization: Bearer $TOKEN")

if [[ "$FORMAT" == "json" ]]; then
  echo "$SALES"
else
  echo "=== Sales Report ==="
  [[ -n "$AFTER" ]] && echo "After: $AFTER"
  [[ -n "$PRODUCT" ]] && echo "Product: $PRODUCT"
  echo ""
  
  # Simple table output
  echo "$SALES" | grep -o '"product_name":"[^"]*"[^}]*"price":[0-9]*[^}]*"created_at":"[^"]*"' | \
    while read line; do
      NAME=$(echo "$line" | grep -o '"product_name":"[^"]*"' | cut -d'"' -f4)
      PRICE=$(echo "$line" | grep -o '"price":[0-9]*' | cut -d':' -f2)
      DATE=$(echo "$line" | grep -o '"created_at":"[^"]*"' | cut -d'"' -f4 | cut -dT -f1)
      DOLLARS=$(echo "scale=2; $PRICE / 100" | bc 2>/dev/null || echo "$PRICE")
      echo "$DATE | \$$DOLLARS | $NAME"
    done
fi
