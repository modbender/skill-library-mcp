#!/bin/bash
# Jira issue reader
# Usage: ./jira_reader.sh <issue_key>

# Source authentication
if [[ -f "../scripts/auth.sh" ]]; then
  source ../scripts/auth.sh
fi

# Check arguments
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <issue_key>"
  exit 1
fi

ISSUE_KEY="$1"
JIRA_API_URL="https://your-domain.atlassian.net/rest/api/2/issue/${ISSUE_KEY}"

# Make API request
curl -s \
  -H "Authorization: Basic ${JIRA_API_TOKEN}" \
  -H "Content-Type: application/json" \
  "${JIRA_API_URL}" | jq '.'

# Example output structure:
# {
#   "key": "PROJ-123",
#   "fields": {
#     "summary": "Issue summary",
#     "status": {"name": "In Progress"},
#     "description": "Issue description"
#   }
# }

# Suggested improvement: Parse JSON and generate actionable insights
