#!/bin/bash
# yoinkit content <url>
# Get content and metadata from a social post

set -e

URL="$1"

if [ -z "$URL" ]; then
    echo "Error: URL required"
    echo "Usage: yoinkit content <url>"
    exit 1
fi

if [ -z "$YOINKIT_API_TOKEN" ]; then
    echo "Error: YOINKIT_API_TOKEN not configured"
    exit 1
fi

API_BASE="${YOINKIT_API_URL:-https://yoinkit.ai/api/v1/openclaw}"

# Normalize YouTube short URLs and youtu.be links
if [[ "$URL" == *"youtube.com/shorts/"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's|.*youtube.com/shorts/||' | sed 's|[?&].*||')
    URL="https://www.youtube.com/watch?v=$VIDEO_ID"
elif [[ "$URL" == *"youtu.be/"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's|.*youtu.be/||' | sed 's|[?&].*||')
    URL="https://www.youtube.com/watch?v=$VIDEO_ID"
fi

# Detect platform and construct endpoint
if [[ "$URL" == *"youtube.com"* ]] || [[ "$URL" == *"youtu.be"* ]]; then
    ENDPOINT="youtube/video?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"tiktok.com"* ]]; then
    ENDPOINT="tiktok/video?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"twitter.com"* ]] || [[ "$URL" == *"x.com"* ]]; then
    ENDPOINT="twitter/tweet?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"instagram.com"* ]]; then
    ENDPOINT="instagram/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"reddit.com"* ]]; then
    ENDPOINT="reddit/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"linkedin.com"* ]]; then
    ENDPOINT="linkedin/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"facebook.com"* ]]; then
    ENDPOINT="facebook/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"threads.net"* ]]; then
    ENDPOINT="threads/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"pinterest.com"* ]]; then
    ENDPOINT="pinterest/pin?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"bsky.app"* ]]; then
    ENDPOINT="bluesky/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"truthsocial.com"* ]]; then
    ENDPOINT="truthsocial/post?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"twitch.tv"* ]]; then
    ENDPOINT="twitch/clip?url=$(echo "$URL" | jq -sRr @uri)"
elif [[ "$URL" == *"kick.com"* ]]; then
    ENDPOINT="kick/clip?url=$(echo "$URL" | jq -sRr @uri)"
else
    echo "Error: Unsupported platform"
    exit 1
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

# Output formatted content from data wrapper
echo "$RESPONSE" | jq '.data // .'
