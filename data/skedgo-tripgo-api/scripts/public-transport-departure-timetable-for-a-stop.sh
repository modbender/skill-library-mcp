#!/bin/bash
# Departure Timetable for a Stop
# POST /departures.json
#
# Gets the departure timetable for a provided list of transit stops.
#
# Usage: ./public-transport-departure-timetable-for-a-stop.sh --region REGION --embarkation-stops JSON [--disembarkation-region REGION] [--disembarkation-stops JSON] [--timestamp INT] [--limit INT] [--include-stops BOOL]
#
# Required environment variables:
#   TRIPGO_API_KEY - Your TripGo API key

set -euo pipefail

API_KEY="${TRIPGO_API_KEY:-}"
ENDPOINT="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}/departures.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region)
      REGION="$2"
      shift 2
      ;;
    --embarkation-stops)
      EMBARKATION_STOPS="$2"
      shift 2
      ;;
    --disembarkation-region)
      DISEMBARKATION_REGION="$2"
      shift 2
      ;;
    --disembarkation-stops)
      DISEMBARKATION_STOPS="$2"
      shift 2
      ;;
    --timestamp)
      TIMESTAMP="$2"
      shift 2
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --include-stops)
      INCLUDE_STOPS="$2"
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

if [[ -z "${REGION:-}" ]] || [[ -z "${EMBARKATION_STOPS:-}" ]]; then
  echo "Error: --region and --embarkation-stops are required"
  exit 1
fi

if ! jq -e . >/dev/null 2>&1 <<<"$EMBARKATION_STOPS"; then
  echo "Error: --embarkation-stops must be valid JSON"
  exit 1
fi

BODY=$(jq -n \
  --arg region "$REGION" \
  --argjson embarkationStops "$EMBARKATION_STOPS" \
  '{region: $region, embarkationStops: $embarkationStops}')

if [[ -n "${DISEMBARKATION_REGION:-}" ]]; then
  BODY=$(jq --arg disembarkationRegion "$DISEMBARKATION_REGION" '. + {disembarkationRegion: $disembarkationRegion}' <<<"$BODY")
fi

if [[ -n "${DISEMBARKATION_STOPS:-}" ]]; then
  if ! jq -e . >/dev/null 2>&1 <<<"$DISEMBARKATION_STOPS"; then
    echo "Error: --disembarkation-stops must be valid JSON"
    exit 1
  fi
  BODY=$(jq --argjson disembarkationStops "$DISEMBARKATION_STOPS" '. + {disembarkationStops: $disembarkationStops}' <<<"$BODY")
fi

if [[ -n "${TIMESTAMP:-}" ]]; then
  BODY=$(jq --argjson timeStamp "$TIMESTAMP" '. + {timeStamp: $timeStamp}' <<<"$BODY")
fi

if [[ -n "${LIMIT:-}" ]]; then
  BODY=$(jq --argjson limit "$LIMIT" '. + {limit: $limit}' <<<"$BODY")
fi

if [[ -n "${INCLUDE_STOPS:-}" ]]; then
  BODY=$(jq --argjson includeStops "$INCLUDE_STOPS" '. + {includeStops: $includeStops}' <<<"$BODY")
fi

echo "Making request to $ENDPOINT"
echo "Request body: $BODY"

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $API_KEY" \
  -d "$BODY" | jq '.'
