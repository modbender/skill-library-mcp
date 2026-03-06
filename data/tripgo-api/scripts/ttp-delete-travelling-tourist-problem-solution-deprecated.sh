#!/bin/bash
#
# Get Solution to Travelling Tourist Problem (Deprecated)
# GET /ttp/{id}/solution
#
# Note: The documentation title incorrectly shows "Delete travelling tourist problem"
# but this endpoint actually retrieves the solution for the problem.
#
# Retrieves the solution for the problem of the provided ID.
# The solution may take time to be created.
# Use hashCode query parameter to check if solution has changed.
#

TRIPGO_API_KEY="${TRIPGO_API_KEY:-your-api-key-here}"
BASE_URL="https://api.tripgo.com/v1"

# Usage function
usage() {
    echo "Usage: $0 <problem-id> [hashCode]"
    echo "Example: $0 abc123"
    echo "Example with hashCode: $0 abc123 12345"
    exit 1
}

# Check for problem ID
if [ -z "$1" ]; then
    usage
fi

PROBLEM_ID="$1"
HASH_CODE="$2"

# Build URL with optional hashCode
URL="${BASE_URL}/ttp/${PROBLEM_ID}/solution"
if [ -n "$HASH_CODE" ]; then
    URL="${URL}?hashCode=${HASH_CODE}"
fi

echo "Getting solution for travelling tourist problem: $PROBLEM_ID"
if [ -n "$HASH_CODE" ]; then
    echo "Using hashCode: $HASH_CODE"
fi

curl -X GET "${URL}" \
  -H "X-TripGo-Key: ${TRIPGO_API_KEY}"

echo ""
echo "Note: This endpoint is DEPRECATED"
echo "Note: Documentation title incorrectly says 'Delete travelling tourist problem' but URL is /ttp/{id}/solution"
