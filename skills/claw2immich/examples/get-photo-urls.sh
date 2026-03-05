#!/usr/bin/env bash
# Example: Get photo URLs for assets
# Usage: ./get-photo-urls.sh <person-name> [limit] [immich-server-url]

set -euo pipefail

PERSON="${1:-}"
LIMIT="${2:-5}"
IMMICH_SERVER="${3:-http://joesnuc:2283}"

if [[ -z "$PERSON" ]]; then
  echo "Usage: $0 <person-name> [limit] [immich-server-url]"
  echo "Example: $0 Alice 5 http://joesnuc:2283"
  exit 1
fi

echo "🔍 Searching for: $PERSON"

# Find person
PERSON_DATA=$(mcporter call immich.immich_searchperson \
  query_name="$PERSON" \
  --output json 2>/dev/null)

PERSON_ID=$(echo "$PERSON_DATA" | jq -r '.[0].id // empty')

if [[ -z "$PERSON_ID" ]]; then
  echo "❌ Person not found: $PERSON"
  exit 1
fi

PERSON_NAME=$(echo "$PERSON_DATA" | jq -r '.[0].name')
echo "✓ Found: $PERSON_NAME (ID: $PERSON_ID)"

# Search photos
echo ""
echo "📸 Fetching latest $LIMIT photos..."

RESULTS=$(mcporter call immich.immich_searchassets \
  --args "{
    \"body_personIds\": [\"$PERSON_ID\"],
    \"query_order\": \"desc\",
    \"query_size\": $LIMIT
  }" \
  --output json 2>/dev/null)

COUNT=$(echo "$RESULTS" | jq -r '.assets.count // 0')

if [[ "$COUNT" -eq 0 ]]; then
  echo "No photos found for $PERSON_NAME"
  exit 0
fi

echo "Found $COUNT photo(s)"
echo ""
echo "📷 Photo URLs:"
echo ""

# Generate URLs for each photo
echo "$RESULTS" | jq -r --arg server "$IMMICH_SERVER" '.assets.items[] | 
  "File: \(.originalFileName) (\(.fileCreatedAt[:10]))\n" +
  "  Thumbnail: \($server)/api/assets/\(.id)/thumbnail\n" +
  "  Original:  \($server)/api/assets/\(.id)/original\n" +
  "  ID:        \(.id)\n"'

# Optional: Download first photo
echo ""
read -p "Download first photo? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  FIRST_ID=$(echo "$RESULTS" | jq -r '.assets.items[0].id')
  FIRST_NAME=$(echo "$RESULTS" | jq -r '.assets.items[0].originalFileName')
  
  echo "Downloading: $FIRST_NAME"
  curl -o "$FIRST_NAME" "${IMMICH_SERVER}/api/assets/${FIRST_ID}/original"
  echo "✓ Saved to: $FIRST_NAME"
fi
