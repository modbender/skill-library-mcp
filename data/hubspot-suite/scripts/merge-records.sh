#!/bin/bash
# Merge two HubSpot records (keep primary, merge data from duplicate)
# Usage: ./merge-records.sh <object-type> <primary-id> <duplicate-id>
# Example: ./merge-records.sh contacts 123 456

set -euo pipefail

OBJECT_TYPE="${1:?Usage: merge-records.sh <object-type> <primary-id> <duplicate-id>}"
PRIMARY_ID="${2:?Usage: merge-records.sh <object-type> <primary-id> <duplicate-id>}"
DUPLICATE_ID="${3:?Usage: merge-records.sh <object-type> <primary-id> <duplicate-id>}"
TOKEN="${HUBSPOT_ACCESS_TOKEN:?Set HUBSPOT_ACCESS_TOKEN}"
BASE="https://api.hubapi.com"

echo "🔗 Merging ${OBJECT_TYPE}: ${DUPLICATE_ID} → ${PRIMARY_ID}..."

RESP=$(curl -s -w "\n%{http_code}" -X POST \
  "${BASE}/crm/v3/objects/${OBJECT_TYPE}/merge" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"primaryObjectId\": \"${PRIMARY_ID}\", \"objectIdToMerge\": \"${DUPLICATE_ID}\"}")

HTTP_CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Merged successfully. Primary record: ${PRIMARY_ID}"
else
  echo "❌ Merge failed (HTTP ${HTTP_CODE}): ${BODY}"
  exit 1
fi
