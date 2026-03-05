#!/usr/bin/env bash
# bolt.sh — CLI helper for the Bolt sprint management API
#
# Usage: bolt.sh <command> [args...]
#
# Environment variables:
#   BOLT_BASE_URL   — Required. Base URL of your Bolt instance (e.g. http://localhost:3000)
#   BOLT_API_TOKEN  — Optional. API token if server was started with BOLT_API_TOKEN.
#
# Commands:
#   health                          Check server connectivity
#   projects                        List all projects
#   sprints <projectId>             List sprints for a project
#   stories [flags]                 List stories (see flags below)
#   digest sprint <sprintId>        Get sprint digest (counts, blockers, assignees)
#   digest daily <projectId>        Get daily project snapshot
#   create-story <json>             Create a story (pass JSON body)
#   move <storyId> <status>         Move story: waiting|in_progress|completed
#   patch <storyId> <json>          Update story fields (pass JSON patch)
#   note <storyId> <body>           Add a note to a story
#   label-add <storyId> <label>     Add a label to a story
#   label-rm <storyId> <label>      Remove a label from a story
#   log-event <sessionId> <msg>     Log an agent event
#   audit [projectId]               Tail the audit log

set -euo pipefail

BASE="${BOLT_BASE_URL:?BOLT_BASE_URL is required}"
BASE="${BASE%/}"  # Strip trailing slash

# Build auth header args
AUTH_ARGS=()
if [[ -n "${BOLT_API_TOKEN:-}" ]]; then
  AUTH_ARGS=(-H "x-bolt-token: $BOLT_API_TOKEN")
fi

# Wrapper: GET request
bolt_get() {
  curl -sf \
    "${AUTH_ARGS[@]}" \
    "$BASE$1"
}

# Wrapper: POST request with JSON body
bolt_post() {
  local path="$1"
  local body="${2:-{}}"
  local idem_key
  idem_key=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen 2>/dev/null || date +%s%N)
  curl -sf -X POST \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: $idem_key" \
    "${AUTH_ARGS[@]}" \
    -d "$body" \
    "$BASE$path"
}

# Wrapper: PATCH request with JSON body
bolt_patch() {
  local path="$1"
  local body="$2"
  local idem_key
  idem_key=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen 2>/dev/null || date +%s%N)
  curl -sf -X PATCH \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: $idem_key" \
    "${AUTH_ARGS[@]}" \
    -d "$body" \
    "$BASE$path"
}

CMD="${1:-help}"
shift || true

case "$CMD" in
  health)
    bolt_get "/health"
    ;;

  projects)
    bolt_get "/api/v1/projects"
    ;;

  sprints)
    PROJECT_ID="${1:?Usage: bolt.sh sprints <projectId>}"
    bolt_get "/api/v1/projects/$PROJECT_ID/sprints"
    ;;

  stories)
    # Passthrough query string: bolt.sh stories "sprintId=x&status=in_progress&fields=id,title"
    QUERY="${1:-}"
    if [[ -n "$QUERY" ]]; then
      bolt_get "/api/v1/stories?$QUERY"
    else
      bolt_get "/api/v1/stories"
    fi
    ;;

  digest)
    SUBTYPE="${1:?Usage: bolt.sh digest sprint|daily <id>}"
    ID="${2:?Missing id}"
    case "$SUBTYPE" in
      sprint)
        bolt_get "/api/v1/digests/sprint/$ID"
        ;;
      daily)
        bolt_get "/api/v1/digests/project/$ID/daily"
        ;;
      *)
        echo "Unknown digest type: $SUBTYPE. Use 'sprint' or 'daily'." >&2
        exit 1
        ;;
    esac
    ;;

  create-story)
    BODY="${1:?Usage: bolt.sh create-story '<json>'}"
    bolt_post "/api/v1/stories" "$BODY"
    ;;

  move)
    STORY_ID="${1:?Usage: bolt.sh move <storyId> <status>}"
    STATUS="${2:?Missing status: waiting|in_progress|completed}"
    bolt_post "/api/v1/stories/$STORY_ID/move" "{\"status\":\"$STATUS\"}"
    ;;

  patch)
    STORY_ID="${1:?Usage: bolt.sh patch <storyId> '<json>'}"
    BODY="${2:?Missing JSON patch body}"
    bolt_patch "/api/v1/stories/$STORY_ID" "$BODY"
    ;;

  note)
    STORY_ID="${1:?Usage: bolt.sh note <storyId> '<body>' [author] [kind]}"
    BODY="${2:?Missing note body}"
    AUTHOR="${3:-AI}"
    KIND="${4:-note}"
    bolt_post "/api/v1/stories/$STORY_ID/notes" \
      "{\"body\":$(echo "$BODY" | jq -Rs .),\"author\":\"$AUTHOR\",\"kind\":\"$KIND\"}"
    ;;

  label-add)
    STORY_ID="${1:?Usage: bolt.sh label-add <storyId> <label>}"
    LABEL="${2:?Missing label}"
    bolt_post "/api/v1/stories/$STORY_ID/labels" "{\"label\":\"$LABEL\"}"
    ;;

  label-rm)
    STORY_ID="${1:?Usage: bolt.sh label-rm <storyId> <label>}"
    LABEL="${2:?Missing label}"
    curl -sf -X DELETE \
      "${AUTH_ARGS[@]}" \
      "$BASE/api/v1/stories/$STORY_ID/labels/$LABEL"
    ;;

  log-event)
    SESSION_ID="${1:?Usage: bolt.sh log-event <sessionId> '<message>' [type]}"
    MESSAGE="${2:?Missing message}"
    TYPE="${3:-action}"
    bolt_post "/api/v1/agent/sessions/$SESSION_ID/events" \
      "{\"message\":$(echo "$MESSAGE" | jq -Rs .),\"type\":\"$TYPE\"}"
    ;;

  audit)
    PROJECT_ID="${1:-}"
    if [[ -n "$PROJECT_ID" ]]; then
      bolt_get "/api/v1/audit?projectId=$PROJECT_ID&limit=50"
    else
      bolt_get "/api/v1/audit?limit=50"
    fi
    ;;

  help|--help|-h)
    grep '^#' "$0" | sed 's/^# \?//'
    ;;

  *)
    echo "Unknown command: $CMD. Run 'bolt.sh help' for usage." >&2
    exit 1
    ;;
esac
