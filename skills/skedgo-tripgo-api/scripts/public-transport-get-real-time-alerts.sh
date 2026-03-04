#!/bin/bash
# Get Real-time Alerts
# GET /alerts/transit.json
#
# Retrieves real-time alerts for a region.
#
# Usage: ./public-transport-get-real-time-alerts.sh --region REGION
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/alerts/transit.json"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region)
      REGION="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$API_KEY" ]]; then
  echo "Error: TRIPGO_API_KEY environment variable is required"
  exit 1
fi

if [[ -z "${REGION:-}" ]]; then
  echo "Error: --region is required"
  exit 1
fi

QUERY="region=$(urlencode "$REGION")"

echo "Making request to $ENDPOINT?$QUERY"

curl -s -X GET "$ENDPOINT?$QUERY" \
  -H "X-TripGo-Key: $API_KEY" | jq '.'
