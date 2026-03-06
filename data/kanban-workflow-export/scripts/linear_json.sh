#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper for Kanban Workflow's LinearAdapter.
#
# This script provides a small, JSON-first CLI surface expected by the adapter:
#   - whoami
#   - issues-team <team_id>
#   - issues-project <project_id>
#   - issues-view <view_id> (best-effort; falls back to updatedAt ordering)
#
# It is intended to be used alongside the ClawHub skill `linear` (owner: ManuelHettich)
# which standardizes auth via LINEAR_API_KEY.
#
# Requirements: LINEAR_API_KEY, curl, jq

API="https://api.linear.app/graphql"

if [[ -z "${LINEAR_API_KEY:-}" ]]; then
  echo "Error: LINEAR_API_KEY not set" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl not found" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq not found" >&2
  exit 1
fi

gql() {
  local query="$1"

  # Use jq to produce a correctly escaped JSON payload.
  local payload
  payload=$(jq -cn --arg q "$query" '{query:$q}')

  curl -sS -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "Authorization: $LINEAR_API_KEY" \
    -d "$payload"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  whoami)
    gql '{ viewer { id name displayName } }'
    ;;

  issues-team)
    team_id="${1:-}"
    if [[ -z "$team_id" ]]; then
      echo "Usage: linear_json.sh issues-team <team_id>" >&2
      exit 1
    fi

    # Note: Linear's GraphQL supports querying team by ID.
    gql "{ team(id: \"$team_id\") { issues(first: 250, filter: { state: { type: { nin: [\\\"completed\\\", \\\"canceled\\\"] } } }) { nodes { id title url updatedAt state { id name type } } } } }" \
      | jq -c '{data:{issues:{nodes:(.data.team.issues.nodes // [])}}}'
    ;;

  issues-project)
    project_id="${1:-}"
    if [[ -z "$project_id" ]]; then
      echo "Usage: linear_json.sh issues-project <project_id>" >&2
      exit 1
    fi

    gql "{ project(id: \"$project_id\") { issues(first: 250, filter: { state: { type: { nin: [\\\"completed\\\", \\\"canceled\\\"] } } }) { nodes { id title url updatedAt state { id name type } } } } }" \
      | jq -c '{data:{issues:{nodes:(.data.project.issues.nodes // [])}}}'
    ;;

  issues-view)
    # Kanban Workflow historically supported an explicit view order via linear-cli.
    # The ClawHub `linear` skill does not currently expose view ordering.
    #
    # We still provide this command for compatibility, but it returns an empty list.
    # The adapter will fall back to updatedAt ordering on the team/project snapshot.
    view_id="${1:-}"
    if [[ -z "$view_id" ]]; then
      echo "Usage: linear_json.sh issues-view <view_id>" >&2
      exit 1
    fi

    jq -cn '{data:{issues:{nodes:[]}}}'
    ;;

  help|*)
    echo "linear_json.sh - JSON compatibility wrapper for Kanban Workflow" >&2
    echo "" >&2
    echo "Commands:" >&2
    echo "  whoami" >&2
    echo "  issues-team <team_id>" >&2
    echo "  issues-project <project_id>" >&2
    echo "  issues-view <view_id>" >&2
    exit 2
    ;;
esac
