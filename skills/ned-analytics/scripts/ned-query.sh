#!/bin/bash
# ned-query.sh — Query Ned API endpoints
# Usage: ned-query.sh <endpoint> [period]
# Example: ned-query.sh profitability/summary last_7_days

ENDPOINT="${1:?Usage: ned-query.sh <endpoint> [period]}"
PERIOD="${2:-last_7_days}"

if [ -z "$NED_API_KEY" ]; then
  echo "ERROR: NED_API_KEY not set. Export your Ned API key first:"
  echo "  export NED_API_KEY=ned_live_xxxxx"
  exit 1
fi

URL="https://api.meetned.com/api/v1/${ENDPOINT}?period=${PERIOD}"

response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $NED_API_KEY" "$URL")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" != "200" ]; then
  echo "ERROR: HTTP $http_code"
  echo "$body"
  exit 1
fi

echo "$body"
