#!/usr/bin/env bash
# Example: Find photos by date range
# Usage: ./find-by-date.sh "2024-06-01" "2024-08-31" [city] [limit]

set -euo pipefail

START_DATE="${1:-}"
END_DATE="${2:-}"
CITY="${3:-}"
LIMIT="${4:-20}"

if [[ -z "$START_DATE" ]] || [[ -z "$END_DATE" ]]; then
  echo "Usage: $0 <start-date> <end-date> [city] [limit]"
  echo "Example: $0 2024-06-01 2024-08-31 Paris 10"
  echo ""
  echo "Dates in YYYY-MM-DD format"
  exit 1
fi

# Convert to ISO 8601 with timezone
START_ISO="${START_DATE}T00:00:00Z"
END_ISO="${END_DATE}T23:59:59Z"

echo "📅 Searching photos from $START_DATE to $END_DATE"
[[ -n "$CITY" ]] && echo "📍 Location: $CITY"
echo ""

# Build query
QUERY="{
  \"body_createdAfter\": \"$START_ISO\",
  \"body_createdBefore\": \"$END_ISO\",
  \"query_order\": \"desc\",
  \"query_size\": $LIMIT"

if [[ -n "$CITY" ]]; then
  QUERY="$QUERY,
  \"body_city\": \"$CITY\""
fi

QUERY="$QUERY
}"

# Search
RESULTS=$(mcporter call immich.immich_searchassets \
  --args "$QUERY" \
  --output json 2>/dev/null)

TOTAL=$(echo "$RESULTS" | jq -r '.assets.total // 0')
COUNT=$(echo "$RESULTS" | jq -r '.assets.count // 0')

echo "Results: $COUNT of $TOTAL total matches"
echo ""

if [[ "$COUNT" -eq 0 ]]; then
  echo "No photos found in this date range."
  exit 0
fi

# Display grouped by date
echo "📷 Photos by date:"
echo "$RESULTS" | jq -r '.assets.items[] | 
  "\(.fileCreatedAt[:10]) - \(.originalFileName)"' | 
  awk '{
    if ($1 != prev) {
      if (prev != "") print ""
      prev = $1
      print "  " $1 ":"
    }
    sub(/^[^ ]+ - /, "    • ")
    print
  }'

echo ""
echo "Summary:"
echo "$RESULTS" | jq -r '.assets.items | group_by(.fileCreatedAt[:10]) | 
  map({date: .[0].fileCreatedAt[:10], count: length}) | 
  .[] | "  \(.date): \(.count) photo(s)"'
