#!/bin/bash
# Cloudsways SmartSearch API script
# Usage: ./search.sh '{"q": "your search query", "count": 10}'

set -e

# 1. Authentication Check
if [ -z "$CLOUDSWAYS_AK" ]; then
    echo "Error: Missing Authentication."
    echo "Please set CLOUDSWAYS_AK environment variable."
    exit 1
fi

JSON_INPUT="$1"

# 2. Input Validation & Help Text
if [ -z "$JSON_INPUT" ]; then
    echo "Usage: ./search.sh '<json>'"
    echo ""
    echo "Required:"
    echo "  q: string - User search query term (cannot be empty)"
    echo ""
    echo "Optional:"
    echo "  count: number - Results count (10, 20, 30, 40, 50. Default: 10)"
    echo "  freshness: string - 'Day', 'Week', 'Month'"
    echo "  offset: number - Pagination offset (Default: 0)"
    echo "  enableContent: boolean - Include full text content (Default: false)"
    echo "  mainText: boolean - Return dynamic summary key fragments (Default: false)"
    echo "  contentTimeout: float - Full text read timeout (Max 10.0, Default: 3.0)"
    echo ""
    echo "Example:"
    echo "  ./search.sh '{\"q\": \"open ai recent news\", \"freshness\": \"Week\"}'"
    exit 1
fi

if ! echo "$JSON_INPUT" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON input"
    exit 1
fi

# 3. Extract Required Parameters
QUERY=$(echo "$JSON_INPUT" | jq -r '.q // empty')
if [ -z "$QUERY" ]; then
    echo "Error: 'q' (query) field is required"
    exit 1
fi

# 4. Build GET Request Parameters
CURL_ARGS=("--data-urlencode" "q=$QUERY")

COUNT=$(echo "$JSON_INPUT" | jq -r '.count // empty')
[ -n "$COUNT" ] && CURL_ARGS+=("--data-urlencode" "count=$COUNT")

FRESHNESS=$(echo "$JSON_INPUT" | jq -r '.freshness // empty')
[ -n "$FRESHNESS" ] && CURL_ARGS+=("--data-urlencode" "freshness=$FRESHNESS")

OFFSET=$(echo "$JSON_INPUT" | jq -r '.offset // empty')
[ -n "$OFFSET" ] && CURL_ARGS+=("--data-urlencode" "offset=$OFFSET")

ENABLE_CONTENT=$(echo "$JSON_INPUT" | jq -r '.enableContent // empty')
[ -n "$ENABLE_CONTENT" ] && CURL_ARGS+=("--data-urlencode" "enableContent=$ENABLE_CONTENT")

MAIN_TEXT=$(echo "$JSON_INPUT" | jq -r '.mainText // empty')
[ -n "$MAIN_TEXT" ] && CURL_ARGS+=("--data-urlencode" "mainText=$MAIN_TEXT")

CONTENT_TIMEOUT=$(echo "$JSON_INPUT" | jq -r '.contentTimeout // empty')
[ -n "$CONTENT_TIMEOUT" ] && CURL_ARGS+=("--data-urlencode" "contentTimeout=$CONTENT_TIMEOUT")

# 5. Execute API Call
RESPONSE=$(curl -s -G \
    --url "https://truthapi.cloudsway.net/api/search/smart" \
    --header "Authorization:  ${CLOUDSWAYS_AK}" \
    "${CURL_ARGS[@]}")

# 6. Parse and Clean Response (Optimized for LLM context)
JSON_DATA=$(echo "$RESPONSE" | jq '.webPages.value | map({
    title: .name,
    url: .url,
    snippet: .snippet,
    mainText: .mainText,
    content: .content,
    datePublished: .datePublished
} | del(.. | nulls))' 2>/dev/null)

if [ -n "$JSON_DATA" ] && [ "$JSON_DATA" != "null" ]; then
    echo "$JSON_DATA"
else
    # Fallback to raw response if parsing fails or error occurs
    echo "$RESPONSE"
fi