#!/usr/bin/env bash
# Search FEC individual contributions (political donations)
# Usage: fec-lookup.sh "First Last" [STATE]
# Example: fec-lookup.sh "John Smith" FL

set -euo pipefail

NAME="${1:?Usage: fec-lookup.sh \"First Last\" [STATE]}"
STATE="${2:-}"

BASE="https://api.open.fec.gov/v1/schedules/schedule_a/"
# FEC API key (demo key, rate-limited but functional)
API_KEY="DEMO_KEY"

PARAMS="contributor_name=${NAME// /+}&sort=-contribution_receipt_date&per_page=20&api_key=${API_KEY}"
[ -n "$STATE" ] && PARAMS="${PARAMS}&contributor_state=${STATE}"

URL="${BASE}?${PARAMS}"

echo "Searching FEC contributions for: $NAME ${STATE:+(state: $STATE)}"
echo "URL: $URL"
echo "---"

RESPONSE=$(curl -s "$URL")

COUNT=$(echo "$RESPONSE" | jq -r '.pagination.count // 0')
echo "Total results: $COUNT"
echo ""

if [ "$COUNT" = "0" ]; then
    echo "No political contributions found."
    exit 0
fi

echo "$RESPONSE" | jq -r '.results[] | "Date: \(.contribution_receipt_date) | Amount: $\(.contribution_receipt_amount) | To: \(.committee.name // "Unknown") | City: \(.contributor_city // "?"), \(.contributor_state // "?") | Employer: \(.contributor_employer // "N/A") | Occupation: \(.contributor_occupation // "N/A")"'
