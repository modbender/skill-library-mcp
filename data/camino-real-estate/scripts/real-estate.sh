#!/bin/bash
# Camino AI Real Estate Scout - Evaluate locations for home buyers and renters
# Usage: ./real-estate.sh '{"address": "742 Evergreen Terrace, Springfield", "radius": 1000}'

set -e

# Check dependencies
for cmd in jq curl; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: '$cmd' is required but not installed" >&2
        exit 1
    fi
done

# Check if input is provided
if [ -z "$1" ]; then
    echo "Error: JSON input required" >&2
    echo "Usage: ./real-estate.sh '{\"address\": \"742 Evergreen Terrace, Springfield\", \"radius\": 1000}'" >&2
    echo "   or: ./real-estate.sh '{\"location\": {\"lat\": 40.7589, \"lon\": -73.9851}, \"radius\": 1000}'" >&2
    exit 1
fi

INPUT="$1"

# Validate JSON
if ! echo "$INPUT" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON input" >&2
    exit 1
fi

# Check for API key
if [ -z "$CAMINO_API_KEY" ]; then
    echo "Error: CAMINO_API_KEY environment variable not set" >&2
    echo "Get your API key at https://app.getcamino.ai" >&2
    exit 1
fi

# Check for required fields (address or location)
ADDRESS=$(echo "$INPUT" | jq -r '.address // empty')
LOCATION=$(echo "$INPUT" | jq '.location // empty')
RADIUS=$(echo "$INPUT" | jq -r '.radius // "1000"')

if [ -z "$ADDRESS" ] && { [ "$LOCATION" = "null" ] || [ -z "$LOCATION" ]; }; then
    echo "Error: 'address' or 'location' (with lat/lon) is required" >&2
    exit 1
fi

# If address is provided, geocode it first
if [ -n "$ADDRESS" ]; then
    encoded_query=$(jq -rn --arg v "$ADDRESS" '$v|@uri')
    GEOCODE_RESULT=$(curl -s -X GET \
        -H "X-API-Key: $CAMINO_API_KEY" \
        -H "X-Client: claude-code-skill" \
        "https://api.getcamino.ai/query?query=${encoded_query}&limit=1")

    # Extract lat/lon from first result
    LAT=$(echo "$GEOCODE_RESULT" | jq -r '.results[0].lat // empty')
    LON=$(echo "$GEOCODE_RESULT" | jq -r '.results[0].lon // empty')

    if [ -z "$LAT" ] || [ -z "$LON" ]; then
        echo "Error: Could not geocode address '$ADDRESS'" >&2
        exit 1
    fi
else
    LAT=$(echo "$LOCATION" | jq -r '.lat // empty')
    LON=$(echo "$LOCATION" | jq -r '.lon // empty')

    if [ -z "$LAT" ] || [ -z "$LON" ]; then
        echo "Error: 'location' must contain 'lat' and 'lon' fields" >&2
        exit 1
    fi
fi

# Build context request body
CONTEXT_BODY=$(jq -n \
    --argjson lat "$LAT" \
    --argjson lon "$LON" \
    --argjson radius "$RADIUS" \
    '{
        "location": {"lat": $lat, "lon": $lon},
        "radius": $radius,
        "context": "real estate evaluation: schools, transit, grocery, parks, restaurants, walkability"
    }')

# Make context API request
curl -s -X POST \
    -H "X-API-Key: $CAMINO_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Client: claude-code-skill" \
    -d "$CONTEXT_BODY" \
    "https://api.getcamino.ai/context" | jq .
