#!/bin/bash
#
# TripGo Geocode API - Search and Autocompletion
# https://developer.tripgo.com/#/geocode/paths/~1geocode.json/get
#

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-YOUR_API_KEY}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

# Default values
QUERY=""
NEAR=""
AUTOCOMPLETE=false
ALLOW_GOOGLE=false
ALLOW_W3W=false
ALLOW_YELP=false
ALLOW_FOURSQUARE=false
LIMIT=25

urlencode() {
    jq -nr --arg v "$1" '$v|@uri'
}

# Function to display usage
usage() {
    echo "Usage: $0 -q <query> -n <near coordinate>"
    echo ""
    echo "Options:"
    echo "  -q, --query <term>       Search term (required)"
    echo "  -n, --near <coord>      Nearby coordinate as (lat,lng) (required)"
    echo "  -a, --autocomplete       Enable autocompletion mode"
    echo "  -g, --allow-google       Enable Google Places geocoding"
    echo "  -w, --allow-w3w          Enable What3Words geocoding"
    echo "  -y, --allow-yelp         Enable Yelp geocoding"
    echo "  -f, --allow-foursquare   Enable Foursquare geocoding"
    echo "  -l, --limit <num>        Limit results (default: 25)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -q \"Central Station\" -n \"(-33.8688,151.2093)\""
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--query)
            QUERY="$2"
            shift 2
            ;;
        -n|--near)
            NEAR="$2"
            shift 2
            ;;
        -a|--autocomplete)
            AUTOCOMPLETE=true
            shift
            ;;
        -g|--allow-google)
            ALLOW_GOOGLE=true
            shift
            ;;
        -w|--allow-w3w)
            ALLOW_W3W=true
            shift
            ;;
        -y|--allow-yelp)
            ALLOW_YELP=true
            shift
            ;;
        -f|--allow-foursquare)
            ALLOW_FOURSQUARE=true
            shift
            ;;
        -l|--limit)
            LIMIT="$2"
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
if [[ -z "$QUERY" ]]; then
    echo "Error: Query parameter (-q) is required"
    usage
fi

if [[ -z "$NEAR" ]]; then
    echo "Error: Near coordinate (-n) is required"
    usage
fi

# Build query string safely
URL="${BASE_URL}/geocode.json?q=$(urlencode "$QUERY")&near=$(urlencode "$NEAR")"

if [[ "$AUTOCOMPLETE" == "true" ]]; then
    URL="${URL}&a=true"
fi

if [[ "$ALLOW_GOOGLE" == "true" ]]; then
    URL="${URL}&allowGoogle=true"
fi

if [[ "$ALLOW_W3W" == "true" ]]; then
    URL="${URL}&allowW3W=true"
fi

if [[ "$ALLOW_YELP" == "true" ]]; then
    URL="${URL}&allowYelp=true"
fi

if [[ "$ALLOW_FOURSQUARE" == "true" ]]; then
    URL="${URL}&allowFoursquare=true"
fi

if [[ "$LIMIT" != "25" ]]; then
    URL="${URL}&limit=$(urlencode "$LIMIT")"
fi

# Make the request
echo "Making request to: ${URL}"
echo ""

curl -s -X GET "$URL" \
    -H "Accept: application/json" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" | python3 -m json.tool

echo ""
