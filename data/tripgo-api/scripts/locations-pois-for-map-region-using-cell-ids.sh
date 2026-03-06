#!/bin/bash
#
# POIs for Map Region (using cell IDs)
# POST /locations.json
#
# Gets points of interest for a provided map region using cell IDs.
# Recommended for caching locations locally with efficient updates.
#

TRIPGO_KEY="${TRIPGO_KEY:-your-api-key-here}"

# Required: Region code (e.g., "AU_NSW_Sydney")
REGION="${REGION:-AU_NSW_Sydney}"

# Cell IDs - can be provided via CELL_IDS env var (comma-separated)
CELL_IDS="${CELL_IDS---2540#11340,-2540#11341,-2540#11342,-2541#11340,-2541#11341,-2541#11342}"

# Optional parameters
LEVELS="${LEVELS:-1}"
CELLS_PER_DEGREE="${CELLS_PER_DEGREE:-75}"
MODES="${MODES:-}"
STRICT_MODE_MATCH="${STRICT_MODE_MATCH:-true}"
INCLUDE_CHILDREN="${INCLUDE_CHILDREN:-false}"
INCLUDE_ROUTES="${INCLUDE_ROUTES:-false}"
INCLUDE_DROP_OFF_ONLY="${INCLUDE_DROP_OFF_ONLY:-false}"

# Convert comma-separated CELL_IDS to JSON array
CELL_IDS_JSON=$(echo "$CELL_IDS" | tr ',' '\n' | jq -R . | jq -s .)

# Build JSON body
JSON_BODY=$(jq -n \
  --arg region "$REGION" \
  --argjson levels "$LEVELS" \
  --argjson cellIDs "$CELL_IDS_JSON" \
  --argjson cellsPerDegree "$CELLS_PER_DEGREE" \
  --argjson strictModeMatch "$STRICT_MODE_MATCH" \
  --argjson includeChildren "$INCLUDE_CHILDREN" \
  --argjson includeRoutes "$INCLUDE_ROUTES" \
  --argjson includeDropOffOnly "$INCLUDE_DROP_OFF_ONLY" \
  '{
    region: $region,
    levels: $levels,
    cellIDs: $cellIDs,
    cellsPerDegree: $cellsPerDegree,
    strictModeMatch: $strictModeMatch,
    includeChildren: $includeChildren,
    includeRoutes: $includeRoutes,
    includeDropOffOnly: $includeDropOffOnly
  }')

# Add modes if provided
if [ -n "$MODES" ]; then
  MODES_JSON=$(echo "$MODES" | tr ',' '\n' | jq -R . | jq -s .)
  JSON_BODY=$(echo "$JSON_BODY" | jq --argjson modes "$MODES_JSON" '. + {modes: $modes}')
fi

echo "Fetching POIs for map region..."
echo "  Region: ${REGION}"
echo "  Levels: ${LEVELS}"
echo "  Cell IDs: ${CELL_IDS}"
echo ""

echo "$JSON_BODY" | jq .

echo ""
echo "Making request..."

curl -s -X POST "https://api.tripgo.com/v1/locations.json" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: ${TRIPGO_KEY}" \
  -d "$JSON_BODY" | jq .
