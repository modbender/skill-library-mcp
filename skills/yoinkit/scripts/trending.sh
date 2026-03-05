#!/bin/bash
# yoinkit trending <platform>
# Get trending content across platforms

set -e

PLATFORM="$1"
shift 2>/dev/null || true

# Supported platforms with trending
SUPPORTED_PLATFORMS=("youtube" "tiktok")

# Validate platform
if [[ ! " ${SUPPORTED_PLATFORMS[@]} " =~ " ${PLATFORM} " ]]; then
    echo "Error: Platform $PLATFORM does not support trending or is not supported"
    echo "Supported platforms: ${SUPPORTED_PLATFORMS[*]}"
    exit 1
fi

if [ -z "$YOINKIT_API_TOKEN" ]; then
    echo "Error: YOINKIT_API_TOKEN not configured"
    exit 1
fi

API_BASE="${YOINKIT_API_URL:-https://yoinkit.ai/api/v1/openclaw}"

# Default parameters
TYPE="trending"        # For TikTok: trending, popular, hashtags
COUNTRY="US"           # For TikTok trending: region
PERIOD=""              # For TikTok popular/hashtags: 7, 30
PAGE=""                # For TikTok popular/hashtags: page number
ORDER=""               # For TikTok popular: hot, like, comment, repost

# Parse additional options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --type)
            TYPE="$2"
            shift 2
            ;;
        --country)
            COUNTRY="$2"
            shift 2
            ;;
        --period)
            PERIOD="$2"
            shift 2
            ;;
        --page)
            PAGE="$2"
            shift 2
            ;;
        --order)
            ORDER="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Construct endpoint based on platform and type
if [[ "$PLATFORM" == "youtube" ]]; then
    # YouTube trending takes NO parameters
    ENDPOINT="youtube/trending"
elif [[ "$PLATFORM" == "tiktok" ]]; then
    case "$TYPE" in
        trending)
            # Params: region (required), trim
            ENDPOINT="tiktok/trending?region=$COUNTRY"
            ;;
        popular)
            # Params: period (7|30), page, orderBy (like|hot|comment|repost), countryCode
            ENDPOINT="tiktok/popular?countryCode=$COUNTRY"
            [ -n "$PERIOD" ] && ENDPOINT+="&period=$PERIOD"
            [ -n "$PAGE" ] && ENDPOINT+="&page=$PAGE"
            [ -n "$ORDER" ] && ENDPOINT+="&orderBy=$ORDER"
            ;;
        hashtags)
            # Params: period (7|30|120), page, countryCode, newOnBoard
            ENDPOINT="tiktok/hashtags?countryCode=$COUNTRY"
            [ -n "$PERIOD" ] && ENDPOINT+="&period=$PERIOD"
            [ -n "$PAGE" ] && ENDPOINT+="&page=$PAGE"
            ;;
        *)
            echo "Error: Unknown TikTok trending type: $TYPE"
            echo "Supported types: trending, popular, hashtags"
            exit 1
            ;;
    esac
fi

# Make API request
RESPONSE=$(curl -s -H "Authorization: Bearer $YOINKIT_API_TOKEN" \
    "$API_BASE/$ENDPOINT")

# Check for errors
if echo "$RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
    ERROR=$(echo "$RESPONSE" | jq -r '.error.message // .error // "Unknown error"')
    echo "Error: $ERROR"
    exit 1
fi

# Output formatted results from data wrapper
echo "$RESPONSE" | jq '.data // .'
