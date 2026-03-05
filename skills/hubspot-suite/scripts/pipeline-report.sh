#!/bin/bash
# Export deal pipeline report as CSV
# Usage: ./pipeline-report.sh [pipeline-id]
# Requires: HUBSPOT_ACCESS_TOKEN

set -euo pipefail

TOKEN="${HUBSPOT_ACCESS_TOKEN:?Set HUBSPOT_ACCESS_TOKEN}"
BASE="https://api.hubapi.com"
PIPELINE_ID="${1:-default}"

echo "dealname,dealstage,amount,closedate,owner,createdate"

AFTER=""
while true; do
  URL="${BASE}/crm/v3/objects/deals?limit=100&properties=dealname,dealstage,amount,closedate,hubspot_owner_id,createdate"
  [ -n "$AFTER" ] && URL="${URL}&after=${AFTER}"
  
  RESP=$(curl -s -H "Authorization: Bearer ${TOKEN}" "$URL")
  
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    p = r.get('properties', {})
    name = (p.get('dealname') or '').replace(',', ';')
    stage = p.get('dealstage', '')
    amount = p.get('amount', '0')
    close = p.get('closedate', '')[:10] if p.get('closedate') else ''
    owner = p.get('hubspot_owner_id', '')
    created = p.get('createdate', '')[:10] if p.get('createdate') else ''
    print(f'{name},{stage},{amount},{close},{owner},{created}')
" <<< "$RESP" 2>/dev/null

  AFTER=$(python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('paging',{}).get('next',{}).get('after',''))" <<< "$RESP" 2>/dev/null)
  [ -z "$AFTER" ] && break
done
