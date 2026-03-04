#!/bin/bash
# yoinkit search <platform> <query>
# Search content across social platforms

set -e

PLATFORM="$1"
QUERY="$2"
shift 2 2>/dev/null || true

# Supported platforms with search
SUPPORTED_PLATFORMS=("youtube" "tiktok" "instagram" "reddit" "pinterest")

# Validate platform
if [[ ! " ${SUPPORTED_PLATFORMS[@]} " =~ " ${PLATFORM} " ]]; then
    echo "Error: Platform $PLATFORM does not support search or is not supported"
    echo "Supported platforms: ${SUPPORTED_PLATFORMS[*]}"
    exit 1
fi

if [ -z "$QUERY" ]; then
    echo "Error: Query required"
    echo "Usage: yoinkit search <platform> \"<query>\" [options]"
    exit 1
fi

if [ -z "$YOINKIT_API_TOKEN" ]; then
    echo "Error: YOINKIT_API_TOKEN not configured"
    exit 1
fi

API_BASE="${YOINKIT_API_URL:-https://yoinkit.ai/api/v1/openclaw}"

# Platform-specific defaults
SORT=""
TIME=""
CONTINUATION=""
CURSOR=""
PAGE=""

# Parse additional options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --sort)
            SORT="$2"
            shift 2
            ;;
        --time)
            TIME="$2"
            shift 2
            ;;
        --continuation)
            CONTINUATION="$2"
            shift 2
            ;;
        --cursor)
            CURSOR="$2"
            shift 2
            ;;
        --page)
            PAGE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build endpoint with platform-specific params
ENCODED_QUERY=$(echo "$QUERY" | jq -sRr @uri)

case "$PLATFORM" in
    youtube)
        # Params: query (required), uploadDate, sortBy, filter, continuationToken, includeExtras
        QUERY_PARAMS="query=$ENCODED_QUERY"
        [ -n "$SORT" ] && QUERY_PARAMS+="&sortBy=$SORT"           # relevance, popular
        [ -n "$TIME" ] && QUERY_PARAMS+="&uploadDate=$TIME"       # today, this_week, this_month, this_year
        [ -n "$CONTINUATION" ] && QUERY_PARAMS+="&continuationToken=$CONTINUATION"
        ;;
    tiktok)
        # Params: query (required), date_posted, sort_by, region, cursor, trim
        QUERY_PARAMS="query=$ENCODED_QUERY"
        [ -n "$SORT" ] && QUERY_PARAMS+="&sort_by=$SORT"          # relevance, most-liked, date-posted
        [ -n "$TIME" ] && QUERY_PARAMS+="&date_posted=$TIME"      # yesterday, this-week, this-month, last-3-months, last-6-months, all-time
        [ -n "$CURSOR" ] && QUERY_PARAMS+="&cursor=$CURSOR"
        ;;
    instagram)
        # Params: query (required), page
        QUERY_PARAMS="query=$ENCODED_QUERY"
        [ -n "$PAGE" ] && QUERY_PARAMS+="&page=$PAGE"
        ;;
    reddit)
        # Params: query (required), sort, timeframe, after, trim
        QUERY_PARAMS="query=$ENCODED_QUERY"
        [ -n "$SORT" ] && QUERY_PARAMS+="&sort=$SORT"             # relevance, new, top, comment_count
        [ -n "$TIME" ] && QUERY_PARAMS+="&timeframe=$TIME"        # all, day, week, month, year
        [ -n "$CURSOR" ] && QUERY_PARAMS+="&after=$CURSOR"
        ;;
    pinterest)
        # Params: query (required), cursor, trim
        QUERY_PARAMS="query=$ENCODED_QUERY"
        [ -n "$CURSOR" ] && QUERY_PARAMS+="&cursor=$CURSOR"
        ;;
esac

# Make API request
RESPONSE=$(curl -s -H "Authorization: Bearer $YOINKIT_API_TOKEN" \
    "$API_BASE/$PLATFORM/search?$QUERY_PARAMS")

# Check for errors
if echo "$RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
    ERROR=$(echo "$RESPONSE" | jq -r '.error.message // .error // "Unknown error"')
    echo "Error: $ERROR"
    exit 1
fi

# Output formatted results from data wrapper
echo "$RESPONSE" | jq '.data // .'
