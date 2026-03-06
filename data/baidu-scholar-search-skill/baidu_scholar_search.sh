#!/bin/bash

# Baidu Scholar Search Skill Implementation
# Usage: bash baidu_scholar_search.sh "keyword" [page_number] [include_abstract]
# Example: bash baidu_scholar_search.sh "肿瘤免疫" 0 true

set -e

# Check required environment variable
if [ -z "$BAIDU_API_KEY" ]; then
    echo '{"error": "BAIDU_API_KEY environment variable not set"}'
    exit 1
fi

# Get search keyword (required)
WD="$1"
if [ -z "$WD" ]; then
    echo '{"error": "Missing search keyword parameter"}'
    exit 1
fi

# Page number (default 0, i.e., first page)
pageNum="${2:-0}"

# Include abstract (default false, not included)
enable_abstract="${3:-false}"

# Send request
curl -s -X GET \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "X-Appbuilder-From: openclaw" \
  "https://qianfan.baidubce.com/v2/tools/baidu_scholar/search?wd=$WD&pageNum=$pageNum&enable_abstract=$enable_abstract"
