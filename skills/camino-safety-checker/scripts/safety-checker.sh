#!/bin/bash
# Camino AI Late Night Safety - Find safety resources near any location
# Usage: ./safety-checker.sh '{"location": {"lat": 40.7506, "lon": -73.9935}, "radius": 500}'

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
    echo "Usage: ./safety-checker.sh '{\"location\": {\"lat\": 40.7506, \"lon\": -73.9935}, \"radius\": 500}'" >&2
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

# Check for required field
LOCATION=$(echo "$INPUT" | jq '.location // empty')

if [ "$LOCATION" = "null" ] || [ -z "$LOCATION" ]; then
    echo "Error: 'location' field with lat/lon is required" >&2
    exit 1
fi

# Extract location and optional radius
LAT=$(echo "$LOCATION" | jq -r '.lat // empty')
LON=$(echo "$LOCATION" | jq -r '.lon // empty')
RADIUS=$(echo "$INPUT" | jq -r '.radius // "500"')

if [ -z "$LAT" ] || [ -z "$LON" ]; then
    echo "Error: 'location' must contain 'lat' and 'lon' fields" >&2
    exit 1
fi

# Build context request body with safety-focused context
CONTEXT_BODY=$(jq -n \
    --argjson lat "$LAT" \
    --argjson lon "$LON" \
    --argjson radius "$RADIUS" \
    '{
        "location": {"lat": $lat, "lon": $lon},
        "radius": $radius,
        "context": "late night safety: 24-hour businesses, transit, police, hospitals"
    }')

# Make context API request
curl -s -X POST \
    -H "X-API-Key: $CAMINO_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Client: claude-code-skill" \
    -d "$CONTEXT_BODY" \
    "https://api.getcamino.ai/context" | jq .
