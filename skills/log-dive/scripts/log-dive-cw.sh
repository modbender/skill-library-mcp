#!/usr/bin/env bash
# log-dive CloudWatch Logs backend — queries via AWS CLI
# Read-only. Never modifies or deletes logs.
#
# Powered by Anvil AI 🤿
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Validation ─────────────────────────────────────────────────────────────
validate_cw() {
  if ! command -v aws &>/dev/null; then
    jq -n '{
      "error": "AWS CLI (aws) is required but not found.",
      "install": "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
      "backend": "cloudwatch",
      "exit_code": 1
    }'
    exit 1
  fi

  if [[ -z "${AWS_REGION:-}" ]]; then
    jq -n '{"error":"AWS_REGION is not set. Export it: export AWS_REGION=us-east-1","backend":"cloudwatch","exit_code":1}'
    exit 1
  fi

  if [[ -z "${AWS_PROFILE:-}" ]] && [[ -z "${AWS_ACCESS_KEY_ID:-}" ]]; then
    jq -n '{"error":"No AWS credentials configured. Set AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY","backend":"cloudwatch","exit_code":1}'
    exit 1
  fi

  if [[ -n "${AWS_ENDPOINT_URL:-}" ]] && [[ ! "${AWS_ENDPOINT_URL}" =~ ^https?:// ]]; then
    jq -n --arg url "${AWS_ENDPOINT_URL}" \
      '{"error":"AWS_ENDPOINT_URL must use http:// or https:// scheme","got":$url,"backend":"cloudwatch","exit_code":1}'
    exit 1
  fi
}

# ─── Helper: AWS CLI with common flags ──────────────────────────────────────
aws_logs() {
  local args=("logs" "$@" --output json)

  if [[ -n "${AWS_ENDPOINT_URL:-}" ]]; then
    args+=(--endpoint-url "$AWS_ENDPOINT_URL")
  fi

  aws "${args[@]}" 2>&1
}

# ─── Helper: duration to epoch milliseconds ────────────────────────────────
duration_to_epoch_ms() {
  local dur="${1:-1h}"
  local num="${dur%[smhd]}"
  local unit="${dur##*[0-9]}"
  local seconds
  case "$unit" in
    s) seconds="$num" ;;
    m) seconds=$((num * 60)) ;;
    h) seconds=$((num * 3600)) ;;
    d) seconds=$((num * 86400)) ;;
    *) seconds=3600 ;;
  esac
  local now
  now=$(date +%s)
  echo "$(( (now - seconds) * 1000 ))"
}

now_epoch_ms() {
  echo "$(( $(date +%s) * 1000 ))"
}

# ─── Search (filter-log-events) ────────────────────────────────────────────
search() {
  validate_cw

  local query=""
  local since="1h"
  local limit="200"
  local log_group=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query)     query="$2"; shift 2 ;;
      --since)     since="$2"; shift 2 ;;
      --limit)     limit="$2"; shift 2 ;;
      --log-group) log_group="$2"; shift 2 ;;
      *)           shift ;;
    esac
  done

  if [[ -z "$query" ]]; then
    jq -n '{"error":"--query is required for search","backend":"cloudwatch","exit_code":1}'
    exit 1
  fi

  if [[ -z "$log_group" ]]; then
    jq -n '{"error":"--log-group is required for CloudWatch search. Use the indices command to list available log groups.","backend":"cloudwatch","exit_code":1}'
    exit 1
  fi

  local start_time
  start_time=$(duration_to_epoch_ms "$since")
  local end_time
  end_time=$(now_epoch_ms)

  # Cap limit at 10000 (AWS maximum)
  if [[ "$limit" -gt 10000 ]]; then
    limit=10000
  fi

  local response
  response=$(aws_logs filter-log-events \
    --log-group-name "$log_group" \
    --filter-pattern "$query" \
    --start-time "$start_time" \
    --end-time "$end_time" \
    --limit "$limit" \
    --interleaved 2>&1) || true

  # Check for errors
  if echo "$response" | jq empty 2>/dev/null; then
    # Parse and transform
    echo "$response" | jq --arg query "$query" --arg log_group "$log_group" '{
      backend: "cloudwatch",
      query: $query,
      log_group: $log_group,
      count: (.events | length),
      entries: [
        .events[] | {
          timestamp: (.timestamp / 1000 | todate),
          timestamp_ms: .timestamp,
          log_stream: .logStreamName,
          event_id: .eventId,
          line: .message
        }
      ]
    }'
  else
    # Handle AWS CLI errors
    jq -n --arg err "$response" --arg log_group "$log_group" --arg query "$query" '{
      error: "CloudWatch filter-log-events failed",
      details: $err,
      log_group: $log_group,
      query: $query,
      backend: "cloudwatch",
      exit_code: 1
    }'
    exit 1
  fi
}

# ─── List log groups ───────────────────────────────────────────────────────
list_log_groups() {
  validate_cw

  local response
  response=$(aws_logs describe-log-groups --limit 50 2>&1) || true

  if echo "$response" | jq empty 2>/dev/null; then
    echo "$response" | jq '{
      backend: "cloudwatch",
      log_groups: [
        .logGroups[] | {
          name: .logGroupName,
          stored_bytes: .storedBytes,
          retention_days: .retentionInDays,
          created: (.creationTime / 1000 | todate)
        }
      ],
      count: (.logGroups | length)
    }'
  else
    jq -n --arg err "$response" \
      '{"error":"Failed to list CloudWatch log groups","details":$err,"backend":"cloudwatch","exit_code":1}'
    exit 1
  fi
}

# ─── List log streams for a group ───────────────────────────────────────────
list_log_streams() {
  validate_cw

  local log_group="${1:-}"

  if [[ -z "$log_group" ]]; then
    jq -n '{"error":"Log group name is required. Use: --log-group <name>","backend":"cloudwatch","exit_code":1}'
    exit 1
  fi

  local response
  response=$(aws_logs describe-log-streams \
    --log-group-name "$log_group" \
    --order-by LastEventTime \
    --descending \
    --limit 50 2>&1) || true

  if echo "$response" | jq empty 2>/dev/null; then
    echo "$response" | jq --arg log_group "$log_group" '{
      backend: "cloudwatch",
      log_group: $log_group,
      streams: [
        .logStreams[] | {
          name: .logStreamName,
          last_event: (.lastEventTimestamp / 1000 | todate),
          stored_bytes: .storedBytes
        }
      ],
      count: (.logStreams | length)
    }'
  else
    jq -n --arg err "$response" --arg lg "$log_group" \
      '{"error":"Failed to list log streams","details":$err,"log_group":$lg,"backend":"cloudwatch","exit_code":1}'
    exit 1
  fi
}

# ─── Tail (get-log-events, recent) ─────────────────────────────────────────
tail_logs() {
  validate_cw

  local log_group=""
  local limit="100"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --log-group) log_group="$2"; shift 2 ;;
      --query)     shift 2 ;; # ignored for tail
      --limit)     limit="$2"; shift 2 ;;
      *)           shift ;;
    esac
  done

  if [[ -z "$log_group" ]]; then
    jq -n '{"error":"--log-group is required for CloudWatch tail","backend":"cloudwatch","exit_code":1}'
    exit 1
  fi

  # Cap limit
  if [[ "$limit" -gt 10000 ]]; then
    limit=10000
  fi

  local start_time
  start_time=$(duration_to_epoch_ms "5m")

  # Use filter-log-events with no filter to get recent events
  local response
  response=$(aws_logs filter-log-events \
    --log-group-name "$log_group" \
    --start-time "$start_time" \
    --limit "$limit" \
    --interleaved 2>&1) || true

  if echo "$response" | jq empty 2>/dev/null; then
    echo "$response" | jq --arg log_group "$log_group" '{
      backend: "cloudwatch",
      mode: "tail",
      log_group: $log_group,
      count: (.events | length),
      entries: [
        .events[] | {
          timestamp: (.timestamp / 1000 | todate),
          timestamp_ms: .timestamp,
          log_stream: .logStreamName,
          line: .message
        }
      ]
    }'
  else
    jq -n --arg err "$response" --arg lg "$log_group" \
      '{"error":"Failed to tail CloudWatch logs","details":$err,"log_group":$lg,"backend":"cloudwatch","exit_code":1}'
    exit 1
  fi
}

# ─── Main ───────────────────────────────────────────────────────────────────
main() {
  local command="${1:-search}"
  shift || true

  case "$command" in
    search)
      search "$@"
      ;;
    log-groups)
      list_log_groups
      ;;
    streams)
      local log_group=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --log-group) log_group="$2"; shift 2 ;;
          *)           shift ;;
        esac
      done
      list_log_streams "$log_group"
      ;;
    tail)
      tail_logs "$@"
      ;;
    *)
      jq -n --arg cmd "$command" \
        '{"error":"Unknown CloudWatch command: \($cmd)","backend":"cloudwatch","exit_code":1}'
      exit 1
      ;;
  esac
}

main "$@"
