#!/bin/bash
# Update Trip with Real-Time Data
# GET /trip/update/{id}

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-your-api-key-here}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Check if trip ID is provided
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <update-url-id> [hash]"
    echo "Example: $0 abc123def456 abc123hash"
    echo ""
    echo "Note: Use the updateURL from the original trip response"
    echo "The optional hash parameter allows checking for changes without full response"
    exit 1
fi

TRIP_ID="$1"
HASH="${2:-}"
TRIP_ID_ENC="$(urlencode "$TRIP_ID")"

# Build the URL
URL="${BASE_URL}/trip/update/${TRIP_ID_ENC}"
if [[ -n "$HASH" ]]; then
    URL="${URL}?hash=$(urlencode "$HASH")"
fi

# Make the request
curl -s -X GET "${URL}" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -H "Accept: application/json"
