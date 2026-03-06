#!/usr/bin/env bash
# log-dive — Unified Log Search dispatcher
# Routes commands to the appropriate backend (Loki, Elasticsearch, CloudWatch)
# Read-only. Never modifies or deletes logs.
#
# Powered by Anvil AI 🤿
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="0.1.1"

# ─── Colors & formatting ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─── Dependency checks ─────────────────────────────────────────────────────
check_jq() {
  if ! command -v jq &>/dev/null; then
    echo '{"error":"jq is required but not found. Install: apt install jq / brew install jq","exit_code":1}' >&2
    exit 1
  fi
}

# ─── URL validation ────────────────────────────────────────────────────────
validate_url() {
  local url="$1"
  local name="$2"
  if [[ ! "$url" =~ ^https?:// ]]; then
    jq -n --arg name "$name" --arg url "$url" \
      '{"error":("\($name) URL must use http:// or https:// scheme, got: \($url)"),"exit_code":1}'
    exit 1
  fi
}

# ─── Backend detection ──────────────────────────────────────────────────────
detect_backends() {
  local loki_configured=false
  local loki_tool="none"
  local es_configured=false
  local cw_configured=false

  # Loki
  if [[ -n "${LOKI_ADDR:-}" ]]; then
    loki_configured=true
    if command -v logcli &>/dev/null; then
      loki_tool="logcli"
    elif command -v curl &>/dev/null; then
      loki_tool="curl"
    else
      loki_tool="missing"
    fi
  fi

  # Elasticsearch
  if [[ -n "${ELASTICSEARCH_URL:-}" ]]; then
    es_configured=true
  fi

  # CloudWatch
  if [[ -n "${AWS_REGION:-}" ]] && { [[ -n "${AWS_PROFILE:-}" ]] || [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; }; then
    cw_configured=true
  fi

  jq -n \
    --argjson loki_configured "$loki_configured" \
    --arg loki_addr "${LOKI_ADDR:-}" \
    --arg loki_tool "$loki_tool" \
    --argjson es_configured "$es_configured" \
    --arg es_url "${ELASTICSEARCH_URL:-}" \
    --argjson cw_configured "$cw_configured" \
    --arg aws_region "${AWS_REGION:-}" \
    --arg aws_profile "${AWS_PROFILE:-}" \
    '{
      backends: {
        loki: {
          configured: $loki_configured,
          address: $loki_addr,
          tool: $loki_tool
        },
        elasticsearch: {
          configured: $es_configured,
          url: $es_url
        },
        cloudwatch: {
          configured: $cw_configured,
          region: $aws_region,
          profile: $aws_profile
        }
      },
      configured_count: ([$loki_configured, $es_configured, $cw_configured] | map(select(. == true)) | length)
    }'
}

# ─── Parse time duration to epoch ──────────────────────────────────────────
# Converts "30m", "1h", "2d" to epoch milliseconds (for CloudWatch) or date string
duration_to_seconds() {
  local dur="${1:-1h}"
  local num="${dur%[smhd]}"
  local unit="${dur##*[0-9]}"
  case "$unit" in
    s) echo "$num" ;;
    m) echo $((num * 60)) ;;
    h) echo $((num * 3600)) ;;
    d) echo $((num * 86400)) ;;
    *) echo 3600 ;;  # default 1h
  esac
}

since_to_epoch_ms() {
  local seconds
  seconds=$(duration_to_seconds "$1")
  local now
  now=$(date +%s)
  echo $(( (now - seconds) * 1000 ))
}

since_to_iso() {
  local seconds
  seconds=$(duration_to_seconds "$1")
  local target
  target=$(( $(date +%s) - seconds ))
  date -u -d "@$target" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || \
    date -u -r "$target" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || \
    echo "now-$1"
}

since_to_es_range() {
  local dur="${1:-1h}"
  echo "now-${dur}"
}

# ─── Route search to backend ───────────────────────────────────────────────
route_search() {
  local backend="${1:-}"
  shift
  case "$backend" in
    loki)
      bash "$SCRIPT_DIR/log-dive-loki.sh" search "$@"
      ;;
    elasticsearch|es)
      bash "$SCRIPT_DIR/log-dive-es.sh" search "$@"
      ;;
    cloudwatch|cw)
      bash "$SCRIPT_DIR/log-dive-cw.sh" search "$@"
      ;;
    *)
      jq -n --arg backend "$backend" \
        '{"error":"Unknown backend: \($backend). Valid: loki, elasticsearch, cloudwatch","exit_code":1}'
      exit 1
      ;;
  esac
}

# ─── Route indices/labels to backend ───────────────────────────────────────
route_indices() {
  local backend="${1:-}"
  shift
  case "$backend" in
    loki)
      bash "$SCRIPT_DIR/log-dive-loki.sh" labels "$@"
      ;;
    elasticsearch|es)
      bash "$SCRIPT_DIR/log-dive-es.sh" indices "$@"
      ;;
    cloudwatch|cw)
      bash "$SCRIPT_DIR/log-dive-cw.sh" log-groups "$@"
      ;;
    *)
      jq -n --arg backend "$backend" \
        '{"error":"Unknown backend: \($backend). Valid: loki, elasticsearch, cloudwatch","exit_code":1}'
      exit 1
      ;;
  esac
}

# ─── Route tail to backend ─────────────────────────────────────────────────
route_tail() {
  local backend="${1:-}"
  shift
  case "$backend" in
    loki)
      bash "$SCRIPT_DIR/log-dive-loki.sh" tail "$@"
      ;;
    cloudwatch|cw)
      bash "$SCRIPT_DIR/log-dive-cw.sh" tail "$@"
      ;;
    elasticsearch|es)
      jq -n '{"error":"Elasticsearch does not support live tailing. Use search with a short time range instead.","exit_code":1}'
      exit 1
      ;;
    *)
      jq -n --arg backend "$backend" \
        '{"error":"Unknown backend: \($backend). Valid: loki, cloudwatch (ES does not support tail)","exit_code":1}'
      exit 1
      ;;
  esac
}

# ─── Auto-detect and search all backends ───────────────────────────────────
search_all() {
  local results=()
  local found=false

  if [[ -n "${LOKI_ADDR:-}" ]]; then
    found=true
    echo '{"_meta":"searching loki..."}' >&2
    bash "$SCRIPT_DIR/log-dive-loki.sh" search "$@" || true
  fi

  if [[ -n "${ELASTICSEARCH_URL:-}" ]]; then
    found=true
    echo '{"_meta":"searching elasticsearch..."}' >&2
    bash "$SCRIPT_DIR/log-dive-es.sh" search "$@" || true
  fi

  if [[ -n "${AWS_REGION:-}" ]] && { [[ -n "${AWS_PROFILE:-}" ]] || [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; }; then
    found=true
    echo '{"_meta":"searching cloudwatch..."}' >&2
    bash "$SCRIPT_DIR/log-dive-cw.sh" search "$@" || true
  fi

  if [[ "$found" == "false" ]]; then
    jq -n '{
      "error": "No backends configured. Set environment variables for at least one backend.",
      "help": {
        "loki": "export LOKI_ADDR=http://loki:3100",
        "elasticsearch": "export ELASTICSEARCH_URL=https://es:9200",
        "cloudwatch": "export AWS_REGION=us-east-1 AWS_PROFILE=myprofile"
      },
      "exit_code": 1
    }'
    exit 1
  fi
}

# ─── Usage ──────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
log-dive v${VERSION} — Unified Log Search 🤿

Usage:
  log-dive.sh <command> [options]

Commands:
  backends                           Show configured backends and status
  search  [--backend <b>] [opts]     Search logs
  indices [--backend <b>]            List indices / log groups
  labels  [--backend <b>] [--label]  List labels (Loki) or log groups (CW)
  tail    [--backend <b>] [opts]     Tail live logs (Loki, CloudWatch)

Search options:
  --backend <name>     loki | elasticsearch | cloudwatch (auto-detect if omitted)
  --query <query>      Backend-specific query string (required)
  --since <duration>   Time range: 30m, 1h, 2d (default: 1h)
  --limit <n>          Max results (default: 200)
  --index <pattern>    Elasticsearch index pattern (e.g., app-logs-*)
  --log-group <name>   CloudWatch log group name
  --label <name>       Loki label name (for labels command)

Examples:
  log-dive.sh backends
  log-dive.sh search --backend loki --query '{app="api"} |= "error"' --since 30m
  log-dive.sh search --backend elasticsearch --query '{"query":{"match":{"message":"timeout"}}}' --index 'logs-*'
  log-dive.sh search --backend cloudwatch --query '"ERROR"' --log-group /ecs/myapp
  log-dive.sh labels --backend loki
  log-dive.sh indices --backend elasticsearch
  log-dive.sh tail --backend loki --query '{app="api"}'

Powered by Anvil AI 🤿
EOF
}

# ─── Main ───────────────────────────────────────────────────────────────────
main() {
  check_jq

  if [[ $# -eq 0 ]]; then
    usage
    exit 0
  fi

  local command="$1"
  shift

  # Parse common flags
  local backend=""
  local query=""
  local since="1h"
  local limit="200"
  local index=""
  local log_group=""
  local label=""
  local args=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --backend)  backend="$2"; shift 2 ;;
      --query)    query="$2"; shift 2 ;;
      --since)    since="$2"; shift 2 ;;
      --limit)    limit="$2"; shift 2 ;;
      --index)    index="$2"; shift 2 ;;
      --log-group) log_group="$2"; shift 2 ;;
      --label)    label="$2"; shift 2 ;;
      --help|-h)  usage; exit 0 ;;
      *)          args+=("$1"); shift ;;
    esac
  done

  case "$command" in
    backends)
      detect_backends
      ;;

    search)
      if [[ -z "$query" ]]; then
        jq -n '{"error":"--query is required for search","exit_code":1}'
        exit 1
      fi

      local search_args=()
      search_args+=(--query "$query")
      search_args+=(--since "$since")
      search_args+=(--limit "$limit")
      [[ -n "$index" ]] && search_args+=(--index "$index")
      [[ -n "$log_group" ]] && search_args+=(--log-group "$log_group")

      if [[ -n "$backend" ]]; then
        route_search "$backend" "${search_args[@]}"
      else
        search_all "${search_args[@]}"
      fi
      ;;

    indices|labels)
      if [[ -n "$backend" ]]; then
        local idx_args=()
        [[ -n "$label" ]] && idx_args+=(--label "$label")
        route_indices "$backend" "${idx_args[@]}"
      else
        # Auto-detect: show all available
        if [[ -n "${LOKI_ADDR:-}" ]]; then
          echo '--- Loki Labels ---' >&2
          bash "$SCRIPT_DIR/log-dive-loki.sh" labels ${label:+--label "$label"} || true
        fi
        if [[ -n "${ELASTICSEARCH_URL:-}" ]]; then
          echo '--- Elasticsearch Indices ---' >&2
          bash "$SCRIPT_DIR/log-dive-es.sh" indices || true
        fi
        if [[ -n "${AWS_REGION:-}" ]] && { [[ -n "${AWS_PROFILE:-}" ]] || [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; }; then
          echo '--- CloudWatch Log Groups ---' >&2
          bash "$SCRIPT_DIR/log-dive-cw.sh" log-groups || true
        fi
      fi
      ;;

    tail)
      if [[ -z "$backend" ]]; then
        # Auto-detect: prefer loki, then cloudwatch
        if [[ -n "${LOKI_ADDR:-}" ]]; then
          backend="loki"
        elif [[ -n "${AWS_REGION:-}" ]]; then
          backend="cloudwatch"
        else
          jq -n '{"error":"No tail-capable backend configured. Set LOKI_ADDR or AWS_REGION.","exit_code":1}'
          exit 1
        fi
      fi

      local tail_args=()
      [[ -n "$query" ]] && tail_args+=(--query "$query")
      [[ -n "$log_group" ]] && tail_args+=(--log-group "$log_group")
      tail_args+=(--limit "$limit")
      route_tail "$backend" "${tail_args[@]}"
      ;;

    help|--help|-h)
      usage
      ;;

    version|--version|-v)
      echo "log-dive v${VERSION}"
      ;;

    *)
      jq -n --arg cmd "$command" \
        '{"error":"Unknown command: \($cmd). Run with --help for usage.","exit_code":1}'
      exit 1
      ;;
  esac
}

main "$@"
