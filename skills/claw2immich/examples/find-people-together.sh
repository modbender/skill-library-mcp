#!/usr/bin/env bash
# Example: Find photos with multiple people together
# Usage: ./find-people-together.sh "Alice" "Bob" [limit]

set -euo pipefail

PERSON1="${1:-}"
PERSON2="${2:-}"
LIMIT="${3:-10}"

if [[ -z "$PERSON1" ]] || [[ -z "$PERSON2" ]]; then
  echo "Usage: $0 <person1> <person2> [limit]"
  echo "Example: $0 Alice Bob 5"
  exit 1
fi

echo "🔍 Searching for people..."

# Find first person
echo "Finding: $PERSON1"
PERSON1_DATA=$(mcporter call immich.immich_searchperson \
  query_name="$PERSON1" \
  --output json 2>/dev/null)

PERSON1_ID=$(echo "$PERSON1_DATA" | jq -r '.[0].id // empty')

if [[ -z "$PERSON1_ID" ]]; then
  echo "❌ Person not found: $PERSON1"
  exit 1
fi

echo "✓ Found: $PERSON1 (ID: $PERSON1_ID)"

# Find second person
echo "Finding: $PERSON2"
PERSON2_DATA=$(mcporter call immich.immich_searchperson \
  query_name="$PERSON2" \
  --output json 2>/dev/null)

PERSON2_ID=$(echo "$PERSON2_DATA" | jq -r '.[0].id // empty')

if [[ -z "$PERSON2_ID" ]]; then
  echo "❌ Person not found: $PERSON2"
  exit 1
fi

echo "✓ Found: $PERSON2 (ID: $PERSON2_ID)"

# Search photos with both people
echo ""
echo "📸 Searching photos with both people together..."

RESULTS=$(mcporter call immich.immich_searchassets \
  --args "{
    \"body_personIds\": [\"$PERSON1_ID\", \"$PERSON2_ID\"],
    \"query_order\": \"desc\",
    \"query_size\": $LIMIT
  }" \
  --output json 2>/dev/null)

TOTAL=$(echo "$RESULTS" | jq -r '.assets.total // 0')
COUNT=$(echo "$RESULTS" | jq -r '.assets.count // 0')

echo ""
echo "Results: $COUNT of $TOTAL total matches"
echo ""

if [[ "$COUNT" -eq 0 ]]; then
  echo "No photos found with both $PERSON1 and $PERSON2 together."
  exit 0
fi

# Display results
echo "📷 Photos:"
echo "$RESULTS" | jq -r '.assets.items[] | "  - \(.originalFileName) (\(.fileCreatedAt[:10]))"'

# Optionally show most recent photo details
echo ""
echo "Most recent photo:"
echo "$RESULTS" | jq -r '.assets.items[0] | "  File: \(.originalFileName)\n  Date: \(.fileCreatedAt)\n  Path: \(.originalPath)\n  ID: \(.id)"'
