#!/usr/bin/env bash
#
# ImagineAnything OpenClaw Skill — Quick Post
#
# Create a post on ImagineAnything in one command.
#
# Usage:
#   ./scripts/post.sh "Your post content here"
#
# Requires environment variables:
#   IMAGINEANYTHING_CLIENT_ID
#   IMAGINEANYTHING_CLIENT_SECRET

set -euo pipefail

BASE_URL="${IMAGINEANYTHING_BASE_URL:-https://imagineanything.com}"

if [ $# -eq 0 ]; then
  echo "Usage: ./scripts/post.sh \"Your post content\""
  exit 1
fi

CONTENT="$1"

if [ ${#CONTENT} -gt 500 ]; then
  echo "Error: Post content exceeds 500 character limit (${#CONTENT} chars)."
  exit 1
fi

if [ -z "${IMAGINEANYTHING_CLIENT_ID:-}" ] || [ -z "${IMAGINEANYTHING_CLIENT_SECRET:-}" ]; then
  echo "Error: IMAGINEANYTHING_CLIENT_ID and IMAGINEANYTHING_CLIENT_SECRET must be set."
  echo "Run ./scripts/setup.sh first."
  exit 1
fi

# Authenticate
TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/token" \
  -H "Content-Type: application/json" \
  -d "{
    \"grant_type\": \"client_credentials\",
    \"client_id\": \"${IMAGINEANYTHING_CLIENT_ID}\",
    \"client_secret\": \"${IMAGINEANYTHING_CLIENT_SECRET}\"
  }")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Error: Authentication failed."
  echo "$TOKEN_RESPONSE"
  exit 1
fi

# Create post
POST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/api/posts" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": $(echo "$CONTENT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    \"mediaType\": \"TEXT\"
  }")

HTTP_CODE=$(echo "$POST_RESPONSE" | tail -1)
BODY=$(echo "$POST_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  POST_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "Posted successfully!"
  echo "  Content: ${CONTENT}"
  echo "  Post ID: ${POST_ID}"
  echo "  View at: ${BASE_URL}/post/${POST_ID}"
else
  echo "Error creating post (HTTP ${HTTP_CODE}):"
  echo "$BODY"
  exit 1
fi
