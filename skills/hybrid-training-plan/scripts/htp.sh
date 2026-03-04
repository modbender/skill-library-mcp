#!/usr/bin/env bash
# htp.sh — CLI adapter for hybridtrainingplan.app API
# Requires: curl, jq
# Env vars: HYBRID_API_KEY (required), HYBRID_API_URL (optional)

set -euo pipefail

API_URL="${HYBRID_API_URL:-https://api.hybridtrainingplan.app}"
API_KEY="${HYBRID_API_KEY:?HYBRID_API_KEY must be set}"

cmd="${1:-}"
shift || true

htp_get() {
  curl -sf -H "Authorization: Bearer $API_KEY" "$API_URL$1"
}

htp_post() {
  local path="$1"
  local body="${2:-{}}"
  curl -sf -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$API_URL$path"
}

htp_put() {
  local path="$1"
  local body="${2:-{}}"
  curl -sf -X PUT \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$API_URL$path"
}

htp_patch() {
  local path="$1"
  local body="${2:-{}}"
  curl -sf -X PATCH \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$API_URL$path"
}

case "$cmd" in
  dashboard)
    htp_get "/api/users/me/dashboard" | jq .
    ;;

  day)
    # Usage: htp.sh day <date> <planId>
    date="${1:?date required (YYYY-MM-DD)}"
    plan_id="${2:?planId required}"
    # Fetch plan content and find the day
    htp_get "/api/plans/$plan_id" | jq --arg date "$date" '
      .content.weeks[]
      | .days[]
      | select(.date == $date)
    '
    ;;

  complete)
    # Usage: htp.sh complete <date> <planId>
    date="${1:?date required (YYYY-MM-DD)}"
    plan_id="${2:?planId required}"
    htp_patch "/api/plans/$plan_id/days/$date" '{"status":"completed"}' | jq .
    ;;

  skip)
    # Usage: htp.sh skip <date> <planId>
    date="${1:?date required (YYYY-MM-DD)}"
    plan_id="${2:?planId required}"
    htp_patch "/api/plans/$plan_id/days/$date" '{"status":"skipped"}' | jq .
    ;;

  log-session)
    # Usage: htp.sh log-session '<json>'
    body="${1:?JSON body required}"
    htp_put "/api/session-logs" "$body" | jq .
    ;;

  session-logs)
    # Usage: htp.sh session-logs <planId> <date>
    plan_id="${1:?planId required}"
    date="${2:?date required (YYYY-MM-DD)}"
    htp_get "/api/session-logs?planId=$plan_id&dayDate=$date" | jq .
    ;;

  maxes)
    htp_get "/api/exercise-maxes" | jq '.maxes | sort_by(.displayName)'
    ;;

  set-max)
    # Usage: htp.sh set-max "<exerciseName>" <weightKg>
    exercise_name="${1:?exercise name required}"
    weight_kg="${2:?weight in kg required}"
    body=$(jq -n --arg name "$exercise_name" --argjson kg "$weight_kg" \
      '{"displayName":$name,"oneRepMaxKg":$kg}')
    htp_post "/api/exercise-maxes" "$body" | jq .
    ;;

  *)
    echo "Usage: htp.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  dashboard                         — today's plan overview"
    echo "  day <date> <planId>               — view a day's sessions"
    echo "  complete <date> <planId>          — mark day complete"
    echo "  skip <date> <planId>              — mark day skipped"
    echo "  log-session <json>                — upsert session log"
    echo "  session-logs <planId> <date>      — get logs for a day"
    echo "  maxes                             — list exercise 1RMs"
    echo "  set-max <name> <kg>               — set/update a 1RM"
    exit 1
    ;;
esac
