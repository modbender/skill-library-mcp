#!/usr/bin/env bash
# log-dive Loki backend — queries via logcli or HTTP API (curl)
# Read-only. Never modifies or deletes logs.
#
# Powered by Anvil AI 🤿
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Validation ─────────────────────────────────────────────────────────────
validate_loki() {
  if [[ -z "${LOKI_ADDR:-}" ]]; then
    jq -n '{"error":"LOKI_ADDR is not set. Export it: export LOKI_ADDR=http://loki:3100","backend":"loki","exit_code":1}'
    exit 1
  fi

  # URL scheme validation
  if [[ ! "$LOKI_ADDR" =~ ^https?:// ]]; then
    jq -n --arg url "$LOKI_ADDR" \
      '{"error":"LOKI_ADDR must use http:// or https:// scheme","got":$url,"backend":"loki","exit_code":1}'
    exit 1
  fi

  if ! command -v logcli &>/dev/null && ! command -v curl &>/dev/null; then
    jq -n '{
      "error": "Neither logcli nor curl found. Install one of them.",
      "install_logcli": "https://grafana.com/docs/loki/latest/tools/logcli/",
      "install_curl": "apt install curl / brew install curl",
      "backend": "loki",
      "exit_code": 1
    }'
    exit 1
  fi
}

# ─── Helper: build curl auth headers ───────────────────────────────────────
loki_curl_headers() {
  local headers=()
  if [[ -n "${LOKI_TOKEN:-}" ]]; then
    headers+=(-H "Authorization: Bearer ${LOKI_TOKEN}")
  fi
  if [[ -n "${LOKI_TENANT_ID:-}" ]]; then
    headers+=(-H "X-Scope-OrgID: ${LOKI_TENANT_ID}")
  fi
  echo "${headers[@]:-}"
}

# ─── Helper: duration to nanoseconds for Loki API ──────────────────────────
duration_to_ns() {
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
  echo "$(( (now - seconds) * 1000000000 ))"
}

now_ns() {
  echo "$(( $(date +%s) * 1000000000 ))"
}

# ─── Search via logcli ──────────────────────────────────────────────────────
search_logcli() {
  local query="$1"
  local since="$2"
  local limit="$3"

  local logcli_args=(
    query
    "$query"
    --limit="$limit"
    --since="$since"
    --output=jsonl
    --quiet
  )

  if [[ -n "${LOKI_TENANT_ID:-}" ]]; then
    logcli_args+=(--org-id="$LOKI_TENANT_ID")
  fi

  local raw_output
  if raw_output=$(LOKI_ADDR="${LOKI_ADDR}" logcli "${logcli_args[@]}" 2>&1); then
    # Parse logcli JSONL output into a structured JSON response
    echo "$raw_output" | jq -s --arg query "$query" --arg backend "loki" --arg tool "logcli" '{
      backend: $backend,
      tool: $tool,
      query: $query,
      count: length,
      entries: [.[] | {
        timestamp: .labels.timestamp // .timestamp // .ts,
        labels: .labels,
        line: .line
      }]
    }'
  else
    jq -n --arg err "$raw_output" --arg query "$query" \
      '{"error":$err,"query":$query,"backend":"loki","tool":"logcli","exit_code":1}'
    exit 1
  fi
}

# ─── Search via HTTP API (curl) ─────────────────────────────────────────────
search_curl() {
  local query="$1"
  local since="$2"
  local limit="$3"

  local start_ns
  start_ns=$(duration_to_ns "$since")
  local end_ns
  end_ns=$(now_ns)

  local url
  url=$(jq -rn --arg addr "$LOKI_ADDR" --arg query "$query" --arg start "$start_ns" --arg end "$end_ns" --arg limit "$limit" \
    '"\($addr)/loki/api/v1/query_range?query=\($query | @uri)&start=\($start)&end=\($end)&limit=\($limit)"')

  local curl_args=(-s -S --max-time 30)

  if [[ -n "${LOKI_TOKEN:-}" ]]; then
    curl_args+=(-H "Authorization: Bearer ${LOKI_TOKEN}")
  fi
  if [[ -n "${LOKI_TENANT_ID:-}" ]]; then
    curl_args+=(-H "X-Scope-OrgID: ${LOKI_TENANT_ID}")
  fi

  local response
  if response=$(curl "${curl_args[@]}" "$url" 2>&1); then
    # Check for API error
    local status
    status=$(echo "$response" | jq -r '.status // "success"' 2>/dev/null || echo "parse_error")

    if [[ "$status" == "success" ]]; then
      # Transform Loki API response into our standard format
      echo "$response" | jq --arg query "$query" --arg backend "loki" --arg tool "curl" '{
        backend: $backend,
        tool: $tool,
        query: $query,
        status: .status,
        count: ([.data.result[]?.values[]?] | length),
        entries: [
          .data.result[] | .stream as $labels |
          .values[] | {
            timestamp: .[0],
            labels: $labels,
            line: .[1]
          }
        ] | sort_by(.timestamp) | reverse
      }'
    else
      jq -n --arg err "$response" --arg query "$query" \
        '{"error":"Loki API error","details":$err,"query":$query,"backend":"loki","tool":"curl","exit_code":1}'
      exit 1
    fi
  else
    jq -n --arg err "$response" --arg addr "$LOKI_ADDR" \
      '{"error":"Failed to connect to Loki","details":$err,"address":$addr,"backend":"loki","exit_code":1}'
    exit 1
  fi
}

# ─── Labels ─────────────────────────────────────────────────────────────────
list_labels() {
  validate_loki

  local label="${1:-}"

  if command -v logcli &>/dev/null; then
    if [[ -n "$label" ]]; then
      local raw
      raw=$(LOKI_ADDR="${LOKI_ADDR}" logcli labels "$label" --quiet 2>&1) || true
      echo "$raw" | jq -Rs --arg label "$label" '{
        backend: "loki",
        label: $label,
        values: (split("\n") | map(select(length > 0)))
      }'
    else
      local raw
      raw=$(LOKI_ADDR="${LOKI_ADDR}" logcli labels --quiet 2>&1) || true
      echo "$raw" | jq -Rs '{
        backend: "loki",
        labels: (split("\n") | map(select(length > 0)))
      }'
    fi
  else
    # Fallback to HTTP API
    local curl_args=(-s -S --max-time 15)
    if [[ -n "${LOKI_TOKEN:-}" ]]; then
      curl_args+=(-H "Authorization: Bearer ${LOKI_TOKEN}")
    fi
    if [[ -n "${LOKI_TENANT_ID:-}" ]]; then
      curl_args+=(-H "X-Scope-OrgID: ${LOKI_TENANT_ID}")
    fi

    if [[ -n "$label" ]]; then
      local response
      response=$(curl "${curl_args[@]}" "${LOKI_ADDR}/loki/api/v1/label/${label}/values" 2>&1) || true
      echo "$response" | jq --arg label "$label" '{
        backend: "loki",
        label: $label,
        values: .data
      }'
    else
      local response
      response=$(curl "${curl_args[@]}" "${LOKI_ADDR}/loki/api/v1/labels" 2>&1) || true
      echo "$response" | jq '{
        backend: "loki",
        labels: .data
      }'
    fi
  fi
}

# ─── Tail ───────────────────────────────────────────────────────────────────
tail_logs() {
  validate_loki

  local query=""
  local limit="100"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query)  query="$2"; shift 2 ;;
      --limit)  limit="$2"; shift 2 ;;
      *)        shift ;;
    esac
  done

  if [[ -z "$query" ]]; then
    jq -n '{"error":"--query is required for tail","backend":"loki","exit_code":1}'
    exit 1
  fi

  if command -v logcli &>/dev/null; then
    local logcli_args=(
      query
      "$query"
      --tail
      --limit="$limit"
      --output=jsonl
      --quiet
    )
    if [[ -n "${LOKI_TENANT_ID:-}" ]]; then
      logcli_args+=(--org-id="$LOKI_TENANT_ID")
    fi

    # Run tail with timeout (default 30s)
    LOKI_ADDR="$LOKI_ADDR" timeout 30 logcli "${logcli_args[@]}" 2>&1 | \
      head -n "$limit" | \
      jq -s --arg query "$query" '{
        backend: "loki",
        mode: "tail",
        query: $query,
        count: length,
        entries: [.[] | {timestamp: .timestamp, labels: .labels, line: .line}]
      }'
  else
    # WebSocket tail via curl is complex; fallback to polling recent
    echo '{"warning":"logcli not available for tail mode. Falling back to recent query.","backend":"loki"}' >&2
    search_curl "$query" "5m" "$limit"
  fi
}

# ─── Main ───────────────────────────────────────────────────────────────────
main() {
  local command="${1:-search}"
  shift || true

  # Parse args
  local query=""
  local since="1h"
  local limit="200"
  local label=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query)    query="$2"; shift 2 ;;
      --since)    since="$2"; shift 2 ;;
      --limit)    limit="$2"; shift 2 ;;
      --label)    label="$2"; shift 2 ;;
      *)          shift ;;
    esac
  done

  case "$command" in
    search)
      validate_loki

      if [[ -z "$query" ]]; then
        jq -n '{"error":"--query is required for search","backend":"loki","exit_code":1}'
        exit 1
      fi

      # Prefer logcli if available
      if command -v logcli &>/dev/null; then
        search_logcli "$query" "$since" "$limit"
      else
        search_curl "$query" "$since" "$limit"
      fi
      ;;

    labels)
      list_labels "$label"
      ;;

    tail)
      tail_logs --query "$query" --limit "$limit"
      ;;

    *)
      jq -n --arg cmd "$command" \
        '{"error":"Unknown Loki command: \($cmd)","backend":"loki","exit_code":1}'
      exit 1
      ;;
  esac
}

main "$@"
