#!/bin/bash
# HubSpot Data Quality Audit — checks for common data issues
# Usage: ./data-audit.sh
# Requires: HUBSPOT_ACCESS_TOKEN

set -euo pipefail

TOKEN="${HUBSPOT_ACCESS_TOKEN:?Set HUBSPOT_ACCESS_TOKEN}"
BASE="https://api.hubapi.com"

echo "📊 HubSpot Data Quality Audit"
echo "=============================="
echo ""

# Count objects
for OBJ in contacts companies deals tickets; do
  COUNT=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
    "${BASE}/crm/v3/objects/${OBJ}?limit=1" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)
  echo "📦 ${OBJ}: ${COUNT} records"
done

echo ""
echo "🔍 Checking contacts without email..."
NO_EMAIL=$(curl -s -X POST "${BASE}/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filters":[{"propertyName":"email","operator":"NOT_HAS_PROPERTY"}],"limit":1}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)
echo "   Contacts without email: ${NO_EMAIL}"

echo ""
echo "🔍 Checking companies without domain..."
NO_DOMAIN=$(curl -s -X POST "${BASE}/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filters":[{"propertyName":"domain","operator":"NOT_HAS_PROPERTY"}],"limit":1}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)
echo "   Companies without domain: ${NO_DOMAIN}"

echo ""
echo "🔍 Checking deals without amount..."
NO_AMOUNT=$(curl -s -X POST "${BASE}/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filters":[{"propertyName":"amount","operator":"NOT_HAS_PROPERTY"}],"limit":1}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)
echo "   Deals without amount: ${NO_AMOUNT}"

echo ""
echo "✅ Audit complete"
