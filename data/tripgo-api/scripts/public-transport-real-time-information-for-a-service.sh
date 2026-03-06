#!/bin/bash
# Real-time Information for a Service
# POST /latest.json
#
# Retrieves real-time information for specified services.
#
# Usage: ./public-transport-real-time-information-for-a-service.sh --region REGION --services JSON
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key
#
# Example services JSON:
#   '[{"operator":"Sydney Buses","serviceTripID":"766415652016030700000","startStopCode":"2035143"}]'

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/latest.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region)
      REGION="$2"
      shift 2
      ;;
    --services)
      SERVICES="$2"
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

if [[ -z "${REGION:-}" ]] || [[ -z "${SERVICES:-}" ]]; then
  echo "Error: --region and --services are required"
  exit 1
fi

if ! jq -e . >/dev/null 2>&1 <<<"$SERVICES"; then
  echo "Error: --services must be valid JSON"
  exit 1
fi

BODY=$(jq -n \
  --arg region "$REGION" \
  --argjson services "$SERVICES" \
  '{region: $region, services: $services}')

echo "Making request to $ENDPOINT"
echo "Request body: $BODY"

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $API_KEY" \
  -d "$BODY" | jq '.'
