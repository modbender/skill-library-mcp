#!/bin/bash
# Details of a Route
# POST /info/routeInfo.json
#
# Retrieves detailed information about a route and its stops.
#
# Usage: ./public-transport-details-of-a-route.sh --regions JSON --operator-id ID --route-id ID
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/info/routeInfo.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --regions)
      REGIONS="$2"
      shift 2
      ;;
    --operator-id)
      OPERATOR_ID="$2"
      shift 2
      ;;
    --route-id)
      ROUTE_ID="$2"
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

if [[ -z "${REGIONS:-}" ]] || [[ -z "${OPERATOR_ID:-}" ]] || [[ -z "${ROUTE_ID:-}" ]]; then
  echo "Error: --regions, --operator-id, and --route-id are required"
  exit 1
fi

if ! jq -e . >/dev/null 2>&1 <<<"$REGIONS"; then
  echo "Error: --regions must be valid JSON"
  exit 1
fi

BODY=$(jq -n \
  --argjson regions "$REGIONS" \
  --arg operatorID "$OPERATOR_ID" \
  --arg routeID "$ROUTE_ID" \
  '{regions: $regions, operatorID: $operatorID, routeID: $routeID}')

echo "Making request to $ENDPOINT"
echo "Request body: $BODY"

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $API_KEY" \
  -d "$BODY" | jq '.'
