#!/bin/bash
#
# Additional Details for a Coordinate
# GET /locationInfo.json
#
# Gets details, including real-time information, for a location.
# Returns what3words information and, if available, nearby transit stop and car park.
#

set -euo pipefail

TRIPGO_KEY="${TRIPGO_KEY:-${TRIPGO_API_KEY:-your-api-key-here}}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Either provide lat/lng OR identifier
# Option 1: Coordinates
LAT="${LAT:-}"
LNG="${LNG:-}"

# Option 2: Unique identifier (requires REGION)
IDENTIFIER="${IDENTIFIER:-}"
REGION="${REGION:-}"

# Build query string
if [[ -n "$IDENTIFIER" ]]; then
  # Using identifier - region is required
  if [[ -z "$REGION" ]]; then
    echo "Error: REGION is required when using IDENTIFIER"
    exit 1
  fi
  QUERY_PARAMS="identifier=$(urlencode "$IDENTIFIER")&region=$(urlencode "$REGION")"
else
  # Using coordinates - lat and lng required
  if [[ -z "$LAT" ]] || [[ -z "$LNG" ]]; then
    echo "Error: LAT and LNG are required (or provide IDENTIFIER)"
    echo "Usage:"
    echo "  LAT=-33.859 LNG=151.207 $0"
    echo "  # or"
    echo "  IDENTIFIER=... REGION=AU_NSW_Sydney $0"
    exit 1
  fi
  QUERY_PARAMS="lat=$(urlencode "$LAT")&lng=$(urlencode "$LNG")"
fi

echo "Fetching location details..."
if [[ -n "$IDENTIFIER" ]]; then
  echo "  Identifier: ${IDENTIFIER}"
  echo "  Region: ${REGION}"
else
  echo "  Lat: ${LAT}, Lng: ${LNG}"
fi
echo ""

curl -s -X GET "${BASE_URL}/locationInfo.json?${QUERY_PARAMS}" \
  -H "Accept: application/json" \
  -H "X-TripGo-Key: ${TRIPGO_KEY}" | jq .
