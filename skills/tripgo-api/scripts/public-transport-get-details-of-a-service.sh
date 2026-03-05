#!/bin/bash
# Get Details of a Service
# GET /service.json
#
# Gets the details of a transit service from the traveller's perspective.
#
# Usage: ./public-transport-get-details-of-a-service.sh --region REGION --service-trip-id ID --embarkation-date INT --encode BOOL [--operator NAME] [--start-stop-code CODE] [--end-stop-code CODE]
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/service.json"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region)
      REGION="$2"
      shift 2
      ;;
    --service-trip-id)
      SERVICE_TRIP_ID="$2"
      shift 2
      ;;
    --embarkation-date)
      EMBARKATION_DATE="$2"
      shift 2
      ;;
    --encode)
      ENCODE="$2"
      shift 2
      ;;
    --operator)
      OPERATOR="$2"
      shift 2
      ;;
    --start-stop-code)
      START_STOP_CODE="$2"
      shift 2
      ;;
    --end-stop-code)
      END_STOP_CODE="$2"
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

if [[ -z "${REGION:-}" ]] || [[ -z "${SERVICE_TRIP_ID:-}" ]] || [[ -z "${EMBARKATION_DATE:-}" ]] || [[ -z "${ENCODE:-}" ]]; then
  echo "Error: --region, --service-trip-id, --embarkation-date, and --encode are required"
  exit 1
fi

QUERY="region=$(urlencode "$REGION")&serviceTripID=$(urlencode "$SERVICE_TRIP_ID")&embarkationDate=$(urlencode "$EMBARKATION_DATE")&encode=$(urlencode "$ENCODE")"

if [[ -n "${OPERATOR:-}" ]]; then
  QUERY="$QUERY&operator=$(urlencode "$OPERATOR")"
fi

if [[ -n "${START_STOP_CODE:-}" ]]; then
  QUERY="$QUERY&startStopCode=$(urlencode "$START_STOP_CODE")"
fi

if [[ -n "${END_STOP_CODE:-}" ]]; then
  QUERY="$QUERY&endStopCode=$(urlencode "$END_STOP_CODE")"
fi

echo "Making request to $ENDPOINT?$QUERY"

curl -s -X GET "$ENDPOINT?$QUERY" \
  -H "X-TripGo-Key: $API_KEY" | jq '.'
