#!/usr/bin/env bash
# Jira PAT Helper Functions
# For self-hosted Jira with SSO/SAML authentication

set -euo pipefail

# Verify required environment variables
check_env() {
  if [[ -z "${JIRA_PAT:-}" ]]; then
    echo "Error: JIRA_PAT environment variable not set" >&2
    exit 1
  fi
  if [[ -z "${JIRA_URL:-}" ]]; then
    echo "Error: JIRA_URL environment variable not set" >&2
    exit 1
  fi
}

# Get issue details
jira_get() {
  check_env
  local issue_key="$1"
  curl -s -H "Authorization: Bearer $JIRA_PAT" \
    "$JIRA_URL/rest/api/2/issue/$issue_key" | jq
}

# Get issue summary (compact view)
jira_summary() {
  check_env
  local issue_key="$1"
  curl -s -H "Authorization: Bearer $JIRA_PAT" \
    "$JIRA_URL/rest/api/2/issue/$issue_key" | \
    jq -r '"\(.key): \(.fields.summary) [\(.fields.status.name)]"'
}

# Search issues with JQL
jira_search() {
  check_env
  local jql="$1"
  curl -s -H "Authorization: Bearer $JIRA_PAT" \
    "$JIRA_URL/rest/api/2/search?jql=$jql" | \
    jq '.issues[] | "\(.key): \(.fields.summary) [\(.fields.status.name)]"' -r
}

# List epic children
jira_children() {
  check_env
  local epic_key="$1"
  curl -s -H "Authorization: Bearer $JIRA_PAT" \
    "$JIRA_URL/rest/api/2/search?jql=parent=$epic_key" | \
    jq '.issues[] | "\(.key): \(.fields.summary) [\(.fields.status.name)]"' -r
}

# Get available transitions
jira_transitions() {
  check_env
  local issue_key="$1"
  curl -s -H "Authorization: Bearer $JIRA_PAT" \
    "$JIRA_URL/rest/api/2/issue/$issue_key/transitions" | \
    jq '.transitions[] | "\(.id): \(.name)"' -r
}

# Transition an issue
jira_transition() {
  check_env
  local issue_key="$1"
  local transition_id="$2"
  local comment="${3:-}"

  local payload
  if [[ -n "$comment" ]]; then
    payload=$(jq -n --arg tid "$transition_id" --arg comment "$comment" \
      '{transition: {id: $tid}, update: {comment: [{add: {body: $comment}}]}}')
  else
    payload=$(jq -n --arg tid "$transition_id" '{transition: {id: $tid}}')
  fi

  curl -s -X POST \
    -H "Authorization: Bearer $JIRA_PAT" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$JIRA_URL/rest/api/2/issue/$issue_key/transitions"
  echo "Transitioned $issue_key"
}

# Add a comment
jira_comment() {
  check_env
  local issue_key="$1"
  local body="$2"

  curl -s -X POST \
    -H "Authorization: Bearer $JIRA_PAT" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg body "$body" '{body: $body}')" \
    "$JIRA_URL/rest/api/2/issue/$issue_key/comment" | jq
}

# Main dispatcher
case "${1:-help}" in
  get) jira_get "$2" ;;
  summary) jira_summary "$2" ;;
  search) jira_search "$2" ;;
  children) jira_children "$2" ;;
  transitions) jira_transitions "$2" ;;
  transition) jira_transition "$2" "$3" "${4:-}" ;;
  comment) jira_comment "$2" "$3" ;;
  help|*)
    cat <<EOF
Jira PAT Helper - For self-hosted Jira with SSO

Usage: jira-pat.sh <command> [args]

Commands:
  get <issue>           Get full issue details
  summary <issue>       Get compact issue summary
  search <jql>          Search with JQL query
  children <epic>       List children of an epic
  transitions <issue>   List available transitions
  transition <issue> <id> [comment]  Transition issue
  comment <issue> <body>  Add a comment

Environment:
  JIRA_PAT   Personal Access Token (required)
  JIRA_URL   Jira instance URL (required)
EOF
    ;;
esac
