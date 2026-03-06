#!/bin/bash
#
# Delete Travelling Tourist Problem (Deprecated)
# DELETE /ttp/{id}
#
# Deletes the problem of the provided ID.
# This is optional as problems expire automatically.
#

set -euo pipefail

TRIPGO_API_KEY="${TRIPGO_API_KEY:-your-api-key-here}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Usage function
usage() {
    echo "Usage: $0 <problem-id>"
    echo "Example: $0 abc123"
    exit 1
}

# Check for problem ID
if [[ $# -lt 1 ]]; then
    usage
fi

PROBLEM_ID="$1"
PROBLEM_ID_ENC="$(urlencode "$PROBLEM_ID")"

echo "Deleting travelling tourist problem: $PROBLEM_ID"

curl -s -X DELETE "${BASE_URL}/ttp/${PROBLEM_ID_ENC}" \
  -H "X-TripGo-Key: ${TRIPGO_API_KEY}"

echo ""
echo "Note: This endpoint is DEPRECATED"
