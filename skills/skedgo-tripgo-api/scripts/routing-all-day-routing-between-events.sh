#!/bin/bash
# TripGo API - All-Day Routing Between Events
# Endpoint: POST /agenda/run
# Documentation: https://developer.tripgo.com/#/routing/paths/~1agenda~1run/post

# Configuration
TRIPGO_API_KEY="${TRIPGO_KEY:-YOUR_API_KEY}"
BASE_URL="https://api.tripgo.com/v1"

# Default values
MODES=""
START_TIME=""
END_TIME=""
ITEMS_JSON=""

# Usage function
usage() {
    echo "Usage: $0 -s <start_time> -e <end_time> -m <modes> -i <items_json>"
    echo ""
    echo "Required options:"
    echo "  -s, --start TIME      Start time in seconds since 1970"
    echo "  -e, --end TIME        End time in seconds since 1970"
    echo "  -m, --modes MODES     Transport modes (comma-separated)"
    echo "  -i, --items JSON      JSON array of agenda items"
    echo ""
    echo "Optional options:"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Items JSON format:"
    echo '  [{"location":"(lat,lng)\"name\"","event":"home"},{"location":"(lat,lng)\"name\"","event":"work","startTime":1234567890,"endTime":1234571490}]'
    echo ""
    echo "Examples:"
    echo "  $0 -s 1532793600 -e 1532822400 -m 'pt_pub,me_car' -i '[{\"location\":\"(-33.859,151.207)\",\"event\":\"home\"},{\"location\":\"(-33.891,151.209)\",\"event\":\"work\",\"startTime\":1532800800,\"endTime\":1532811600}]'"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--start)
            START_TIME="$2"
            shift 2
            ;;
        -e|--end)
            END_TIME="$2"
            shift 2
            ;;
        -m|--modes)
            MODES="$2"
            shift 2
            ;;
        -i|--items)
            ITEMS_JSON="$2"
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
if [[ -z "$START_TIME" ]] || [[ -z "$END_TIME" ]] || [[ -z "$MODES" ]] || [[ -z "$ITEMS_JSON" ]]; then
    echo "Error: Missing required parameters"
    usage
fi

# Build JSON payload
JSON_payload="{
  \"config\": {
    \"modes\": [\"${MODES//,/,\",\"}\"]
  },
  \"frame\": {
    \"startTime\": ${START_TIME},
    \"endTime\": ${END_TIME}
  },
  \"items\": ${ITEMS_JSON}
}"

# Make the request
echo "Making POST request to: ${BASE_URL}/agenda/run"
echo "Payload:"
echo "$JSON_payload" | jq '.'
echo ""

curl -s -X POST "${BASE_URL}/agenda/run" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -d "$JSON_payload" | jq '.'
