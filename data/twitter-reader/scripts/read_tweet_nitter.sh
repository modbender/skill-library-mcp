#!/bin/bash
# shellcheck shell=bash

# Twitter/X Tweet Reader using Nitter (fallback)
# Usage: ./read_tweet_nitter.sh <tweet_url>
#
# NOTE: This is a BEST-EFFORT fallback. Most public Nitter instances are
# defunct or unreliable as of 2024+. The instance list below is likely
# stale and may yield zero working results. Prefer FxTwitter API
# (read_tweet.sh) as the primary method. This script exists only as a
# last-resort option.

set -euo pipefail
trap 'echo "{\"error\": \"Script failed unexpectedly\"}" | jq .' ERR

# Check if URL is provided
if [ $# -eq 0 ]; then
    echo '{"error": "No URL provided", "usage": "./read_tweet_nitter.sh <tweet_url>"}' | jq .
    exit 1
fi

URL="$1"

# List of working Nitter instances (these may change over time)
NITTER_INSTANCES=(
    "nitter.net"
    "nitter.it"
    "nitter.unixfox.eu"
    "nitter.domain.glass"
    "nitter.ktachibana.party"
)

# Function to extract user and tweet ID from URL
extract_tweet_info() {
    local url="$1"
    
    if [[ "$url" =~ (x\.com|twitter\.com)/([^/]+)/status/([0-9]+) ]]; then
        local user="${BASH_REMATCH[2]}"
        local tweet_id="${BASH_REMATCH[3]}"
        echo "$user $tweet_id"
    else
        echo "ERROR ERROR"
    fi
}

# Function to try fetching from a Nitter instance
try_nitter_instance() {
    local instance="$1"
    local user="$2"
    local tweet_id="$3"
    
    local nitter_url="https://$instance/$user/status/$tweet_id"
    
    # Fetch the page with a timeout
    local html
    html=$(curl -s -m 10 -A "Mozilla/5.0 (compatible; OpenClaw-TwitterReader/1.0)" "$nitter_url" 2>/dev/null || echo "")
    
    if [ -z "$html" ]; then
        return 1
    fi
    
    # Check if the page loaded successfully (not blocked or error)
    if echo "$html" | grep -qi "tweet not found\|temporarily restricted\|suspended\|error"; then
        return 1
    fi
    
    # Basic extraction using grep/sed (fragile but works for basic cases)
    # This is a simplified extraction - in practice, you'd want more robust parsing
    
    local tweet_text=""
    local author_name=""
    local author_handle="$user"
    local timestamp=""
    
    # Extract tweet text (this is very basic and may need adjustment)
    tweet_text=$(echo "$html" | grep -o '<div class="tweet-content media-body"[^>]*>.*</div>' | head -1 | sed 's/<[^>]*>//g' | sed 's/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g; s/&quot;/"/g' || echo "")
    
    # Extract author name
    author_name=$(echo "$html" | grep -o '<a class="fullname"[^>]*>[^<]*</a>' | head -1 | sed 's/<[^>]*>//g' || echo "$user")
    
    # Extract timestamp (simplified)
    timestamp=$(echo "$html" | grep -o '<span class="tweet-date"[^>]*><a[^>]*title="[^"]*"' | head -1 | sed 's/.*title="\([^"]*\)".*/\1/' || echo "")
    
    if [ -n "$tweet_text" ] && [ ${#tweet_text} -gt 10 ]; then
        # Build JSON response
        jq -n \
            --arg text "$tweet_text" \
            --arg author_name "$author_name" \
            --arg author_handle "$author_handle" \
            --arg timestamp "$timestamp" \
            --arg url "https://x.com/$user/status/$tweet_id" \
            --arg instance "$instance" \
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
                        "original": $timestamp
                    },
                    "url": $url,
                    "engagement": {
                        "likes": null,
                        "retweets": null,
                        "replies": null,
                        "quotes": null
                    },
                    "media": {
                        "photos": [],
                        "video": null
                    },
                    "quoted_tweet": null
                },
                "source": "nitter",
                "instance": $instance,
                "fetched_at": now,
                "note": "Limited data extraction via Nitter - engagement stats not available"
            }'
        return 0
    fi
    
    return 1
}

# Extract user and tweet ID
tweet_info=$(extract_tweet_info "$URL")
if [[ "$tweet_info" == "ERROR ERROR" ]]; then
    echo '{"error": "Invalid Twitter/X URL format", "expected": "x.com/user/status/123456789 or twitter.com/user/status/123456789"}' | jq .
    exit 1
fi

user=$(echo "$tweet_info" | cut -d' ' -f1)
tweet_id=$(echo "$tweet_info" | cut -d' ' -f2)

# Try each Nitter instance until one works
for instance in "${NITTER_INSTANCES[@]}"; do
    echo "Trying Nitter instance: $instance" >&2
    if try_nitter_instance "$instance" "$user" "$tweet_id"; then
        exit 0
    fi
done

# If all instances failed
jq -n \
    --argjson tried_instances "$(printf '%s\n' "${NITTER_INSTANCES[@]}" | jq -R -s 'split("\n") | map(select(length > 0))')" \
    '{
        "error": "All Nitter instances failed",
        "details": "Unable to fetch tweet data from any available Nitter instance",
        "tried_instances": $tried_instances,
        "suggestion": "Try the main script with FxTwitter API, or wait for Nitter instances to recover"
    }'
exit 1