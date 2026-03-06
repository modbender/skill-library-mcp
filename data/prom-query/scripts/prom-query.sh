#!/usr/bin/env bash
# prom-query.sh — Prometheus Metrics Query & Alert Interpreter
# Part of the prom-query skill for OpenClaw
# Powered by Anvil AI 📊
#
# Subcommands: query, range, alerts, targets, explore, rules
# All read-only. Never mutates Prometheus data.

set -euo pipefail

###############################################################################
# Globals
###############################################################################
VERSION="1.0.0"
SCRIPT_NAME="$(basename "$0")"
MAX_SAMPLES=500          # Downsample range queries beyond this many points
DEFAULT_STEP="15s"
DEFAULT_RANGE="1h"
CURL_TIMEOUT=30

###############################################################################
# Helpers
###############################################################################

die() {
  echo "ERROR: $*" >&2
  exit 1
}

usage() {
  cat <<EOF
prom-query v${VERSION} — Prometheus Metrics Query & Alert Interpreter

USAGE:
  ${SCRIPT_NAME} <command> [options]

COMMANDS:
  query   <promql>                     Instant query (current value)
  range   <promql> [--start=] [--end=] [--step=]  Range query (timeseries)
  alerts  [--state=firing|pending|inactive]        Active alerts
  targets [--state=active|dropped|any]             Scrape target health
  explore [pattern]                                Search available metrics
  rules   [--type=alert|record]                    Alerting & recording rules

ENVIRONMENT:
  PROMETHEUS_URL    (required) Base URL, e.g. https://prometheus.example.com
  PROMETHEUS_TOKEN  (optional) Bearer token for authentication

EXAMPLES:
  ${SCRIPT_NAME} query 'up'
  ${SCRIPT_NAME} range 'rate(http_requests_total[5m])' --start=-1h --step=1m
  ${SCRIPT_NAME} alerts
  ${SCRIPT_NAME} targets
  ${SCRIPT_NAME} explore 'http_request'
  ${SCRIPT_NAME} rules --type=alert

Powered by Anvil AI 📊
EOF
  exit 0
}

###############################################################################
# Validation
###############################################################################

validate_env() {
  if [[ -z "${PROMETHEUS_URL:-}" ]]; then
    die "PROMETHEUS_URL is not set. Set it to your Prometheus server URL, e.g.:\n  export PROMETHEUS_URL=https://prometheus.example.com\n\nCompatible with Prometheus, Thanos, Mimir, and VictoriaMetrics."
  fi

  # Strip trailing slash
  PROMETHEUS_URL="${PROMETHEUS_URL%/}"

  # Validate scheme
  case "$PROMETHEUS_URL" in
    http://*|https://*)
      ;;
    *)
      die "PROMETHEUS_URL must start with http:// or https:// (got: ${PROMETHEUS_URL})"
      ;;
  esac
}

###############################################################################
# HTTP / API helpers
###############################################################################

# Build curl auth args (never leak token to stdout)
build_auth_args() {
  local -a args=()
  if [[ -n "${PROMETHEUS_TOKEN:-}" ]]; then
    args+=(-H "Authorization: Bearer ${PROMETHEUS_TOKEN}")
  fi
  printf '%s\n' "${args[@]}"
}

# Core API call. Prints response body, exits non-zero on HTTP errors.
api_get() {
  local endpoint="$1"
  shift
  local url="${PROMETHEUS_URL}${endpoint}"

  local response
  local http_code

  # Use a temp file to capture curl stderr
  local tmp
  tmp=$(mktemp)
  trap 'rm -f "$tmp"' RETURN

  # Re-build curl args without stdin header trick for simplicity
  local -a final_args=(
    -s -S
    --connect-timeout 10
    --max-time "$CURL_TIMEOUT"
    -w '\n%{http_code}'
  )

  if [[ -n "${PROMETHEUS_TOKEN:-}" ]]; then
    final_args+=(-H "Authorization: Bearer ${PROMETHEUS_TOKEN}")
  fi

  final_args+=("$@")
  final_args+=("$url")

  if ! response=$(curl "${final_args[@]}" 2>"$tmp"); then
    local curl_err
    curl_err=$(cat "$tmp")
    die "Cannot reach Prometheus at ${PROMETHEUS_URL} — is the server running? Check PROMETHEUS_URL env var.\nCurl error: ${curl_err}"
  fi

  # Extract HTTP code from last line
  http_code=$(echo "$response" | tail -1)
  response=$(echo "$response" | sed '$d')

  if [[ "$http_code" -ge 400 ]]; then
    local api_error
    api_error=$(echo "$response" | jq -r '.error // .message // "Unknown error"' 2>/dev/null || echo "$response")
    die "Prometheus API returned HTTP ${http_code}: ${api_error}"
  fi

  # Validate response is valid JSON with status=success
  local status
  status=$(echo "$response" | jq -r '.status // empty' 2>/dev/null || true)
  if [[ "$status" == "error" ]]; then
    local error_type error_msg
    error_type=$(echo "$response" | jq -r '.errorType // "unknown"' 2>/dev/null)
    error_msg=$(echo "$response" | jq -r '.error // "unknown error"' 2>/dev/null)
    die "PromQL error (${error_type}): ${error_msg}"
  fi

  echo "$response"
}

###############################################################################
# Time helpers
###############################################################################

# Parse relative time like "-1h", "-30m", "-2d" to epoch seconds
resolve_time() {
  local input="$1"

  # If empty, return empty (let caller handle default)
  if [[ -z "$input" ]]; then
    echo ""
    return
  fi

  # If it looks like an epoch timestamp already
  if [[ "$input" =~ ^[0-9]{10}(\.[0-9]+)?$ ]]; then
    echo "$input"
    return
  fi

  # If it looks like an RFC3339 / ISO8601 date
  if [[ "$input" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
    date -d "$input" +%s 2>/dev/null || die "Cannot parse time: ${input}"
    return
  fi

  # Relative time: -1h, -30m, -2d, -1w
  if [[ "$input" =~ ^-([0-9]+)([smhdw])$ ]]; then
    local amount="${BASH_REMATCH[1]}"
    local unit="${BASH_REMATCH[2]}"
    local seconds

    case "$unit" in
      s) seconds=$((amount)) ;;
      m) seconds=$((amount * 60)) ;;
      h) seconds=$((amount * 3600)) ;;
      d) seconds=$((amount * 86400)) ;;
      w) seconds=$((amount * 604800)) ;;
    esac

    local now
    now=$(date +%s)
    echo $((now - seconds))
    return
  fi

  die "Cannot parse time '${input}'. Use relative (-1h, -30m, -2d) or absolute (epoch or ISO8601)."
}

# Parse step string to seconds for math
step_to_seconds() {
  local step="$1"
  if [[ "$step" =~ ^([0-9]+)([smhd])$ ]]; then
    local amount="${BASH_REMATCH[1]}"
    local unit="${BASH_REMATCH[2]}"
    case "$unit" in
      s) echo "$amount" ;;
      m) echo $((amount * 60)) ;;
      h) echo $((amount * 3600)) ;;
      d) echo $((amount * 86400)) ;;
    esac
  elif [[ "$step" =~ ^[0-9]+$ ]]; then
    echo "$step"
  else
    echo "15" # fallback
  fi
}

###############################################################################
# Commands
###############################################################################

cmd_query() {
  local promql="${1:-}"
  if [[ -z "$promql" ]]; then
    die "Usage: ${SCRIPT_NAME} query '<promql>'\n\nExample: ${SCRIPT_NAME} query 'up'"
  fi

  local response
  response=$(api_get "/api/v1/query" --data-urlencode "query=${promql}")

  # Format output: include the query, result type, and data
  echo "$response" | jq --arg query "$promql" '{
    command: "query",
    promql: $query,
    resultType: .data.resultType,
    resultCount: (.data.result | length),
    results: .data.result
  }'
}

cmd_range() {
  local promql=""
  local start_time=""
  local end_time=""
  local step="$DEFAULT_STEP"

  # Parse args
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --start=*) start_time="${1#--start=}" ;;
      --end=*)   end_time="${1#--end=}" ;;
      --step=*)  step="${1#--step=}" ;;
      --*)       die "Unknown option: $1" ;;
      *)
        if [[ -z "$promql" ]]; then
          promql="$1"
        else
          die "Unexpected argument: $1"
        fi
        ;;
    esac
    shift
  done

  if [[ -z "$promql" ]]; then
    die "Usage: ${SCRIPT_NAME} range '<promql>' [--start=-1h] [--end=now] [--step=15s]"
  fi

  # Resolve times
  local start_epoch end_epoch
  if [[ -z "$start_time" ]]; then
    start_epoch=$(resolve_time "-${DEFAULT_RANGE}")
  else
    start_epoch=$(resolve_time "$start_time")
  fi

  if [[ -z "$end_time" ]]; then
    end_epoch=$(date +%s)
  else
    end_epoch=$(resolve_time "$end_time")
  fi

  # Calculate expected number of points and auto-adjust step if needed
  local step_secs
  step_secs=$(step_to_seconds "$step")
  local expected_points=$(( (end_epoch - start_epoch) / step_secs ))
  local original_step="$step"
  local downsampled="false"

  if [[ "$expected_points" -gt "$MAX_SAMPLES" ]]; then
    # Auto-adjust step to keep within MAX_SAMPLES
    step_secs=$(( (end_epoch - start_epoch) / MAX_SAMPLES ))
    if [[ "$step_secs" -lt 60 ]]; then
      step="${step_secs}s"
    elif [[ "$step_secs" -lt 3600 ]]; then
      step="$(( step_secs / 60 ))m"
    elif [[ "$step_secs" -lt 86400 ]]; then
      step="$(( step_secs / 3600 ))h"
    else
      step="$(( step_secs / 86400 ))d"
    fi
    downsampled="true"
  fi

  local response
  response=$(api_get "/api/v1/query_range" \
    --data-urlencode "query=${promql}" \
    --data-urlencode "start=${start_epoch}" \
    --data-urlencode "end=${end_epoch}" \
    --data-urlencode "step=${step}")

  # Summarize each series: min, max, avg, latest, point count
  echo "$response" | jq \
    --arg query "$promql" \
    --arg step "$step" \
    --arg original_step "$original_step" \
    --argjson downsampled "$downsampled" \
    --arg range_start "$start_epoch" \
    --arg range_end "$end_epoch" \
    '{
      command: "range",
      promql: $query,
      timeRange: {
        start: ($range_start | tonumber),
        end: ($range_end | tonumber),
        step: $step,
        downsampled: $downsampled,
        originalStep: (if $downsampled then $original_step else null end)
      },
      seriesCount: (.data.result | length),
      series: [.data.result[] | {
        metric: .metric,
        pointCount: (.values | length),
        summary: {
          min: ([.values[][1] | tonumber] | min),
          max: ([.values[][1] | tonumber] | max),
          avg: (([.values[][1] | tonumber] | add) / ([.values[][1] | tonumber] | length)),
          first: (.values[0][1] | tonumber),
          last: (.values[-1][1] | tonumber),
          firstTimestamp: .values[0][0],
          lastTimestamp: .values[-1][0]
        },
        values: .values
      }]
    }'
}

cmd_alerts() {
  local state_filter=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --state=*) state_filter="${1#--state=}" ;;
      --*)       die "Unknown option: $1" ;;
      *)         die "Unexpected argument: $1" ;;
    esac
    shift
  done

  local response
  response=$(api_get "/api/v1/alerts")

  # Format and optionally filter
  if [[ -n "$state_filter" ]]; then
    echo "$response" | jq --arg state "$state_filter" '
      [.data.alerts[] | select(.state == $state)] as $filtered |
      {
        command: "alerts",
        stateFilter: $state,
        alerts: [$filtered[] | {
          alertname: .labels.alertname,
          state: .state,
          severity: ((.labels.severity) // "unknown"),
          summary: ((.annotations.summary) // (.annotations.description) // "no summary"),
          labels: .labels,
          activeAt: .activeAt,
          value: .value
        }],
        totalCount: ($filtered | length),
        bySeverity: ([$filtered[] | {sev: ((.labels.severity) // "unknown")}] | group_by(.sev) | map({
          severity: .[0].sev,
          count: length
        }))
      }'
  else
    echo "$response" | jq '
      .data.alerts as $all |
      {
        command: "alerts",
        stateFilter: "all",
        alerts: [$all[] | {
          alertname: .labels.alertname,
          state: .state,
          severity: ((.labels.severity) // "unknown"),
          summary: ((.annotations.summary) // (.annotations.description) // "no summary"),
          labels: .labels,
          activeAt: .activeAt,
          value: .value
        }],
        totalCount: ($all | length),
        byState: ($all | group_by(.state) | map({
          state: .[0].state,
          count: length
        })),
        bySeverity: ([$all[] | {sev: ((.labels.severity) // "unknown")}] | group_by(.sev) | map({
          severity: .[0].sev,
          count: length
        }))
      }'
  fi
}

cmd_targets() {
  local state_filter="any"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --state=*) state_filter="${1#--state=}" ;;
      --*)       die "Unknown option: $1" ;;
      *)         die "Unexpected argument: $1" ;;
    esac
    shift
  done

  local response
  response=$(api_get "/api/v1/targets")

  local state_arg="$state_filter"
  echo "$response" | jq --arg state "$state_arg" '{
    command: "targets",
    stateFilter: $state,
    active: (if $state == "any" or $state == "active" then
      [.data.activeTargets[] | {
        job: .labels.job,
        instance: .labels.instance,
        health: .health,
        scrapeUrl: .scrapeUrl,
        lastScrape: .lastScrape,
        lastScrapeDuration: .lastScrapeDuration,
        lastError: (if .lastError != "" then .lastError else null end)
      }]
    else [] end),
    dropped: (if $state == "any" or $state == "dropped" then
      [.data.droppedTargets[:20] | .[] | {
        job: ((.discoveredLabels.__meta_filepath) // (.discoveredLabels.job) // "unknown"),
        discoveredLabels: .discoveredLabels
      }]
    else [] end),
    summary: {
      activeTotal: (.data.activeTargets | length),
      activeUp: ([.data.activeTargets[] | select(.health == "up")] | length),
      activeDown: ([.data.activeTargets[] | select(.health == "down")] | length),
      droppedTotal: (.data.droppedTargets | length)
    }
  }'
}

cmd_explore() {
  local pattern="${1:-}"

  # Get all metric names
  local response
  response=$(api_get "/api/v1/label/__name__/values")

  if [[ -n "$pattern" ]]; then
    # Filter metric names matching the pattern (case-insensitive)
    local matching
    if ! matching=$(echo "$response" | jq --arg pat "$pattern" '[.data[] | select(test($pat; "i"))]' 2>/dev/null); then
      die "Invalid regex pattern for explore: '${pattern}'. Try a simpler pattern like 'http' or 'cpu'."
    fi

    local count
    count=$(echo "$matching" | jq 'length')

    # If reasonable count, fetch metadata for each
    if [[ "$count" -gt 0 && "$count" -le 50 ]]; then
      local metadata
      metadata=$(api_get "/api/v1/metadata")

      echo "$matching" | jq --argjson meta "$(echo "$metadata" | jq '.data')" --arg pattern "$pattern" '{
        command: "explore",
        pattern: $pattern,
        matchCount: length,
        metrics: [.[] | . as $name | {
          name: $name,
          type: ($meta[$name][0].type // "unknown"),
          help: ($meta[$name][0].help // "no description"),
          unit: ($meta[$name][0].unit // null)
        }]
      }'
    else
      echo "$matching" | jq --arg pattern "$pattern" '{
        command: "explore",
        pattern: $pattern,
        matchCount: length,
        metrics: (if length > 100 then
          { note: "Too many matches. Showing first 100. Refine your pattern.", names: .[:100] }
        else
          [.[] | { name: . }]
        end)
      }'
    fi
  else
    # No pattern: show summary of all available metrics
    echo "$response" | jq '{
      command: "explore",
      pattern: null,
      totalMetrics: (.data | length),
      note: "Pass a pattern to filter, e.g.: prom-query explore http_request",
      sampleMetrics: (.data[:30])
    }'
  fi
}

cmd_rules() {
  local type_filter=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --type=*) type_filter="${1#--type=}" ;;
      --*)      die "Unknown option: $1" ;;
      *)        die "Unexpected argument: $1" ;;
    esac
    shift
  done

  local response
  response=$(api_get "/api/v1/rules")

  if [[ -n "$type_filter" ]]; then
    echo "$response" | jq --arg type "$type_filter" '{
      command: "rules",
      typeFilter: $type,
      groups: [.data.groups[] | {
        name: .name,
        file: .file,
        rules: [.rules[] | select(.type == ($type | if . == "alert" then "alerting" else . end)) | {
          name: .name,
          type: .type,
          query: .query,
          duration: .duration,
          health: .health,
          lastEvaluation: .lastEvaluation,
          evaluationTime: .evaluationTime,
          labels: (if .labels then .labels else null end),
          annotations: (if .annotations then .annotations else null end),
          state: (if .state then .state else null end)
        }]
      } | select(.rules | length > 0)]
    }'
  else
    echo "$response" | jq '{
      command: "rules",
      typeFilter: "all",
      groups: [.data.groups[] | {
        name: .name,
        file: .file,
        interval: .interval,
        rules: [.rules[] | {
          name: .name,
          type: .type,
          query: .query,
          health: .health,
          state: (if .state then .state else null end),
          lastEvaluation: .lastEvaluation
        }]
      }],
      summary: {
        totalGroups: (.data.groups | length),
        totalAlertingRules: ([.data.groups[].rules[] | select(.type == "alerting")] | length),
        totalRecordingRules: ([.data.groups[].rules[] | select(.type == "recording")] | length)
      }
    }'
  fi
}

###############################################################################
# Main
###############################################################################

main() {
  if [[ $# -eq 0 ]]; then
    usage
  fi

  local cmd="$1"
  shift

  case "$cmd" in
    -h|--help|help)
      usage
      ;;
    -v|--version|version)
      echo "prom-query v${VERSION}"
      exit 0
      ;;
    query|range|alerts|targets|explore|rules)
      validate_env
      "cmd_${cmd}" "$@"
      ;;
    *)
      die "Unknown command: ${cmd}\nRun '${SCRIPT_NAME} --help' for usage."
      ;;
  esac
}

main "$@"
