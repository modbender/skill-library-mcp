#!/bin/bash
# Routes for a Region or Operator
# POST /info/routes.json
#
# Retrieves detailed information about routes for either all operators in a region, or a specified operator.
#
# Usage: ./public-transport-routes-for-a-region-or-operator.sh [--regions JSON] [--operator-id ID] [--modes JSON] [--query STRING] [--full BOOL] [--only-realtime BOOL]
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/info/routes.json"

# Default request body
REGIONS='["US_CA_LosAngeles"]'
FULL='true'

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
    --modes)
      MODES="$2"
      shift 2
      ;;
    --query)
      QUERY="$2"
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
    --route-ids)
      ROUTE_IDS="$2"
      shift 2
      ;;
    --route-names)
      ROUTE_NAMES="$2"
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

if ! jq -e . >/dev/null 2>&1 <<<"$REGIONS"; then
  echo "Error: --regions must be valid JSON"
  exit 1
fi

BODY=$(jq -n \
  --argjson regions "$REGIONS" \
  --argjson full "$FULL" \
  '{regions: $regions, full: $full}')

if [[ -n "${OPERATOR_ID:-}" ]]; then
  BODY=$(jq --arg operatorID "$OPERATOR_ID" '. + {operatorID: $operatorID}' <<<"$BODY")
fi

if [[ -n "${MODES:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$MODES"; then
    echo "Error: --modes must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson modes "$MODES" '. + {modes: $modes}' <<<"$BODY")
fi

if [[ -n "${QUERY:-}" ]]; then
  BODY=$(jq --arg query "$QUERY" '. + {query: $query}' <<<"$BODY")
fi

if [[ -n "${ONLY_REAL_TIME:-}" ]]; then
  BODY=$(jq --argjson onlyRealTime "$ONLY_REAL_TIME" '. + {onlyRealTime: $onlyRealTime}' <<<"$BODY")
fi

if [[ -n "${ROUTE_IDS:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$ROUTE_IDS"; then
    echo "Error: --route-ids must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson routesIDs "$ROUTE_IDS" '. + {routesIDs: $routesIDs}' <<<"$BODY")
fi

if [[ -n "${ROUTE_NAMES:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$ROUTE_NAMES"; then
    echo "Error: --route-names must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson routesNames "$ROUTE_NAMES" '. + {routesNames: $routesNames}' <<<"$BODY")
fi

echo "Making request to $ENDPOINT"
echo "Request body: $BODY"

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $API_KEY" \
  -d "$BODY" | jq '.'
