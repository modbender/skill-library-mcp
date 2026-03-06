#!/usr/bin/env bash
# =============================================================================
# TripGo API - TSPs per Region
# Endpoint: POST /regionInfo.json
# Description: Retrieves basic information about covered transport service
#              providers for the specified regions.
# =============================================================================

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-}"
TRIPGO_BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

# Default parameters
REGION="${REGION:-}"

# Usage function
usage() {
    cat << USAGE
Usage: $(basename "$0") [OPTIONS]

Options:
    -k, --api-key KEY    TripGo API key (required, or set TRIPGO_API_KEY)
    -r, --region CODE    Region code from regions.json (required)
    -u, --base-url URL   Base URL (default: https://api.tripgo.com/v1)
    -h, --help           Show this help message

Examples:
    $(basename "$0") -k YOUR_API_KEY -r DE_HH_Hamburg
    $(basename "$0") -k YOUR_API_KEY --region AU_SYD_Sydney
USAGE
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--api-key)
            TRIPGO_API_KEY="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
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

# Validate region
if [[ -z "$REGION" ]]; then
    echo "Error: Region is required. Use -r/--region to specify a region code."
    echo "       Use /regions.json endpoint to get available region codes."
    exit 1
fi

# Build request body
REQUEST_BODY=$(jq -n \
    --arg region "$REGION" \
    '{
        region: $region
    }')

# Make request
echo "Fetching TSPs for region: ${REGION}..."
curl -s -X POST "${TRIPGO_BASE_URL}/regionInfo.json" \
    -H "Content-Type: application/json" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -d "$REQUEST_BODY" | jq '.'
