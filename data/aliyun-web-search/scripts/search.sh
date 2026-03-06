#!/usr/bin/env bash

# Aliyun Web Search Script
# Usage: ./search.sh <query> [top_k]
# Example: ./search.sh "AI news" 5

API_KEY="${ALIYUN_SEARCH_API_KEY:-}"
BASE_URL="${ALIYUN_SEARCH_HOST:-}"

if [ -z "$API_KEY" ]; then
  echo "Error: ALIYUN_SEARCH_API_KEY environment variable is not set"
  exit 1
fi

if [ -z "$BASE_URL" ]; then
  echo "Error: ALIYUN_SEARCH_HOST environment variable is not set"
  exit 1
fi

QUERY="${1:-AI news}"
TOP_K="${2:-5}"

WORKSPACE="default"
SERVICE_ID="ops-web-search-001"

URL="${BASE_URL}/v3/openapi/workspaces/${WORKSPACE}/web-search/${SERVICE_ID}"

# Build JSON body
BODY=$(cat <<EOF
{
  "query": "$QUERY",
  "query_rewrite": true,
  "top_k": $TOP_K,
  "content_type": "snippet"
}
EOF
)

# Make request
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "$BODY"
