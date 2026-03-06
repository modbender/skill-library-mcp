#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# pager-triage.sh — PagerDuty Incident Triage for OpenClaw
# RUN_ID: cf_rd_20260215_2021
# Author: Anvil AI
#
# Subcommands:
#   incidents  — List active PagerDuty incidents
#   detail     — Incident deep dive (timeline, alerts, notes, log entries)
#   oncall     — On-call schedules
#   ack        — Acknowledge incident (--confirm required)
#   resolve    — Resolve incident (--confirm required)
#   note       — Add incident note (--confirm required)
#   services   — List services with status
#   recent     — Recent incident history
###############################################################################

readonly PD_API_BASE="https://api.pagerduty.com"
readonly CURL_TIMEOUT=10
readonly RETRY_DELAY=2

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

mask_key() {
  local key="${1:-}"
  if [[ ${#key} -ge 4 ]]; then
    printf '****%s' "${key: -4}"
  else
    printf '****'
  fi
}

die() {
  local msg="$1"
  jq -n --arg error "$msg" '{"error": $error}' >&2
  exit 1
}

check_deps() {
  for cmd in curl jq; do
    if ! command -v "$cmd" &>/dev/null; then
      die "Required dependency '$cmd' is not installed."
    fi
  done
}

check_api_key() {
  if [[ -z "${PAGERDUTY_API_KEY:-}" ]]; then
    die "PAGERDUTY_API_KEY is not set. Create a REST API v2 key at PagerDuty → Settings → API Access Keys, then: export PAGERDUTY_API_KEY=your_key_here"
  fi
}

check_email() {
  if [[ -z "${PAGERDUTY_EMAIL:-}" ]]; then
    die "PAGERDUTY_EMAIL is not set. Required for write operations (ack/resolve/note). Set it to your PagerDuty login email: export PAGERDUTY_EMAIL=you@company.com"
  fi
}

# pd_api METHOD PATH [DATA]
# Performs a PagerDuty API call with retry on 5xx and handles 401/403/429.
pd_api() {
  local method="$1"
  local path="$2"
  local data="${3:-}"

  local url="${PD_API_BASE}${path}"

  # Validate HTTPS scheme
  if [[ "$url" != https://* ]]; then
    die "Refusing non-HTTPS URL: $url"
  fi

  local -a curl_args=(
    -s -w '\n%{http_code}'
    --max-time "$CURL_TIMEOUT"
    -H "Authorization: Token token=${PAGERDUTY_API_KEY}"
    -H "Content-Type: application/json"
    -X "$method"
  )

  # Add From header for write operations
  if [[ "$method" != "GET" && -n "${PAGERDUTY_EMAIL:-}" ]]; then
    curl_args+=(-H "From: ${PAGERDUTY_EMAIL}")
  fi

  if [[ -n "$data" ]]; then
    curl_args+=(-d "$data")
  fi

  local response http_code body
  local attempt=0
  local max_attempts=2

  while (( attempt < max_attempts )); do
    response=$(curl "${curl_args[@]}" "$url" 2>/dev/null) || {
      if (( attempt + 1 < max_attempts )); then
        sleep "$RETRY_DELAY"
        (( attempt++ ))
        continue
      fi
      die "PagerDuty API is unreachable. Check https://status.pagerduty.com/"
    }

    # Split response into body and http_code
    http_code=$(tail -n1 <<< "$response")
    body=$(sed '$d' <<< "$response")

    case "$http_code" in
      2[0-9][0-9])
        printf '%s' "$body"
        return 0
        ;;
      401)
        die "Invalid PAGERDUTY_API_KEY ($(mask_key "${PAGERDUTY_API_KEY}")). Create a read-only API key at PagerDuty → Settings → API Access Keys."
        ;;
      403)
        die "Access denied (HTTP 403). Your API key ($(mask_key "${PAGERDUTY_API_KEY}")) lacks permission for this operation. Check your key's access level."
        ;;
      429)
        die "PagerDuty rate limit hit (HTTP 429). Wait 30 seconds and retry. PagerDuty allows 960 requests/minute."
        ;;
      5[0-9][0-9])
        if (( attempt + 1 < max_attempts )); then
          sleep "$RETRY_DELAY"
          (( attempt++ ))
          continue
        fi
        die "PagerDuty API error (HTTP $http_code). Check https://status.pagerduty.com/"
        ;;
      *)
        die "PagerDuty API returned unexpected HTTP $http_code. Check https://developer.pagerduty.com/docs/ for details."
        ;;
    esac
  done
}

# Compute duration in minutes between an ISO timestamp and now
duration_minutes_since() {
  local ts="$1"
  local now_epoch ts_epoch
  now_epoch=$(date -u +%s)
  # Portable: try GNU date first, then fallback
  ts_epoch=$(date -u -d "$ts" +%s 2>/dev/null) || ts_epoch=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts" +%s 2>/dev/null) || ts_epoch="$now_epoch"
  echo $(( (now_epoch - ts_epoch) / 60 ))
}

# Convert "24h"/"7d"/"30d" to ISO since timestamp
since_to_iso() {
  local window="${1:-24h}"
  local seconds=0
  case "$window" in
    24h) seconds=86400 ;;
    7d)  seconds=604800 ;;
    30d) seconds=2592000 ;;
    *)   seconds=86400 ;;
  esac
  local now_epoch
  now_epoch=$(date -u +%s)
  local since_epoch=$(( now_epoch - seconds ))
  date -u -d "@$since_epoch" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -r "$since_epoch" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ
}

now_iso() {
  date -u +%Y-%m-%dT%H:%M:%SZ
}

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

cmd_incidents() {
  check_api_key
  local raw
  raw=$(pd_api GET "/incidents?statuses%5B%5D=triggered&statuses%5B%5D=acknowledged&sort_by=urgency&limit=25&include%5B%5D=assignees&include%5B%5D=services")

  local timestamp
  timestamp=$(now_iso)

  printf '%s' "$raw" | jq --arg ts "$timestamp" '
    {
      tool: "pd_incidents",
      provider: "pagerduty",
      timestamp: $ts,
      total_incidents: (.incidents | length),
      incidents: [
        (.incidents // [])[] | {
          id: .id,
          incident_number: .incident_number,
          title: .title,
          status: .status,
          urgency: .urgency,
          service: {
            id: (.service.id // null),
            name: (.service.summary // null)
          },
          created_at: .created_at,
          assignments: [
            (.assignments // [])[] | {
              name: .assignee.summary,
              email: (.assignee.html_url // null)
            }
          ],
          alert_count: (.alert_counts.all // 0),
          escalation_level: (
            if (.assignments | length) > 0 then
              (.assignments[0].escalation_level // 1)
            else 1 end
          ),
          last_status_change: .last_status_change_at
        }
      ],
      summary: (
        (.incidents | length | tostring) + " active incident(s): " +
        ([ (.incidents // [])[] | .urgency + " (" + .status + ")" ] | group_by(.) | map(.[0] + " x" + (length|tostring)) | join(", "))
      )
    }
  '
}

cmd_detail() {
  check_api_key
  local incident_id="${1:-}"
  if [[ -z "$incident_id" ]]; then
    die "Usage: pager-triage detail <incident_id>"
  fi

  # Sanitize: only allow alphanumeric characters for incident ID
  if [[ ! "$incident_id" =~ ^[A-Za-z0-9]+$ ]]; then
    die "Invalid incident ID format. Expected alphanumeric, got: $incident_id"
  fi

  local incident_raw log_raw alerts_raw notes_raw

  incident_raw=$(pd_api GET "/incidents/${incident_id}?include%5B%5D=assignees&include%5B%5D=acknowledgers&include%5B%5D=conference_bridge")
  log_raw=$(pd_api GET "/incidents/${incident_id}/log_entries?limit=25&include%5B%5D=channels")
  alerts_raw=$(pd_api GET "/incidents/${incident_id}/alerts?limit=25")
  notes_raw=$(pd_api GET "/incidents/${incident_id}/notes")

  # Combine all data
  jq -n \
    --argjson incident "$incident_raw" \
    --argjson logs "$log_raw" \
    --argjson alerts "$alerts_raw" \
    --argjson notes "$notes_raw" '
    {
      tool: "pd_incident_detail",
      incident: {
        id: $incident.incident.id,
        incident_number: $incident.incident.incident_number,
        title: $incident.incident.title,
        status: $incident.incident.status,
        urgency: $incident.incident.urgency,
        service: {
          id: ($incident.incident.service.id // null),
          name: ($incident.incident.service.summary // null)
        },
        created_at: $incident.incident.created_at,
        escalation_policy: {
          id: ($incident.incident.escalation_policy.id // null),
          name: ($incident.incident.escalation_policy.summary // null)
        },
        assignments: [
          ($incident.incident.assignments // [])[] | {
            name: .assignee.summary,
            email: (.assignee.html_url // null),
            escalation_level: (.escalation_level // 1)
          }
        ],
        acknowledgers: [
          ($incident.incident.acknowledgers // [])[] | {
            name: .summary,
            at: .at
          }
        ],
        description: ($incident.incident.description // null),
        conference_bridge: ($incident.incident.conference_bridge // null)
      },
      timeline: [
        ($logs.log_entries // [])[] | {
          type: .type,
          created_at: .created_at,
          summary: (.summary // .channel.summary // ""),
          channel_type: (.channel.type // null)
        }
      ] | sort_by(.created_at),
      alerts: [
        ($alerts.alerts // [])[] | {
          id: .id,
          status: .status,
          summary: (.summary.description // .summary // null),
          severity: (.severity // null),
          created_at: .created_at,
          source: (.body.cef_details.source_location // .service.summary // null),
          details: (.body.details // {})
        }
      ],
      notes: [
        ($notes.notes // [])[] | {
          id: .id,
          content: .content,
          created_at: .created_at,
          user: (.user.summary // null)
        }
      ],
      analysis: {
        alert_count: ([$alerts.alerts // [] | length] | first),
        escalation_count: ([$logs.log_entries // [] | map(select(.type == "escalate_log_entry")) | length] | first),
        acknowledged: ($incident.incident.status == "acknowledged"),
        trigger_source: (
          [$logs.log_entries // [] | map(select(.type == "trigger_log_entry")) | first | .channel.summary // .summary // "unknown"] | first
        )
      }
    }
  '
}

cmd_oncall() {
  check_api_key
  local raw
  raw=$(pd_api GET "/oncalls?earliest=true&include%5B%5D=users&include%5B%5D=schedules&include%5B%5D=escalation_policies")

  printf '%s' "$raw" | jq '
    {
      tool: "pd_oncall",
      oncalls: [
        (.oncalls // [])[] | {
          user: {
            name: (.user.summary // null),
            email: (.user.email // null)
          },
          schedule: {
            name: (.schedule.summary // null),
            id: (.schedule.id // null)
          },
          escalation_policy: {
            name: (.escalation_policy.summary // null),
            id: (.escalation_policy.id // null)
          },
          escalation_level: .escalation_level,
          start: .start,
          end: .end
        }
      ],
      summary: (
        ((.oncalls // []) | length | tostring) + " on-call assignment(s). " +
        ([(.oncalls // [])[] | (.schedule.summary // "Unknown") + ": " + (.user.summary // "Unknown")] | unique | join(". ")) + "."
      )
    }
  '
}

cmd_ack() {
  check_api_key
  check_email
  local incident_id=""
  local confirm=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --confirm) confirm=true; shift ;;
      *) incident_id="$1"; shift ;;
    esac
  done

  if [[ -z "$incident_id" ]]; then
    die "Usage: pager-triage ack <incident_id> --confirm"
  fi

  if [[ ! "$incident_id" =~ ^[A-Za-z0-9]+$ ]]; then
    die "Invalid incident ID format. Expected alphanumeric, got: $incident_id"
  fi

  if [[ "$confirm" != "true" ]]; then
    # Fetch incident for display, then refuse
    local incident_raw
    incident_raw=$(pd_api GET "/incidents/${incident_id}?include%5B%5D=assignees&include%5B%5D=services")
    local detail
    detail=$(printf '%s' "$incident_raw" | jq '{
      id: .incident.id,
      incident_number: .incident.incident_number,
      title: .incident.title,
      service: (.incident.service.summary // "unknown"),
      urgency: .incident.urgency,
      status: .incident.status,
      alert_count: (.incident.alert_counts.all // 0)
    }')

    jq -n --argjson detail "$detail" '{
      error: "confirmation_required",
      message: "⚠️ ACKNOWLEDGE INCIDENT — --confirm flag is required to proceed.",
      incident: $detail,
      hint: "Re-run with --confirm to acknowledge this incident. This will stop escalation."
    }' >&2
    exit 1
  fi

  local payload
  payload=$(jq -n '{incident: {type: "incident_reference", status: "acknowledged"}}')

  local result
  result=$(pd_api PUT "/incidents/${incident_id}" "$payload")

  local ts
  ts=$(now_iso)

  printf '%s' "$result" | jq --arg ts "$ts" --arg email "${PAGERDUTY_EMAIL}" '{
    tool: "pd_incident_ack",
    incident_id: .incident.id,
    status: .incident.status,
    acknowledged_at: $ts,
    acknowledged_by: $email
  }'
}

cmd_resolve() {
  check_api_key
  check_email
  local incident_id=""
  local confirm=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --confirm) confirm=true; shift ;;
      *) incident_id="$1"; shift ;;
    esac
  done

  if [[ -z "$incident_id" ]]; then
    die "Usage: pager-triage resolve <incident_id> --confirm"
  fi

  if [[ ! "$incident_id" =~ ^[A-Za-z0-9]+$ ]]; then
    die "Invalid incident ID format. Expected alphanumeric, got: $incident_id"
  fi

  if [[ "$confirm" != "true" ]]; then
    local incident_raw
    incident_raw=$(pd_api GET "/incidents/${incident_id}?include%5B%5D=assignees&include%5B%5D=services")
    local detail
    detail=$(printf '%s' "$incident_raw" | jq '{
      id: .incident.id,
      incident_number: .incident.incident_number,
      title: .incident.title,
      service: (.incident.service.summary // "unknown"),
      urgency: .incident.urgency,
      status: .incident.status,
      alert_count: (.incident.alert_counts.all // 0)
    }')

    jq -n --argjson detail "$detail" '{
      error: "confirmation_required",
      message: "⚠️ RESOLVE INCIDENT — --confirm flag is required to proceed.",
      incident: $detail,
      hint: "Re-run with --confirm to resolve this incident. This marks it as fixed."
    }' >&2
    exit 1
  fi

  local payload
  payload=$(jq -n '{incident: {type: "incident_reference", status: "resolved"}}')

  local result
  result=$(pd_api PUT "/incidents/${incident_id}" "$payload")

  local ts
  ts=$(now_iso)

  printf '%s' "$result" | jq --arg ts "$ts" --arg email "${PAGERDUTY_EMAIL}" '{
    tool: "pd_incident_resolve",
    incident_id: .incident.id,
    status: .incident.status,
    resolved_at: $ts,
    resolved_by: $email
  }'
}

cmd_note() {
  check_api_key
  check_email
  local incident_id=""
  local content=""
  local confirm=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --confirm) confirm=true; shift ;;
      --content)
        if [[ $# -lt 2 ]]; then
          die "Note content is required after --content. Usage: pager-triage note <id> --content \"text\" --confirm"
        fi
        content="$2"; shift 2
        ;;
      *)
        if [[ -z "$incident_id" ]]; then
          incident_id="$1"
        elif [[ -z "$content" ]]; then
          content="$1"
        fi
        shift
        ;;
    esac
  done

  if [[ -z "$incident_id" ]]; then
    die "Usage: pager-triage note <incident_id> --content \"note text\" --confirm"
  fi

  if [[ ! "$incident_id" =~ ^[A-Za-z0-9]+$ ]]; then
    die "Invalid incident ID format. Expected alphanumeric, got: $incident_id"
  fi

  if [[ -z "$content" ]]; then
    die "Note content is required. Use --content \"your note text\""
  fi

  if [[ "$confirm" != "true" ]]; then
    jq -n --arg id "$incident_id" --arg content "$content" '{
      error: "confirmation_required",
      message: ("⚠️ ADD NOTE TO INCIDENT " + $id + " — --confirm flag is required to proceed."),
      incident_id: $id,
      note_preview: $content,
      hint: "Re-run with --confirm to add this note. Notes are permanent records on the incident."
    }' >&2
    exit 1
  fi

  local payload
  payload=$(jq -n --arg content "$content" '{note: {content: $content}}')

  local result
  result=$(pd_api POST "/incidents/${incident_id}/notes" "$payload")

  printf '%s' "$result" | jq '{
    tool: "pd_incident_note",
    incident_id: (.note.incident.id // null),
    note_id: .note.id,
    content: .note.content,
    created_at: .note.created_at,
    user: (.note.user.summary // null)
  }'
}

cmd_services() {
  check_api_key
  local raw
  raw=$(pd_api GET "/services?include%5B%5D=integrations&limit=100")

  printf '%s' "$raw" | jq '
    {
      tool: "pd_services",
      services: [
        (.services // [])[] | {
          id: .id,
          name: .name,
          status: .status,
          description: (.description // null),
          created_at: .created_at,
          escalation_policy: (.escalation_policy.summary // null),
          integrations: [(.integrations // [])[] | .summary]
        }
      ],
      summary: (
        ((.services // []) | length | tostring) + " services: " +
        ([
          (([(.services // [])[] | select(.status == "critical")] | length | tostring) + " critical"),
          (([(.services // [])[] | select(.status == "warning")] | length | tostring) + " warning"),
          (([(.services // [])[] | select(.status == "active")] | length | tostring) + " active"),
          (([(.services // [])[] | select(.status == "disabled")] | length | tostring) + " disabled")
        ] | join(", "))
      )
    }
  '
}

cmd_recent() {
  check_api_key
  local service_id=""
  local since_window="24h"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --service) service_id="${2:-}"; shift 2 ;;
      --since)   since_window="${2:-24h}"; shift 2 ;;
      *) shift ;;
    esac
  done

  local since_iso
  since_iso=$(since_to_iso "$since_window")
  local now_iso_val
  now_iso_val=$(now_iso)

  local query="since=${since_iso}&until=${now_iso_val}&limit=25&sort_by=created_at%3Adesc"
  if [[ -n "$service_id" ]]; then
    if [[ ! "$service_id" =~ ^[A-Za-z0-9]+$ ]]; then
      die "Invalid service ID format. Expected alphanumeric, got: $service_id"
    fi
    query="${query}&service_ids%5B%5D=${service_id}"
  fi

  local raw
  raw=$(pd_api GET "/incidents?${query}")

  local period_label
  case "$since_window" in
    24h) period_label="last 24 hours" ;;
    7d)  period_label="last 7 days" ;;
    30d) period_label="last 30 days" ;;
    *)   period_label="last 24 hours" ;;
  esac

  printf '%s' "$raw" | jq --arg period "$period_label" --arg svc_id "$service_id" '
    {
      tool: "pd_recent",
      period: $period,
      service: (if $svc_id != "" then $svc_id else "all" end),
      incidents: [
        (.incidents // [])[] | {
          id: .id,
          title: .title,
          status: .status,
          urgency: .urgency,
          created_at: .created_at,
          resolved_at: (.resolved_at // null),
          alert_count: (.alert_counts.all // 0)
        }
      ],
      stats: {
        total: ((.incidents // []) | length),
        by_urgency: ((.incidents // []) | group_by(.urgency) | map({(.[0].urgency): length}) | add // {}),
        by_status: ((.incidents // []) | group_by(.status) | map({(.[0].status): length}) | add // {}),
        mean_time_to_resolve_minutes: (
          [(.incidents // [])[] | select(.status == "resolved" and .resolved_at != null) |
            ((.resolved_at | sub("\\.[0-9]+"; "") | strptime("%Y-%m-%dT%H:%M:%S%Z") | mktime) -
             (.created_at | sub("\\.[0-9]+"; "") | strptime("%Y-%m-%dT%H:%M:%S%Z") | mktime)) / 60
          ] | if length > 0 then (add / length | round) else null end
        )
      }
    }
  '
}

# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

usage() {
  cat <<'EOF'
pager-triage — PagerDuty Incident Triage for OpenClaw

Usage: pager-triage <subcommand> [options]

Subcommands (read-only):
  incidents               List active incidents (triggered + acknowledged)
  detail <incident_id>    Incident deep dive (timeline, alerts, notes)
  oncall                  Show on-call schedules
  services                List services with status
  recent [--service ID] [--since 24h|7d|30d]
                          Recent incident history

Subcommands (write — require --confirm):
  ack     <incident_id> --confirm          Acknowledge incident
  resolve <incident_id> --confirm          Resolve incident
  note    <incident_id> --content "..." --confirm
                                           Add note to incident

Environment:
  PAGERDUTY_API_KEY    (required) PagerDuty REST API v2 token
  PAGERDUTY_EMAIL      (required for write ops) Your PagerDuty login email
EOF
}

main() {
  check_deps

  local subcommand="${1:-}"
  shift || true

  case "$subcommand" in
    incidents) cmd_incidents "$@" ;;
    detail)    cmd_detail "$@" ;;
    oncall)    cmd_oncall "$@" ;;
    ack)       cmd_ack "$@" ;;
    resolve)   cmd_resolve "$@" ;;
    note)      cmd_note "$@" ;;
    services)  cmd_services "$@" ;;
    recent)    cmd_recent "$@" ;;
    help|--help|-h)
      usage
      ;;
    "")
      usage >&2
      exit 1
      ;;
    *)
      die "Unknown subcommand: $subcommand. Run 'pager-triage help' for usage."
      ;;
  esac
}

main "$@"
