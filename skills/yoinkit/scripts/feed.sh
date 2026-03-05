#!/bin/bash
# yoinkit feed <platform> <handle>
# Get a user's recent posts/videos

set -e

PLATFORM="$1"
HANDLE="$2"
shift 2 2>/dev/null || true

SUPPORTED_PLATFORMS=("youtube" "tiktok" "instagram" "twitter" "facebook" "threads" "bluesky" "truthsocial")

if [[ ! " ${SUPPORTED_PLATFORMS[@]} " =~ " ${PLATFORM} " ]]; then
    echo "Error: Platform $PLATFORM does not support user feeds"
    echo "Supported platforms: ${SUPPORTED_PLATFORMS[*]}"
    exit 1
fi

if [ -z "$HANDLE" ]; then
    echo "Error: Handle/username required"
    echo "Usage: yoinkit feed <platform> <handle> [options]"
    echo ""
    echo "Options:"
    echo "  --type posts|reels|videos   Content type (Instagram/Facebook)"
    echo "  --sort latest|popular       Sort order (YouTube)"
    echo "  --cursor TOKEN              Pagination cursor"
    exit 1
fi

if [ -z "$YOINKIT_API_TOKEN" ]; then
    echo "Error: YOINKIT_API_TOKEN not configured"
    exit 1
fi

API_BASE="${YOINKIT_API_URL:-https://yoinkit.ai/api/v1/openclaw}"

# Strip @ prefix if present
HANDLE="${HANDLE#@}"

# Defaults
TYPE="posts"
SORT=""
CURSOR=""

# Parse additional options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --type)
            TYPE="$2"
            shift 2
            ;;
        --sort)
            SORT="$2"
            shift 2
            ;;
        --cursor)
            CURSOR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

ENCODED_HANDLE=$(echo "$HANDLE" | jq -sRr @uri)

case "$PLATFORM" in
    youtube)
        # Params: handle or channelId (required), sort, continuationToken, includeExtras
        ENDPOINT="youtube/channel/videos?handle=$ENCODED_HANDLE"
        [ -n "$SORT" ] && ENDPOINT+="&sort=$SORT"
        [ -n "$CURSOR" ] && ENDPOINT+="&continuationToken=$CURSOR"
        ;;
    tiktok)
        # Params: handle or user_id (required), cursor, trim
        ENDPOINT="tiktok/user/videos?handle=$ENCODED_HANDLE"
        [ -n "$CURSOR" ] && ENDPOINT+="&cursor=$CURSOR"
        ;;
    instagram)
        # Params: handle (required), max_id
        if [[ "$TYPE" == "reels" ]]; then
            ENDPOINT="instagram/user/reels?handle=$ENCODED_HANDLE"
        else
            ENDPOINT="instagram/user/posts?handle=$ENCODED_HANDLE"
        fi
        [ -n "$CURSOR" ] && ENDPOINT+="&max_id=$CURSOR"
        ;;
    twitter)
        # Params: handle or userId (required), cursor, trim
        ENDPOINT="twitter/user/tweets?handle=$ENCODED_HANDLE"
        [ -n "$CURSOR" ] && ENDPOINT+="&cursor=$CURSOR"
        ;;
    facebook)
        # Params: url or pageId (required), cursor
        # Facebook uses page URLs or IDs, not handles — pass as-is
        if [[ "$TYPE" == "reels" ]]; then
            ENDPOINT="facebook/user/reels?url=$(echo "https://facebook.com/$HANDLE" | jq -sRr @uri)"
        else
            ENDPOINT="facebook/user/posts?url=$(echo "https://facebook.com/$HANDLE" | jq -sRr @uri)"
        fi
        [ -n "$CURSOR" ] && ENDPOINT+="&cursor=$CURSOR"
        ;;
    threads)
        # Params: handle (required), max_id, trim
        ENDPOINT="threads/user/posts?handle=$ENCODED_HANDLE"
        [ -n "$CURSOR" ] && ENDPOINT+="&max_id=$CURSOR"
        ;;
    bluesky)
        # Params: handle or user_id (required), cursor
        ENDPOINT="bluesky/user/posts?handle=$ENCODED_HANDLE"
        [ -n "$CURSOR" ] && ENDPOINT+="&cursor=$CURSOR"
        ;;
    truthsocial)
        # Params: handle or user_id (required), max_id
        ENDPOINT="truthsocial/user/posts?handle=$ENCODED_HANDLE"
        [ -n "$CURSOR" ] && ENDPOINT+="&max_id=$CURSOR"
        ;;
esac

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
