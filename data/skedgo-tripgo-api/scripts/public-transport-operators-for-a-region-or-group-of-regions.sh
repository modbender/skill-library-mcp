#!/bin/bash
# Operators for a Region or Group of Regions
# POST /info/operators.json
#
# Retrieves detailed information about covered transport service providers for a specified region.
#
# Usage: ./public-transport-operators-for-a-region-or-group-of-regions.sh
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/info/operators.json"

# Default request body
REGIONS='["US_CA_LosAngeles"]'
MODES='["pt_pub_tram","pt_pub_bus"]'
FULL='true'

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --regions)
      REGIONS="$2"
      shift 2
      ;;
    --modes)
      MODES="$2"
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
    --operator-ids)
      OPERATOR_IDS="$2"
      shift 2
      ;;
    --operator-names)
      OPERATOR_NAMES="$2"
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
if ! jq -e . >/dev/null 2>&1 <<<"$MODES"; then
  echo "Error: --modes must be valid JSON"
  exit 1
fi

BODY=$(jq -n \
  --argjson regions "$REGIONS" \
  --argjson modes "$MODES" \
  --argjson full "$FULL" \
  '{regions: $regions, modes: $modes, full: $full}')

if [[ -n "${ONLY_REAL_TIME:-}" ]]; then
  BODY=$(jq --argjson onlyRealTime "$ONLY_REAL_TIME" '. + {onlyRealTime: $onlyRealTime}' <<<"$BODY")
fi

if [[ -n "${OPERATOR_IDS:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$OPERATOR_IDS"; then
    echo "Error: --operator-ids must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson operatorIDs "$OPERATOR_IDS" '. + {operatorIDs: $operatorIDs}' <<<"$BODY")
fi

if [[ -n "${OPERATOR_NAMES:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$OPERATOR_NAMES"; then
    echo "Error: --operator-names must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson operatorNames "$OPERATOR_NAMES" '. + {operatorNames: $operatorNames}' <<<"$BODY")
fi

echo "Making request to $ENDPOINT"
echo "Request body: $BODY"

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $API_KEY" \
  -d "$BODY" | jq '.'
