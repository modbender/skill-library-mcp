#!/bin/bash
# Mark Trip as Planned by a User
# POST /trip/planned/{id}

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-your-api-key-here}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Check if trip ID is provided
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <planned-url-id>"
    echo "Example: $0 abc123def456"
    echo ""
    echo "Note: Use the plannedURL from the original trip response"
    echo "This endpoint is used for analytics to track which trips users actually took"
    exit 1
fi

TRIP_ID="$1"
TRIP_ID_ENC="$(urlencode "$TRIP_ID")"

# Make the request
curl -s -X POST "${BASE_URL}/trip/planned/${TRIP_ID_ENC}" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -H "Accept: application/json"
