#!/bin/bash
# shellcheck shell=bash

# Twitter/X Thread Reader using FxTwitter API
# Usage: ./read_thread.sh <tweet_url>
# Given any tweet in a thread, follows the reply chain to collect
# all tweets from the same author, output in chronological order.

set -euo pipefail
trap 'echo "{\"error\": \"Script failed unexpectedly\"}" | jq .' ERR

if [ $# -eq 0 ]; then
    echo '{"error": "No URL provided", "usage": "./read_thread.sh <tweet_url>"}' | jq .
    exit 1
fi

URL="$1"
MAX_DEPTH="${2:-50}"  # Safety limit on recursion

# Extract user and tweet ID from URL
extract_tweet_info() {
    local url="$1"
    if [[ "$url" =~ (x\.com|twitter\.com)/([^/]+)/status/([0-9]+) ]]; then
        echo "${BASH_REMATCH[2]} ${BASH_REMATCH[3]}"
    else
        echo "ERROR ERROR"
    fi
}

# Fetch a single tweet, return raw API JSON
fetch_tweet() {
    local user="$1"
    local tweet_id="$2"
    curl -s -A "OpenClaw-TwitterReader/1.0" "https://api.fxtwitter.com/$user/status/$tweet_id"
}

# Extract media from tweet data (comprehensive)
extract_media() {
    local tweet_data="$1"
    echo "$tweet_data" | jq '{
        photos: [(.media.photos // [])[] | .url],
        videos: [(.media.videos // [])[] | {url: .url, thumbnail: .thumbnail_url, duration: .duration}],
        all: [(.media.all // [])[] | {type: .type, url: .url}],
        article_cover: (.article.cover_media.media_url_https // null)
    }'
}

# Format a tweet into our standard output
format_tweet() {
    local tweet_data="$1"
    local media
    media=$(extract_media "$tweet_data")
    
    echo "$tweet_data" | jq --argjson media "$media" '{
        id: .id,
        text: .text,
        author: {
            name: .author.name,
            handle: .author.screen_name
        },
        created_at: .created_at,
        created_timestamp: .created_timestamp,
        url: .url,
        engagement: {
            likes: (.likes // 0),
            retweets: (.retweets // 0),
            replies: (.replies // 0)
        },
        media: $media,
        is_note_tweet: (.is_note_tweet // false),
        replying_to_status: (.replying_to.post // null)
    }'
}

# --- Main ---

tweet_info=$(extract_tweet_info "$URL")
if [[ "$tweet_info" == "ERROR ERROR" ]]; then
    echo '{"error": "Invalid Twitter/X URL format"}' | jq .
    exit 1
fi

user=$(echo "$tweet_info" | cut -d' ' -f1)
tweet_id=$(echo "$tweet_info" | cut -d' ' -f2)

# Collect tweets by walking UP the reply chain
declare -a tweets_json=()
current_user="$user"
current_id="$tweet_id"
depth=0

while [ -n "$current_id" ] && [ "$depth" -lt "$MAX_DEPTH" ]; do
    if ! response=$(fetch_tweet "$current_user" "$current_id"); then
        if [ ${#tweets_json[@]} -gt 0 ]; then
            break
        fi
        echo '{"error": "Failed to fetch tweet data"}' | jq .
        exit 1
    fi
    
    code=$(echo "$response" | jq -r '.code // 0')
    if [ "$code" != "200" ]; then
        # If we already have tweets, just stop walking
        if [ ${#tweets_json[@]} -gt 0 ]; then
            break
        fi
        jq -n --argjson code "$code" --arg tid "$current_id" \
            '{"error": "Failed to fetch tweet", "code": $code, "tweet_id": $tid}'
        exit 1
    fi
    
    tweet_data=$(echo "$response" | jq '.tweet')
    tweet_author=$(echo "$tweet_data" | jq -r '.author.screen_name // ""')
    
    # Only include tweets from the same author (thread = self-replies)
    author_lower=$(echo "$tweet_author" | tr '[:upper:]' '[:lower:]')
    user_lower=$(echo "$user" | tr '[:upper:]' '[:lower:]')
    if [ "$author_lower" = "$user_lower" ] || [ "$depth" -eq 0 ]; then
        # On first tweet, capture the canonical author handle
        if [ "$depth" -eq 0 ]; then
            user="$tweet_author"
        fi
        formatted=$(format_tweet "$tweet_data")
        tweets_json+=("$formatted")
    else
        # Hit a tweet from a different author — thread start found
        break
    fi
    
    # Walk up to parent
    parent_id=$(echo "$tweet_data" | jq -r '.replying_to.post // empty')
    parent_user=$(echo "$tweet_data" | jq -r '.replying_to.screen_name // empty')
    
    if [ -z "$parent_id" ] || [ "$parent_id" = "null" ]; then
        break
    fi
    
    current_id="$parent_id"
    current_user="${parent_user:-$user}"
    depth=$((depth + 1))
done

# Reverse to chronological order and output
count=${#tweets_json[@]}

if [ "$count" -eq 0 ]; then
    echo '{"error": "No tweets found"}' | jq .
    exit 1
fi

# Build JSON array in chronological order (reverse of collection order)
result="["
for ((i = count - 1; i >= 0; i--)); do
    result+="${tweets_json[$i]}"
    if [ "$i" -gt 0 ]; then
        result+=","
    fi
done
result+="]"

jq -n \
    --argjson tweets "$result" \
    --argjson count "$count" \
    '{
        success: true,
        thread_length: $count,
        tweets: $tweets,
        source: "fxtwitter"
    }'
