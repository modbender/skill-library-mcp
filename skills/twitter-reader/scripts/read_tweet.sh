#!/bin/bash
# shellcheck shell=bash

# Twitter/X Tweet Reader using FxTwitter API
# Usage: ./read_tweet.sh <tweet_url>

set -euo pipefail
trap 'echo "{\"error\": \"Script failed unexpectedly\"}" | jq .' ERR

# Check if URL is provided
if [ $# -eq 0 ]; then
    echo '{"error": "No URL provided", "usage": "./read_tweet.sh <tweet_url>"}' | jq .
    exit 1
fi

URL="$1"

# Function to extract user and tweet ID from URL
extract_tweet_info() {
    local url="$1"
    
    # Handle different URL formats
    # x.com/user/status/123456789
    # twitter.com/user/status/123456789
    # x.com/user/status/123456789?s=20
    
    if [[ "$url" =~ (x\.com|twitter\.com)/([^/]+)/status/([0-9]+) ]]; then
        local user="${BASH_REMATCH[2]}"
        local tweet_id="${BASH_REMATCH[3]}"
        echo "$user $tweet_id"
    else
        echo "ERROR ERROR"
    fi
}

# Function to format timestamp
format_timestamp() {
    local timestamp="$1"
    if command -v gdate >/dev/null 2>&1; then
        # macOS with GNU date installed via brew
        gdate -d "$timestamp" "+%Y-%m-%d %H:%M:%S UTC" 2>/dev/null || echo "$timestamp"
    elif date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        date -d "$timestamp" "+%Y-%m-%d %H:%M:%S UTC" 2>/dev/null || echo "$timestamp"
    else
        # macOS/BSD date - more limited
        echo "$timestamp"
    fi
}

# Extract user and tweet ID
tweet_info=$(extract_tweet_info "$URL")
if [[ "$tweet_info" == "ERROR ERROR" ]]; then
    echo '{"error": "Invalid Twitter/X URL format", "expected": "x.com/user/status/123456789 or twitter.com/user/status/123456789"}' | jq .
    exit 1
fi

user=$(echo "$tweet_info" | cut -d' ' -f1)
tweet_id=$(echo "$tweet_info" | cut -d' ' -f2)

# Build FxTwitter API URL
api_url="https://api.fxtwitter.com/$user/status/$tweet_id"

# Make API request
if ! response=$(curl -s -A "OpenClaw-TwitterReader/1.0" "$api_url"); then
    echo '{"error": "Failed to fetch tweet data", "details": "Network request failed"}' | jq .
    exit 1
fi

# Check if response contains an error (non-200 code)
response_code=$(echo "$response" | jq -r '.code // 0')
if [ "$response_code" != "200" ] && [ "$response_code" != "0" ]; then
    error_message=$(echo "$response" | jq -r '.message // "Unknown error"')
    jq -n --arg msg "$error_message" --argjson code "$response_code" \
        '{"error": "API Error", "code": $code, "message": $msg}'
    exit 1
fi

# Check if tweet data exists
if ! echo "$response" | jq -e '.tweet' >/dev/null 2>&1; then
    echo '{"error": "No tweet data in API response"}' | jq .
    exit 1
fi

# Extract and format tweet data
tweet_data=$(echo "$response" | jq '.tweet')

# Extract basic info + engagement + media via individual safe assignments
text=$(echo "$tweet_data" | jq -r '.text // ""' || true)
author_name=$(echo "$tweet_data" | jq -r '.author.name // ""' || true)
author_handle=$(echo "$tweet_data" | jq -r '.author.screen_name // ""' || true)
created_at=$(echo "$tweet_data" | jq -r '.created_at // ""' || true)
tweet_url=$(echo "$tweet_data" | jq -r '.url // ""' || true)
likes=$(echo "$tweet_data" | jq -r '.likes // 0' || true)
retweets=$(echo "$tweet_data" | jq -r '.retweets // 0' || true)
replies=$(echo "$tweet_data" | jq -r '.replies // 0' || true)
quotes=$(echo "$tweet_data" | jq -r '.quotes // 0' || true)
video_url=$(echo "$tweet_data" | jq -r '(.media.videos[0]?.url) // "null"' || true)
article_cover=$(echo "$tweet_data" | jq -r '(.article.cover_media.media_info.original_img_url // .article.cover_media.media_url_https // "null")' || true)

# Extract media arrays (need structured JSON output)
media_urls=$(echo "$tweet_data" | jq '[(.media.photos // [])[] | .url] // []' || echo '[]')
all_media=$(echo "$tweet_data" | jq '[(.media.all // [])[] | {type: .type, url: .url}]' || echo '[]')

# Extract quote tweet if present
quoted_tweet=null
if echo "$tweet_data" | jq -e '.quote' >/dev/null 2>&1; then
    quoted_tweet=$(echo "$tweet_data" | jq '.quote | {
        text: .text,
        author: {
            name: .author.name,
            handle: .author.screen_name
        },
        url: .url
    }')
fi

# Format timestamp
formatted_timestamp=$(format_timestamp "$created_at")

# Build final JSON response
jq -n \
    --arg text "$text" \
    --arg author_name "$author_name" \
    --arg author_handle "$author_handle" \
    --arg timestamp "$formatted_timestamp" \
    --arg original_timestamp "$created_at" \
    --arg url "$tweet_url" \
    --argjson likes "$likes" \
    --argjson retweets "$retweets" \
    --argjson replies "$replies" \
    --argjson quotes "$quotes" \
    --argjson media_photos "$media_urls" \
    --arg video_url "$video_url" \
    --argjson all_media "$all_media" \
    --arg article_cover "$article_cover" \
    --argjson quoted_tweet "$quoted_tweet" \
    '{
        "success": true,
        "tweet": {
            "text": $text,
            "author": {
                "name": $author_name,
                "handle": $author_handle
            },
            "timestamp": {
                "formatted": $timestamp,
                "original": $original_timestamp
            },
            "url": $url,
            "engagement": {
                "likes": $likes,
                "retweets": $retweets,
                "replies": $replies,
                "quotes": $quotes
            },
            "media": {
                "photos": $media_photos,
                "video": ($video_url | if . == "null" or . == "" then null else . end),
                "all": $all_media,
                "article_cover": ($article_cover | if . == "null" or . == "" then null else . end)
            },
            "quoted_tweet": $quoted_tweet
        },
        "source": "fxtwitter",
        "fetched_at": now
    }'