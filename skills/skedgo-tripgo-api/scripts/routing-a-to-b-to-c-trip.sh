#!/bin/bash
# TripGo API - A-to-B-to-C Trip
# Endpoint: POST /waypoint.json
# Documentation: https://developer.tripgo.com/#/routing/paths/~1waypoint.json/post

# Configuration
TRIPGO_API_KEY="${TRIPGO_KEY:-YOUR_API_KEY}"
BASE_URL="https://api.tripgo.com/v1"

# Default values
FROM_COORD=""
TO_COORD=""
VIA_COORD=""
DEPART_AFTER=""
ARRIVE_BEFORE=""
MODES=""

# Usage function
usage() {
    echo "Usage: $0 -f <from_coord> -t <to_coord> -v <via_coord> [options]"
    echo ""
    echo "Required options:"
    echo "  -f, --from COORD      Origin coordinate as (lat,lng)\"name\" (e.g., '(-33.859,151.207)\"Sydney\"')"
    echo "  -t, --to COORD        Destination coordinate as (lat,lng)\"name\" (e.g., '(-33.891,151.209)\"Melbourne\"')"
    echo "  -v, --via COORD       Waypoint coordinate as (lat,lng)\"name\" (e.g., '(-33.863,151.208)\"Parramatta\"')"
    echo ""
    echo "Optional options:"
    echo "  -m, --modes MODES     Transport modes (comma-separated)"
    echo "  -d, --depart TIME     Departure time in seconds since 1970"
    echo "  -a, --arrive TIME     Arrival time in seconds since 1970"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -f '(-33.859,151.207)' -v '(-33.863,151.208)' -t '(-33.891,151.209)'"
    echo "  $0 -f '(-33.859,151.207)' -v '(-33.863,151.208)' -t '(-33.891,151.209)' -m 'pt_pub,wa_wal'"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--from)
            FROM_COORD="$2"
            shift 2
            ;;
        -t|--to)
            TO_COORD="$2"
            shift 2
            ;;
        -v|--via)
            VIA_COORD="$2"
            shift 2
            ;;
        -m|--modes)
            MODES="$2"
            shift 2
            ;;
        -d|--depart)
            DEPART_AFTER="$2"
            shift 2
            ;;
        -a|--arrive)
            ARRIVE_BEFORE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required parameters
if [[ -z "$FROM_COORD" ]] || [[ -z "$TO_COORD" ]] || [[ -z "$VIA_COORD" ]]; then
    echo "Error: Missing required parameters"
    usage
fi

# Build JSON payload
JSON_payload="{
  \"from\": \"${FROM_COORD}\",
  \"to\": \"${TO_COORD}\",
  \"via\": \"${VIA_COORD}\"
"

# Add optional parameters
[[ -n "$MODES" ]] && JSON_payload="${JSON_payload},\"modes\":[\"${MODES//,/,\",\"}\"]"
[[ -n "$DEPART_AFTER" ]] && JSON_payload="${JSON_payload},\"departAfter\":${DEPART_AFTER}"
[[ -n "$ARRIVE_BEFORE" ]] && JSON_payload="${JSON_payload},\"arriveBefore\":${ARRIVE_BEFORE}"

JSON_payload="${JSON_payload}
}"

# Make the request
echo "Making POST request to: ${BASE_URL}/waypoint.json"
echo "Payload:"
echo "$JSON_payload" | jq '.'
echo ""

curl -s -X POST "${BASE_URL}/waypoint.json" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -d "$JSON_payload" | jq '.'
