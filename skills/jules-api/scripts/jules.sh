#!/usr/bin/env bash
# Jules API helper script for OpenClaw
# Usage: bash jules.sh <command> [args...]
#
# Commands:
#   sources [pageSize]                         - List connected repos
#   source <sourceId>                          - Get source details
#   create <sourceId> <branch> <prompt> [title] [--approve] [--auto-pr] - Create session
#   sessions [pageSize]                        - List sessions
#   session <sessionId>                        - Get session details
#   approve <sessionId>                        - Approve a pending plan
#   message <sessionId> <message>              - Send message to session
#   activities <sessionId> [pageSize]          - List session activities
#   activity <sessionId> <activityId>          - Get single activity
#   delete <sessionId>                         - Delete a session
#   poll <sessionId> [interval]               - Poll session until terminal state

set -euo pipefail

BASE_URL="https://jules.googleapis.com/v1alpha"

if [ -z "${JULES_API_KEY:-}" ]; then
  echo "Error: JULES_API_KEY environment variable is not set." >&2
  echo "Get your API key from https://jules.google.com/settings" >&2
  exit 1
fi

AUTH_HEADER="x-goog-api-key: $JULES_API_KEY"

# Helper: make GET request
get() {
  curl -s -H "$AUTH_HEADER" "$1"
}

# Helper: make POST request with JSON body
post() {
  curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" -d "$2" "$1"
}

# Helper: make DELETE request
delete_req() {
  curl -s -X DELETE -H "$AUTH_HEADER" "$1"
}

# Helper: pretty print JSON if jq is available
pretty() {
  if command -v jq &>/dev/null; then
    jq .
  else
    cat
  fi
}

case "${1:-help}" in

  sources)
    PAGE_SIZE="${2:-30}"
    get "$BASE_URL/sources?pageSize=$PAGE_SIZE" | pretty
    ;;

  source)
    if [ -z "${2:-}" ]; then
      echo "Usage: jules.sh source <sourceId>" >&2
      exit 1
    fi
    get "$BASE_URL/sources/$2" | pretty
    ;;

  create)
    if [ -z "${2:-}" ] || [ -z "${3:-}" ] || [ -z "${4:-}" ]; then
      echo "Usage: jules.sh create <sourceId> <branch> <prompt> [title] [--approve] [--auto-pr]" >&2
      echo "  sourceId: e.g. github-owner-repo" >&2
      echo "  branch:   e.g. main" >&2
      echo "  --approve: require plan approval (default: auto-approve)" >&2
      echo "  --auto-pr: auto-create PR when done" >&2
      exit 1
    fi
    SOURCE_ID="$2"
    BRANCH="$3"
    PROMPT="$4"
    TITLE="${5:-}"
    REQUIRE_APPROVAL="false"
    AUTOMATION_MODE=""

    shift 4
    for arg in "$@"; do
      case "$arg" in
        --approve) REQUIRE_APPROVAL="true" ;;
        --auto-pr) AUTOMATION_MODE="AUTO_CREATE_PR" ;;
        *) TITLE="$arg" ;;
      esac
    done

    # Build JSON body
    BODY="{\"prompt\":$(echo "$PROMPT" | jq -Rs .),\"sourceContext\":{\"source\":\"sources/$SOURCE_ID\",\"githubRepoContext\":{\"startingBranch\":\"$BRANCH\"}},\"requirePlanApproval\":$REQUIRE_APPROVAL"
    if [ -n "$TITLE" ] && [ "$TITLE" != "--approve" ] && [ "$TITLE" != "--auto-pr" ]; then
      BODY="$BODY,\"title\":$(echo "$TITLE" | jq -Rs .)"
    fi
    if [ -n "$AUTOMATION_MODE" ]; then
      BODY="$BODY,\"automationMode\":\"$AUTOMATION_MODE\""
    fi
    BODY="$BODY}"

    post "$BASE_URL/sessions" "$BODY" | pretty
    ;;

  sessions)
    PAGE_SIZE="${2:-30}"
    get "$BASE_URL/sessions?pageSize=$PAGE_SIZE" | pretty
    ;;

  session)
    if [ -z "${2:-}" ]; then
      echo "Usage: jules.sh session <sessionId>" >&2
      exit 1
    fi
    get "$BASE_URL/sessions/$2" | pretty
    ;;

  approve)
    if [ -z "${2:-}" ]; then
      echo "Usage: jules.sh approve <sessionId>" >&2
      exit 1
    fi
    post "$BASE_URL/sessions/$2:approvePlan" "{}" | pretty
    ;;

  message)
    if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
      echo "Usage: jules.sh message <sessionId> <message>" >&2
      exit 1
    fi
    SESSION_ID="$2"
    shift 2
    MSG="$*"
    post "$BASE_URL/sessions/$SESSION_ID:sendMessage" "{\"prompt\":$(echo "$MSG" | jq -Rs .)}" | pretty
    ;;

  activities)
    if [ -z "${2:-}" ]; then
      echo "Usage: jules.sh activities <sessionId> [pageSize]" >&2
      exit 1
    fi
    PAGE_SIZE="${3:-50}"
    get "$BASE_URL/sessions/$2/activities?pageSize=$PAGE_SIZE" | pretty
    ;;

  activity)
    if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
      echo "Usage: jules.sh activity <sessionId> <activityId>" >&2
      exit 1
    fi
    get "$BASE_URL/sessions/$2/activities/$3" | pretty
    ;;

  delete)
    if [ -z "${2:-}" ]; then
      echo "Usage: jules.sh delete <sessionId>" >&2
      exit 1
    fi
    delete_req "$BASE_URL/sessions/$2" | pretty
    ;;

  poll)
    if [ -z "${2:-}" ]; then
      echo "Usage: jules.sh poll <sessionId> [interval_seconds]" >&2
      exit 1
    fi
    SESSION_ID="$2"
    INTERVAL="${3:-10}"
    echo "Polling session $SESSION_ID every ${INTERVAL}s..."
    while true; do
      RESPONSE=$(get "$BASE_URL/sessions/$SESSION_ID")
      STATE=$(echo "$RESPONSE" | jq -r '.state // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")
      TITLE_VAL=$(echo "$RESPONSE" | jq -r '.title // "untitled"' 2>/dev/null || echo "untitled")
      echo "[$(date '+%H:%M:%S')] $TITLE_VAL — state: $STATE"

      case "$STATE" in
        COMPLETED|FAILED)
          echo ""
          echo "$RESPONSE" | pretty
          break
          ;;
        AWAITING_PLAN_APPROVAL)
          echo "  → Plan is waiting for approval. Run: jules.sh approve $SESSION_ID"
          ;;
        AWAITING_USER_FEEDBACK)
          echo "  → Jules needs your input. Run: jules.sh message $SESSION_ID \"your response\""
          ;;
      esac
      sleep "$INTERVAL"
    done
    ;;

  help|--help|-h|*)
    echo "Jules API CLI — Google Jules AI coding agent"
    echo ""
    echo "Usage: bash {baseDir}/scripts/jules.sh <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  sources [pageSize]                                          List connected repos"
    echo "  source <sourceId>                                           Get source details & branches"
    echo "  create <sourceId> <branch> <prompt> [title] [--approve] [--auto-pr]"
    echo "                                                              Create a new coding session"
    echo "  sessions [pageSize]                                         List all sessions"
    echo "  session <sessionId>                                         Get session details + outputs"
    echo "  approve <sessionId>                                         Approve a pending plan"
    echo "  message <sessionId> <message>                               Send message to active session"
    echo "  activities <sessionId> [pageSize]                           List session activities"
    echo "  activity <sessionId> <activityId>                           Get a single activity"
    echo "  delete <sessionId>                                          Delete a session"
    echo "  poll <sessionId> [interval_seconds]                         Poll until complete/failed"
    echo ""
    echo "Environment: JULES_API_KEY must be set (get it from https://jules.google.com/settings)"
    ;;
esac
