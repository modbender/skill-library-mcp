#!/bin/bash
# Services for a Route
# POST /info/services.json
#
# Retrieves detailed information about services for a specified route.
#
# Usage: ./public-transport-services-for-a-route.sh --regions JSON --operator-id ID --route-id ID [--service-trip-ids JSON] [--full BOOL] [--only-realtime BOOL]
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/info/services.json"

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
    --service-trip-ids)
      SERVICE_TRIP_IDS="$2"
      shift 2
      ;;
    --full)
      FULL="$2"
      shift 2
      ;;
    --only-realtime)
      ONLY_REAL_TIME="$2"
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

if [[ -n "${SERVICE_TRIP_IDS:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$SERVICE_TRIP_IDS"; then
    echo "Error: --service-trip-ids must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson serviceTripIDs "$SERVICE_TRIP_IDS" '. + {serviceTripIDs: $serviceTripIDs}' <<<"$BODY")
fi

if [[ -n "${FULL:-}" ]]; then
  BODY=$(jq --argjson full "$FULL" '. + {full: $full}' <<<"$BODY")
fi

if [[ -n "${ONLY_REAL_TIME:-}" ]]; then
  BODY=$(jq --argjson onlyRealTime "$ONLY_REAL_TIME" '. + {onlyRealTime: $onlyRealTime}' <<<"$BODY")
fi

echo "Making request to $ENDPOINT"
echo "Request body: $BODY"

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $API_KEY" \
  -d "$BODY" | jq '.'
