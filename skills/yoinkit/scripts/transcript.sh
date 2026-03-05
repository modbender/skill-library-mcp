#!/bin/bash
# yoinkit transcript <url>
# Extract transcript from video URL

set -e

URL="$1"
shift 2>/dev/null || true

if [ -z "$URL" ]; then
    echo "Error: URL required"
    echo "Usage: yoinkit transcript <url> [--language en]"
    exit 1
fi

if [ -z "$YOINKIT_API_TOKEN" ]; then
    echo "Error: YOINKIT_API_TOKEN not configured"
    exit 1
fi

API_BASE="${YOINKIT_API_URL:-https://yoinkit.ai/api/v1/openclaw}"

# Optional parameters
LANGUAGE=""

# Parse additional options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --language)
            LANGUAGE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Normalize YouTube short URLs and youtu.be links
if [[ "$URL" == *"youtube.com/shorts/"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's|.*youtube.com/shorts/||' | sed 's|[?&].*||')
    URL="https://www.youtube.com/watch?v=$VIDEO_ID"
elif [[ "$URL" == *"youtu.be/"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's|.*youtu.be/||' | sed 's|[?&].*||')
    URL="https://www.youtube.com/watch?v=$VIDEO_ID"
fi

# Detect platform and construct endpoint
ENCODED_URL=$(echo "$URL" | jq -sRr @uri)

if [[ "$URL" == *"youtube.com"* ]] || [[ "$URL" == *"youtu.be"* ]]; then
    # Params: url (required), language
    ENDPOINT="youtube/transcript?url=$ENCODED_URL"
    [ -n "$LANGUAGE" ] && ENDPOINT+="&language=$LANGUAGE"
elif [[ "$URL" == *"tiktok.com"* ]]; then
    # Params: url (required), language, use_ai_as_fallback
    ENDPOINT="tiktok/transcript?url=$ENCODED_URL"
    [ -n "$LANGUAGE" ] && ENDPOINT+="&language=$LANGUAGE"
elif [[ "$URL" == *"instagram.com"* ]]; then
    # Params: url (required)
    ENDPOINT="instagram/transcript?url=$ENCODED_URL"
elif [[ "$URL" == *"twitter.com"* ]] || [[ "$URL" == *"x.com"* ]]; then
    # Params: url (required)
    ENDPOINT="twitter/transcript?url=$ENCODED_URL"
elif [[ "$URL" == *"facebook.com"* ]]; then
    # Params: url (required)
    ENDPOINT="facebook/transcript?url=$ENCODED_URL"
else
    echo "Error: Platform does not support transcripts or URL not recognized"
    echo "Supported: YouTube, TikTok, Instagram, Twitter/X, Facebook"
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

# Output transcript — try transcript text first, fall back to full data
echo "$RESPONSE" | jq -r '.data.transcript_only_text // .data.transcript // .data // .'
