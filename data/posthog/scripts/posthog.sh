#!/usr/bin/env bash
# posthog.sh — PostHog API helper for common operations
# Usage: bash posthog.sh <command> [args...]
#
# Required env vars:
#   POSTHOG_API_KEY      — Personal API key (for private endpoints)
#   POSTHOG_PROJECT_ID   — Project ID (from project settings)
#   POSTHOG_HOST         — API host (default: https://us.posthog.com)
#
# For public endpoints (capture/flags):
#   POSTHOG_PROJECT_API_KEY — Project API key
#   POSTHOG_INGEST_HOST     — Ingest host (default: https://us.i.posthog.com)

set -euo pipefail

HOST="${POSTHOG_HOST:-https://us.posthog.com}"
INGEST="${POSTHOG_INGEST_HOST:-https://us.i.posthog.com}"
PROJECT="${POSTHOG_PROJECT_ID:-}"
API_KEY="${POSTHOG_API_KEY:-}"
PROJECT_KEY="${POSTHOG_PROJECT_API_KEY:-}"

_auth_check() {
  if [[ -z "$API_KEY" ]]; then
    echo "Error: POSTHOG_API_KEY not set." >&2
    echo "Create at: https://us.posthog.com/settings/user-api-keys" >&2
    exit 1
  fi
  if [[ -z "$PROJECT" ]]; then
    echo "Error: POSTHOG_PROJECT_ID not set." >&2
    echo "Find at: https://us.posthog.com/settings/project#variables" >&2
    exit 1
  fi
}

_project_key_check() {
  if [[ -z "$PROJECT_KEY" ]]; then
    echo "Error: POSTHOG_PROJECT_API_KEY not set." >&2
    echo "Find at: https://us.posthog.com/settings/project" >&2
    exit 1
  fi
}

AUTH="Authorization: Bearer ${API_KEY}"
CT="Content-Type: application/json"

_get()  { curl -sf -H "$AUTH" -H "$CT" "$@"; }
_post() { curl -sf -H "$AUTH" -H "$CT" -X POST "$@"; }
_patch(){ curl -sf -H "$AUTH" -H "$CT" -X PATCH "$@"; }
_del()  { curl -sf -H "$AUTH" -H "$CT" -X DELETE "$@"; }

cmd="${1:-help}"
shift || true

case "$cmd" in

  # ── Public: Capture ──
  capture)
    _project_key_check
    [[ -z "${2:-}" ]] && { echo "Usage: posthog.sh capture <event> <distinct_id> [propertiesJson]" >&2; exit 1; }
    props="${3:-{}}"
    curl -sf -H "$CT" -X POST -d "{\"api_key\":\"$PROJECT_KEY\",\"event\":\"$1\",\"distinct_id\":\"$2\",\"properties\":$props}" "$INGEST/i/v0/e/"
    ;;

  batch)
    _project_key_check
    # Reads JSON body from stdin (must include batch array)
    echo "Wrapping with api_key..." >&2
    jq --arg key "$PROJECT_KEY" '. + {api_key: $key}' | curl -sf -H "$CT" -X POST -d @- "$INGEST/batch/"
    ;;

  # ── Public: Feature Flags ──
  evaluate-flags)
    _project_key_check
    [[ -z "${1:-}" ]] && { echo "Usage: posthog.sh evaluate-flags <distinct_id> [groupsJson]" >&2; exit 1; }
    groups="${2:-{}}"
    curl -sf -H "$CT" -X POST -d "{\"api_key\":\"$PROJECT_KEY\",\"distinct_id\":\"$1\",\"groups\":$groups}" "$INGEST/flags?v=2"
    ;;

  # ── Private: Current User ──
  whoami)
    _auth_check
    _get "$HOST/api/users/@me/"
    ;;

  # ── Private: Query (HogQL) ──
  query)
    _auth_check
    # Reads HogQL SQL from argument or stdin
    if [[ -n "${1:-}" ]]; then
      sql="$1"
      name="${2:-api_query}"
    else
      sql=$(cat)
      name="${1:-api_query}"
    fi
    _post -d "{\"query\":{\"kind\":\"HogQLQuery\",\"query\":$(echo "$sql" | jq -Rs .)},\"name\":\"$name\"}" "$HOST/api/projects/$PROJECT/query/"
    ;;

  # ── Private: Persons ──
  list-persons)
    _auth_check
    params="limit=${1:-100}"
    [[ -n "${2:-}" ]] && params="$params&search=$2"
    _get "$HOST/api/environments/$PROJECT/persons/?$params"
    ;;

  get-person)
    _auth_check
    [[ -z "${1:-}" ]] && { echo "Usage: posthog.sh get-person <person_id>" >&2; exit 1; }
    _get "$HOST/api/environments/$PROJECT/persons/$1/"
    ;;

  # ── Private: Feature Flags (CRUD) ──
  list-flags)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/feature_flags/?limit=${1:-100}"
    ;;

  get-flag)
    _auth_check
    [[ -z "${1:-}" ]] && { echo "Usage: posthog.sh get-flag <flag_id>" >&2; exit 1; }
    _get "$HOST/api/projects/$PROJECT/feature_flags/$1/"
    ;;

  create-flag)
    _auth_check
    # Reads JSON body from stdin
    _post -d @- "$HOST/api/projects/$PROJECT/feature_flags/"
    ;;

  update-flag)
    _auth_check
    [[ -z "${1:-}" ]] && { echo "Usage: echo '{...}' | posthog.sh update-flag <flag_id>" >&2; exit 1; }
    _patch -d @- "$HOST/api/projects/$PROJECT/feature_flags/$1/"
    ;;

  delete-flag)
    _auth_check
    [[ -z "${1:-}" ]] && { echo "Usage: posthog.sh delete-flag <flag_id>" >&2; exit 1; }
    _del "$HOST/api/projects/$PROJECT/feature_flags/$1/"
    ;;

  # ── Private: Insights ──
  list-insights)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/insights/?limit=${1:-100}"
    ;;

  get-insight)
    _auth_check
    [[ -z "${1:-}" ]] && { echo "Usage: posthog.sh get-insight <insight_id>" >&2; exit 1; }
    _get "$HOST/api/projects/$PROJECT/insights/$1/"
    ;;

  # ── Private: Dashboards ──
  list-dashboards)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/dashboards/?limit=${1:-100}"
    ;;

  get-dashboard)
    _auth_check
    [[ -z "${1:-}" ]] && { echo "Usage: posthog.sh get-dashboard <dashboard_id>" >&2; exit 1; }
    _get "$HOST/api/projects/$PROJECT/dashboards/$1/"
    ;;

  # ── Private: Experiments ──
  list-experiments)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/experiments/?limit=${1:-100}"
    ;;

  # ── Private: Surveys ──
  list-surveys)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/surveys/?limit=${1:-100}"
    ;;

  # ── Private: Cohorts ──
  list-cohorts)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/cohorts/?limit=${1:-100}"
    ;;

  # ── Private: Annotations ──
  list-annotations)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/annotations/?limit=${1:-100}"
    ;;

  create-annotation)
    _auth_check
    [[ -z "${2:-}" ]] && { echo "Usage: posthog.sh create-annotation <content> <date_marker_iso>" >&2; exit 1; }
    _post -d "{\"content\":\"$1\",\"date_marker\":\"$2\",\"scope\":\"organization\"}" "$HOST/api/projects/$PROJECT/annotations/"
    ;;

  # ── Private: Actions ──
  list-actions)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/actions/?limit=${1:-100}"
    ;;

  # ── Private: Session Recordings ──
  list-recordings)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/session_recordings/?limit=${1:-100}"
    ;;

  # ── Private: Event/Property Definitions ──
  list-event-definitions)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/event_definitions/?limit=${1:-100}"
    ;;

  list-property-definitions)
    _auth_check
    _get "$HOST/api/projects/$PROJECT/property_definitions/?limit=${1:-100}"
    ;;

  help|*)
    cat <<EOF
PostHog API Helper — Usage: posthog.sh <command> [args...]

Public Endpoints (POSTHOG_PROJECT_API_KEY):
  capture <event> <distinct_id> [propsJson]   Capture single event
  batch                                        Batch events (JSON from stdin)
  evaluate-flags <distinct_id> [groupsJson]    Evaluate feature flags

Private Endpoints (POSTHOG_API_KEY + POSTHOG_PROJECT_ID):
  whoami                                       Current user info

  query <sql> [name]                           HogQL query (or SQL from stdin)

  list-persons [limit] [search]                List persons
  get-person <id>                              Get person

  list-flags [limit]                           List feature flags
  get-flag <id>                                Get feature flag
  create-flag                                  Create flag (JSON from stdin)
  update-flag <id>                             Update flag (JSON from stdin)
  delete-flag <id>                             Delete flag

  list-insights [limit]                        List insights
  get-insight <id>                             Get insight

  list-dashboards [limit]                      List dashboards
  get-dashboard <id>                           Get dashboard

  list-experiments [limit]                     List experiments
  list-surveys [limit]                         List surveys
  list-cohorts [limit]                         List cohorts
  list-annotations [limit]                     List annotations
  create-annotation <text> <date_iso>          Create annotation
  list-actions [limit]                         List actions
  list-recordings [limit]                      List session recordings
  list-event-definitions [limit]               List event definitions
  list-property-definitions [limit]            List property definitions

Env vars:
  POSTHOG_API_KEY           Personal API key (private endpoints)
  POSTHOG_PROJECT_ID        Project ID
  POSTHOG_HOST              API host (default: https://us.posthog.com)
  POSTHOG_PROJECT_API_KEY   Project API key (public endpoints)
  POSTHOG_INGEST_HOST       Ingest host (default: https://us.i.posthog.com)
EOF
    ;;
esac
