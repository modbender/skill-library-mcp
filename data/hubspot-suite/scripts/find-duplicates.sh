#!/bin/bash
# Find duplicate records in HubSpot by a specific property
# Usage: ./find-duplicates.sh <object-type> <property>
# Example: ./find-duplicates.sh contacts email

set -euo pipefail

OBJECT_TYPE="${1:?Usage: find-duplicates.sh <object-type> <property>}"
PROPERTY="${2:?Usage: find-duplicates.sh <object-type> <property>}"
TOKEN="${HUBSPOT_ACCESS_TOKEN:?Set HUBSPOT_ACCESS_TOKEN}"
BASE="https://api.hubapi.com"

echo "🔍 Finding duplicates in ${OBJECT_TYPE} by ${PROPERTY}..."

# Fetch all records with the specified property
AFTER=""
declare -A SEEN
DUPES=()

while true; do
  URL="${BASE}/crm/v3/objects/${OBJECT_TYPE}?limit=100&properties=${PROPERTY}"
  [ -n "$AFTER" ] && URL="${URL}&after=${AFTER}"
  
  RESP=$(curl -s -H "Authorization: Bearer ${TOKEN}" "$URL")
  
  RESULTS=$(echo "$RESP" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    val = r.get('properties', {}).get('$PROPERTY', '')
    if val:
        print(f\"{r['id']}|{val}\")
" 2>/dev/null)

  while IFS='|' read -r id val; do
    [ -z "$val" ] && continue
    if [ -n "${SEEN[$val]:-}" ]; then
      echo "⚠️  Duplicate: ${PROPERTY}=${val} → IDs: ${SEEN[$val]}, ${id}"
      DUPES+=("$val")
    fi
    SEEN["$val"]="${SEEN[$val]:-}${SEEN[$val]:+, }${id}"
  done <<< "$RESULTS"

  AFTER=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('paging',{}).get('next',{}).get('after',''))" 2>/dev/null)
  [ -z "$AFTER" ] && break
done

echo ""
echo "Found ${#DUPES[@]} duplicate(s) by ${PROPERTY}"
