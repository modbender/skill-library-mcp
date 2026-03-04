#!/bin/bash
#
# POIs for a Circular Region
# GET /locations.json
#
# Gets points of interest for a provided circular region (coordinate + radius).
#

set -euo pipefail

TRIPGO_KEY="${TRIPGO_KEY:-${TRIPGO_API_KEY:-your-api-key-here}}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Default values (Sydney CBD)
LAT="${LAT:--33.859}"
LNG="${LNG:151.207}"
RADIUS="${RADIUS:-1000}"

# Optional parameters
MODES="${MODES:-}"
STRICT_MODE_MATCH="${STRICT_MODE_MATCH:-true}"
LIMIT="${LIMIT:-}"
INCLUDE_CHILDREN="${INCLUDE_CHILDREN:-false}"
INCLUDE_ROUTES="${INCLUDE_ROUTES:-false}"
INCLUDE_DROP_OFF_ONLY="${INCLUDE_DROP_OFF_ONLY:-false}"
SORTED_BY_PROXIMITY="${SORTED_BY_PROXIMITY:-false}"

# Build query string
QUERY_PARAMS="lat=$(urlencode "$LAT")&lng=$(urlencode "$LNG")&radius=$(urlencode "$RADIUS")&strictModeMatch=$(urlencode "$STRICT_MODE_MATCH")&includeChildren=$(urlencode "$INCLUDE_CHILDREN")&includeRoutes=$(urlencode "$INCLUDE_ROUTES")&includeDropOffOnly=$(urlencode "$INCLUDE_DROP_OFF_ONLY")&sortedByProximity=$(urlencode "$SORTED_BY_PROXIMITY")"

if [[ -n "$MODES" ]]; then
  QUERY_PARAMS="${QUERY_PARAMS}&modes=$(urlencode "$MODES")"
fi

if [[ -n "$LIMIT" ]]; then
  QUERY_PARAMS="${QUERY_PARAMS}&limit=$(urlencode "$LIMIT")"
fi

echo "Fetching POIs for circular region..."
echo "  Lat: ${LAT}, Lng: ${LNG}, Radius: ${RADIUS}m"
echo ""

curl -s -X GET "${BASE_URL}/locations.json?${QUERY_PARAMS}" \
  -H "Accept: application/json" \
  -H "X-TripGo-Key: ${TRIPGO_KEY}" | jq .
