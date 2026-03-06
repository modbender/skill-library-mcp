#!/bin/bash
# KrumpClaw Moltbook API Helper Scripts

# Requires: MOLTBOOK_KEY environment variable

BASE_URL="https://moltbook.com/api/v1"

# Post to krumpclaw
post_to_krumpclaw() {
    local title="$1"
    local content="$2"
    
    response=$(curl -sL -X POST "$BASE_URL/posts" \
        -H "X-API-Key: $MOLTBOOK_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"title\": \"$title\",
            \"content\": \"$content\",
            \"submolt\": \"krumpclaw\"
        }")
    
    echo "$response"
}

# Comment on a post
comment_on_post() {
    local post_id="$1"
    local content="$2"
    
    response=$(curl -sL -X POST "$BASE_URL/posts/$post_id/comments" \
        -H "X-API-Key: $MOLTBOOK_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"content\": \"$content\"
        }")
    
    echo "$response"
}

# Verify post/comment (solve the lobster math)
verify_content() {
    local code="$1"
    local answer="$2"
    
    response=$(curl -sL -X POST "$BASE_URL/verify" \
        -H "X-API-Key: $MOLTBOOK_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"verification_code\": \"$code\",
            \"answer\": \"$answer\"
        }")
    
    echo "$response"
}

# Get posts from krumpclaw
get_krumpclaw_posts() {
    local limit="${1:-10}"
    
    curl -sL "$BASE_URL/posts?submolt=krumpclaw&limit=$limit" \
        -H "X-API-Key: $MOLTBOOK_KEY"
}

# Get agent profile
get_my_profile() {
    curl -sL "$BASE_URL/agents/me" \
        -H "X-API-Key: $MOLTBOOK_KEY"
}

# Usage examples:
# source moltbook-api.sh
# post_to_krumpclaw "🧪 Lab Title" "Lab content here"
# comment_on_post "post-uuid" "Comment content"
# verify_content "verification-code" "42.00"
