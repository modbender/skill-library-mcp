#!/bin/bash
# Confluence page reader
# Usage: ./confluence_reader.sh <page_id_or_title>

# Source authentication
if [[ -f "../scripts/auth.sh" ]]; then
  source ../scripts/auth.sh
fi

# Check arguments
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <page_id_or_title>"
  exit 1
fi

PAGE_REF="$1"
CONFLUENCE_API_URL="https://your-domain.atlassian.net/wiki/rest/api/content/${PAGE_REF}"

# Make API request
curl -s \
  -H "Authorization: Basic ${CONFLUENCE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "${CONFLUENCE_API_URL}" | jq '.'

# Example output structure:
# {
#   "title": "Page Title",
#   "body": {"storage": {"value": "Page content"}},
#   "version": {"number": 1}
# }

# Suggested improvement: Parse content and generate actionable insights
