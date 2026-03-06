#!/bin/bash
# TripGo API - A-to-B Trips
# Endpoint: GET /routing.json
# Documentation: https://developer.tripgo.com/#/routing/paths/~1routing.json/get

# Configuration
TRIPGO_API_KEY="${TRIPGO_KEY:-YOUR_API_KEY}"
BASE_URL="https://api.tripgo.com/v1"

# Default values
VERSION="11"
FROM_COORD=""
TO_COORD=""
MODES=""
DEPART_AFTER=""
ARRIVE_BEFORE=""
LOCALE="en"

# Usage function
usage() {
    echo "Usage: $0 -f <from_coord> -t <to_coord> -m <modes> [options]"
    echo ""
    echo "Required options:"
    echo "  -f, --from COORD      Origin coordinate as (lat,lng)\"name\" (e.g., '(-33.859,151.207)\"Sydney\"')"
    echo "  -t, --to COORD        Destination coordinate as (lat,lng)\"name\" (e.g., '(-33.863,151.208)\"Melbourne\"')"
    echo "  -m, --modes MODES     Transport modes (e.g., 'pt_pub,wa_wal' or 'me_car')"
    echo ""
    echo "Optional options:"
    echo "  -d, --depart TIME     Departure time in seconds since 1970"
    echo "  -a, --arrive TIME     Arrival time in seconds since 1970"
    echo "  -v, --version VERSION API version (default: 11)"
    echo "  -l, --locale LOCALE   Locale for results (default: en)"
    echo "  -o, --all-modes       Return all trips, not just multi-modal"
    echo "  -w, --wheelchair      Include wheelchair accessibility"
    echo "  -b, --best-only       Return only the best trip"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -f '(-33.859,151.207)' -t '(-33.863,151.208)' -m 'wa_wal' -d 1532799914"
    echo "  $0 -f '(-33.859,151.207)' -t '(-33.891,151.209)' -m 'pt_pub'"
    echo ""
    echo "Mode identifiers:"
    echo "  pt_pub   - Public transport"
    echo "  wa_wal   - Walk"
    echo "  me_car   - Car"
    echo "  cy_bic   - Bicycle"
    echo "  ps_tax   - Taxi"
    echo "  ps_tnc   - Rideshare (Uber, etc.)"
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
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -l|--locale)
            LOCALE="$2"
            shift 2
            ;;
        -o|--all-modes)
            ALL_MODES="true"
            shift
            ;;
        -w|--wheelchair)
            WHEELCHAIR="true"
            shift
            ;;
        -b|--best-only)
            BEST_ONLY="true"
            shift
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
if [[ -z "$FROM_COORD" ]] || [[ -z "$TO_COORD" ]] || [[ -z "$MODES" ]]; then
    echo "Error: Missing required parameters"
    usage
fi

# Build the query URL
URL="${BASE_URL}/routing.json?v=${VERSION}&from=${FROM_COORD}&to=${TO_COORD}&modes=${MODES}&locale=${LOCALE}"

# Add optional parameters
[[ -n "$DEPART_AFTER" ]] && URL="${URL}&departAfter=${DEPART_AFTER}"
[[ -n "$ARRIVE_BEFORE" ]] && URL="${URL}&arriveBefore=${ARRIVE_BEFORE}"
[[ "$ALL_MODES" == "true" ]] && URL="${URL}&allModes=true"
[[ "$WHEELCHAIR" == "true" ]] && URL="${URL}&wheelchair=true"
[[ "$BEST_ONLY" == "true" ]] && URL="${URL}&bestOnly=true"

# Make the request
echo "Making request to: ${URL}&... (API key hidden)"
echo ""

curl -s -G "${URL}" \
    -H "Accept: application/json" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" | jq '.'
