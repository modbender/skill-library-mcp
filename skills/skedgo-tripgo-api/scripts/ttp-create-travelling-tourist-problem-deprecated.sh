#!/bin/bash
#
# Create Travelling Tourist Problem (Deprecated)
# POST /ttp/
#
# Creates a new instance of a travelling tourist problem.
# Returns an ID which can be used to fetch the solution.
#

TRIPGO_API_KEY="${TRIPGO_API_KEY:-your-api-key-here}"
BASE_URL="https://api.tripgo.com/v1"

# Example request body
REQUEST_BODY='{
  "date": "2016-05-30T00:00:00.000+00:00",
  "modes": ["pt_pub", "ps_tax", "wa_wal", "cy_bic-s"],
  "insertInto": [
    {"id": 1, "lat": -33.5, "lng": 151.1},
    {"id": 2, "lat": -33.6, "lng": 151.1},
    {"id": 3, "lat": -33.4, "lng": 150.9},
    {"id": 4, "lat": -33.5, "lng": 151.1}
  ],
  "insert": [
    {"lat": -33.55, "lng": 151.15}
  ]
}'

echo "Creating travelling tourist problem..."
echo "Request body:"
echo "$REQUEST_BODY" | jq '.'

curl -X POST "${BASE_URL}/ttp/" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
  -d "$REQUEST_BODY" \
  --compressed

echo ""
echo "Note: This endpoint is DEPRECATED"
