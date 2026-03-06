#!/usr/bin/env bash
# =============================================================================
# TripGo API - POIs for a Transport Mode
# Endpoint: GET /regions/{code}/locations
# Description: Bulk fetch of all locations for the provided mode in a region.
# =============================================================================

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-}"
TRIPGO_BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

# Default parameters
REGION_CODE="${REGION_CODE:-}"
MODE="${MODE:-}"
INCLUDE_CHILDREN="${INCLUDE_CHILDREN:-true}"
INCLUDE_ROUTES="${INCLUDE_ROUTES:-false}"

urlencode() {
    jq -nr --arg v "$1" '$v|@uri'
}

# Usage function
usage() {
    cat << USAGE
Usage: $(basename "$0") [OPTIONS]

Options:
    -k, --api-key KEY         TripGo API key (required, or set TRIPGO_API_KEY)
    -r, --region-code CODE    Region code from regions.json (required)
    -m, --mode MODE           Transport mode identifier (required)
    -c, --include-children    Include child stops (default: true)
    --no-children             Don't include child stops
    -o, --include-routes      Include route info (default: false)
    -u, --base-url URL        Base URL (default: https://api.tripgo.com/v1)
    -h, --help                Show this help message

Common Transport Modes:
    pt_pub   - Public transport
    me_car   - Car
    me_car-s - Car share
    cy_bic   - Bicycle
    cy_bic-s - Bike share
    ps_tax   - Taxi
    ps_tnc   - Ride share

Examples:
    $(basename "$0") -k YOUR_API_KEY -r DE_HH_Hamburg -m pt_pub
    $(basename "$0") -k YOUR_API_KEY -r AU_SYD_Sydney -m cy_bic-s -c false
USAGE
    exit 1
}

# Parse arguments
INCLUDE_CHILDREN="true"
INCLUDE_ROUTES="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--api-key)
            TRIPGO_API_KEY="$2"
            shift 2
            ;;
        -r|--region-code)
            REGION_CODE="$2"
            shift 2
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -c|--include-children)
            INCLUDE_CHILDREN="true"
            shift
            ;;
        --no-children)
            INCLUDE_CHILDREN="false"
            shift
            ;;
        -o|--include-routes)
            INCLUDE_ROUTES="true"
            shift
            ;;
        -u|--base-url)
            TRIPGO_BASE_URL="$2"
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

# Validate API key
if [[ -z "$TRIPGO_API_KEY" ]]; then
    echo "Error: API key is required. Set TRIPGO_API_KEY or use -k/--api-key"
    exit 1
fi

# Validate region code
if [[ -z "$REGION_CODE" ]]; then
    echo "Error: Region code is required. Use -r/--region-code to specify."
    echo "       Use /regions.json endpoint to get available region codes."
    exit 1
fi

# Validate mode
if [[ -z "$MODE" ]]; then
    echo "Error: Transport mode is required. Use -m/--mode to specify."
    exit 1
fi

# Build query string
QUERY_PARAMS="mode=$(urlencode "$MODE")&includeChildren=$(urlencode "$INCLUDE_CHILDREN")&includeRoutes=$(urlencode "$INCLUDE_ROUTES")"
REGION_CODE_ENC="$(urlencode "$REGION_CODE")"

# Make request
echo "Fetching POIs for mode '${MODE}' in region '${REGION_CODE}'..."
curl -s -X GET "${TRIPGO_BASE_URL}/regions/${REGION_CODE_ENC}/locations?${QUERY_PARAMS}" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" | jq '.'
