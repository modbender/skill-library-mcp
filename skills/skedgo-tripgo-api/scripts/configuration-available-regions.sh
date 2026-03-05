#!/usr/bin/env bash
# =============================================================================
# TripGo API - Available Regions
# Endpoint: POST /regions.json
# Description: Lists available regions and available transport modes.
# =============================================================================

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-}"
TRIPGO_BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"

# Default parameters
VERSION="${VERSION:-2}"
CITY_POLYGONS="${CITY_POLYGONS:-false}"
HASH_CODE="${HASH_CODE:-}"

# Usage function
usage() {
    cat << USAGE
Usage: $(basename "$0") [OPTIONS]

Options:
    -k, --api-key KEY       TripGo API key (required, or set TRIPGO_API_KEY)
    -v, --version NUM      API version number (default: 2)
    -p, --polygons         Include city polygons (default: false)
    -h, --hash-code CODE   Hash code for caching (optional)
    -u, --base-url URL     Base URL (default: https://api.tripgo.com/v1)
    -h, --help             Show this help message

Examples:
    $(basename "$0") -k YOUR_API_KEY
    $(basename "$0") -k YOUR_API_KEY -v 2 -p
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
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -p|--polygons)
            CITY_POLYGONS="true"
            shift
            ;;
        --hash-code)
            HASH_CODE="$2"
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

# Build request body
REQUEST_BODY=$(jq -n \
    --argjson v "$VERSION" \
    --argjson cityPolygons "$CITY_POLYGONS" \
    '{
        v: $v,
        cityPolygons: $cityPolygons
    }')

# Add hashCode if provided
if [[ -n "$HASH_CODE" ]]; then
    REQUEST_BODY=$(echo "$REQUEST_BODY" | jq --argjson hashCode "$HASH_CODE" '. + {hashCode: $hashCode}')
fi

# Make request
echo "Fetching available regions..."
curl -s -X POST "${TRIPGO_BASE_URL}/regions.json" \
    -H "Content-Type: application/json" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -d "$REQUEST_BODY" | jq '.'
