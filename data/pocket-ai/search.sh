#!/bin/bash
# Pocket AI Semantic Search
# Usage: ./search.sh "your query here"

API_KEY=$(cat ~/.config/pocket-ai/api_key)
QUERY="${1:-meeting}"

curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}" \
  "https://public.heypocketai.com/api/v1/public/search" | jq '.'
