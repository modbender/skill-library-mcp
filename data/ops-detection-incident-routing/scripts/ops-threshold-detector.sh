#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="ops-threshold-detector"

WORKSPACE="${PWD}/workspace"
SESSIONS_FILE=""
SESSIONS_DIR=""
CRON_RUNS_DIR=""
SNAPSHOT_FILE=""
OUTPUT_FILE=""
LOOKBACK_MIN=120
HEARTBEAT_GAP_MIN="${HEARTBEAT_GAP_MIN:-${PAYMASTER_GAP_MIN:-35}}"
CONTEXT_WARN=80
CONTEXT_HIGH=90
CONTEXT_CRIT=100
CRITICAL_JOBS="${CRITICAL_JOBS:-}"
HEARTBEAT_JOB="${HEARTBEAT_JOB:-${PAYMASTER_JOB:-}}"

usage() {
  cat <<USAGE
Usage: $SCRIPT_NAME [options]

Options:
  --workspace <dir>           Base workspace directory (default: ./workspace)
  --sessions-file <file>      Sessions mapping JSON file
  --sessions-dir <dir>        Session transcript directory
  --cron-runs-dir <dir>       Cron run logs directory
  --snapshot-file <file>      Daily snapshot JSONL file
  --output-file <file>        Detector output JSONL file
  --critical-jobs <csv>       Comma-separated job IDs/prefixes to monitor
  --heartbeat-job <id>        Job ID/prefix used for run-gap checks
  --lookback-min <n>          Lookback window for cron failure checks (default: 120)
  --heartbeat-gap-min <n>     Gap threshold in minutes (default: 35)
  --paymaster-job <id>        Deprecated alias for --heartbeat-job
  --paymaster-gap-min <n>     Deprecated alias for --heartbeat-gap-min
  --context-warn <n>          Context warning threshold (default: 80)
  --context-high <n>          Context high threshold (default: 90)
  --context-crit <n>          Context critical threshold (default: 100)
  -h, --help                  Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --sessions-file) SESSIONS_FILE="$2"; shift 2 ;;
    --sessions-dir) SESSIONS_DIR="$2"; shift 2 ;;
    --cron-runs-dir) CRON_RUNS_DIR="$2"; shift 2 ;;
    --snapshot-file) SNAPSHOT_FILE="$2"; shift 2 ;;
    --output-file) OUTPUT_FILE="$2"; shift 2 ;;
    --critical-jobs) CRITICAL_JOBS="$2"; shift 2 ;;
    --heartbeat-job|--paymaster-job) HEARTBEAT_JOB="$2"; shift 2 ;;
    --lookback-min) LOOKBACK_MIN="$2"; shift 2 ;;
    --heartbeat-gap-min|--paymaster-gap-min) HEARTBEAT_GAP_MIN="$2"; shift 2 ;;
    --context-warn) CONTEXT_WARN="$2"; shift 2 ;;
    --context-high) CONTEXT_HIGH="$2"; shift 2 ;;
    --context-crit) CONTEXT_CRIT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }
[[ "$LOOKBACK_MIN" =~ ^[0-9]+$ ]] || { echo "--lookback-min must be an integer" >&2; exit 2; }
[[ "$HEARTBEAT_GAP_MIN" =~ ^[0-9]+$ ]] || { echo "--heartbeat-gap-min must be an integer" >&2; exit 2; }
[[ "$CONTEXT_WARN" =~ ^[0-9]+$ ]] || { echo "--context-warn must be an integer" >&2; exit 2; }
[[ "$CONTEXT_HIGH" =~ ^[0-9]+$ ]] || { echo "--context-high must be an integer" >&2; exit 2; }
[[ "$CONTEXT_CRIT" =~ ^[0-9]+$ ]] || { echo "--context-crit must be an integer" >&2; exit 2; }
(( LOOKBACK_MIN > 0 )) || { echo "--lookback-min must be > 0" >&2; exit 2; }
(( HEARTBEAT_GAP_MIN > 0 )) || { echo "--heartbeat-gap-min must be > 0" >&2; exit 2; }
(( CONTEXT_WARN < CONTEXT_HIGH && CONTEXT_HIGH < CONTEXT_CRIT )) || {
  echo "context thresholds must satisfy warn < high < crit" >&2
  exit 2
}

SESSIONS_FILE="${SESSIONS_FILE:-$WORKSPACE/sessions/sessions.json}"
SESSIONS_DIR="${SESSIONS_DIR:-$(dirname "$SESSIONS_FILE")}"
CRON_RUNS_DIR="${CRON_RUNS_DIR:-$WORKSPACE/cron/runs}"
SNAPSHOT_FILE="${SNAPSHOT_FILE:-$WORKSPACE/metrics/daily-snapshots.jsonl}"
OUTPUT_FILE="${OUTPUT_FILE:-$WORKSPACE/metrics/ops-detector.jsonl}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

LOCK_FILE="${OUTPUT_FILE}.lock"
if command -v flock >/dev/null 2>&1; then
  exec 200>"$LOCK_FILE"
  if ! flock -n 200; then
    echo "another detector run is active" >&2
    exit 0
  fi
else
  # Portable fallback for systems without flock (for example macOS).
  LOCK_DIR="${LOCK_FILE}.d"
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "another detector run is active" >&2
    exit 0
  fi
  trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
fi

alerts='[]'
gaps='[]'
checks=0

append_alert() {
  local sev="$1" trigger="$2" value="$3" threshold="$4" job="${5:-}"
  if [[ -n "$job" ]]; then
    alerts=$(jq -c --arg sev "$sev" --arg trigger "$trigger" --arg job "$job" --argjson value "$value" --argjson threshold "$threshold" '. + [{"sev":$sev,"trigger":$trigger,"value":$value,"threshold":$threshold,"job":$job}]' <<<"$alerts")
  else
    alerts=$(jq -c --arg sev "$sev" --arg trigger "$trigger" --argjson value "$value" --argjson threshold "$threshold" '. + [{"sev":$sev,"trigger":$trigger,"value":$value,"threshold":$threshold}]' <<<"$alerts")
  fi
}

append_gap() {
  local trigger="$1" reason="$2"
  gaps=$(jq -c --arg trigger "$trigger" --arg reason "$reason" '. + [{"trigger":$trigger,"reason":$reason}]' <<<"$gaps")
}

# Guard against path traversal when IDs are used as path components.
is_safe_path_token() {
  local token="$1"
  [[ -n "$token" ]] || return 1
  [[ "$token" =~ ^[A-Za-z0-9._:-]+$ ]] || return 1
  [[ "$token" != *..* ]] || return 1
  [[ "$token" != */* ]] || return 1
  [[ "$token" != *\\* ]] || return 1
  return 0
}

# 1) Cron failures for critical jobs.
checks=$((checks + 1))
if [[ -n "$CRITICAL_JOBS" ]]; then
  cutoff_ms=$(( ( $(date +%s) - (LOOKBACK_MIN * 60) ) * 1000 ))
  IFS=',' read -r -a critical_list <<<"$CRITICAL_JOBS"
  shopt -s nullglob
  for raw_job in "${critical_list[@]}"; do
    job="$(echo "$raw_job" | xargs)"
    [[ -z "$job" ]] && continue
    if ! is_safe_path_token "$job"; then
      append_gap "cron_failure" "invalid_job_id"
      continue
    fi
    files=("$CRON_RUNS_DIR/${job}"*.jsonl)
    if (( ${#files[@]} == 0 )); then
      append_gap "cron_failure" "no_run_log_for_${job}"
      continue
    fi
    failures=$(cat "${files[@]}" 2>/dev/null | jq -r --argjson cutoff "$cutoff_ms" 'select((.action//"")=="finished" and (.status//"ok")!="ok" and (.ts//0) >= $cutoff) | 1' | wc -l | tr -d ' ')
    if [[ "$failures" =~ ^[0-9]+$ ]] && (( failures > 0 )); then
      append_alert "Sev-2" "cron_failure" "$failures" 0 "$job"
    fi
  done
  shopt -u nullglob
fi

# 2) Heartbeat/job run gap.
checks=$((checks + 1))
if [[ -n "$HEARTBEAT_JOB" ]]; then
  if ! is_safe_path_token "$HEARTBEAT_JOB"; then
    append_gap "heartbeat_gap" "invalid_job_id"
  else
    shopt -s nullglob
    pfiles=("$CRON_RUNS_DIR/${HEARTBEAT_JOB}"*.jsonl)
    shopt -u nullglob
    if (( ${#pfiles[@]} > 0 )); then
      run_times="$(cat "${pfiles[@]}" 2>/dev/null | jq -r 'select((.action//"")=="finished") | (.runAtMs // .ts // empty)' | sort -n | tail -2)"
      run_prev="$(printf '%s\n' "$run_times" | sed -n '1p')"
      run_cur="$(printf '%s\n' "$run_times" | sed -n '2p')"
      if [[ "$run_prev" =~ ^[0-9]+$ ]] && [[ "$run_cur" =~ ^[0-9]+$ ]]; then
        gap_ms=$(( run_cur - run_prev ))
        gap_min=$(( gap_ms / 60000 ))
        if (( gap_min > HEARTBEAT_GAP_MIN )); then
          append_alert "Sev-2" "heartbeat_gap" "$gap_min" "$HEARTBEAT_GAP_MIN" "$HEARTBEAT_JOB"
        fi
      fi
    else
      append_gap "heartbeat_gap" "no_run_log_for_${HEARTBEAT_JOB}"
    fi
  fi
fi

# 3) Context pressure.
checks=$((checks + 1))
if [[ -f "$SESSIONS_FILE" ]]; then
  warn_ratio="$(jq -n --argjson v "$CONTEXT_WARN" '$v / 100')"
  high_ratio="$(jq -n --argjson v "$CONTEXT_HIGH" '$v / 100')"
  crit_ratio="$(jq -n --argjson v "$CONTEXT_CRIT" '$v / 100')"

  context_crit_count=$(jq -r --argjson crit "$crit_ratio" '[to_entries[] | select((.value.contextTokens//0) > 0) | ((.value.totalTokens//0) / (.value.contextTokens//1)) | select(. >= $crit)] | length' "$SESSIONS_FILE" 2>/dev/null || echo 0)
  context_high_count=$(jq -r --argjson high "$high_ratio" --argjson crit "$crit_ratio" '[to_entries[] | select((.value.contextTokens//0) > 0) | ((.value.totalTokens//0) / (.value.contextTokens//1)) | select(. >= $high and . < $crit)] | length' "$SESSIONS_FILE" 2>/dev/null || echo 0)
  context_warn_count=$(jq -r --argjson warn "$warn_ratio" --argjson high "$high_ratio" '[to_entries[] | select((.value.contextTokens//0) > 0) | ((.value.totalTokens//0) / (.value.contextTokens//1)) | select(. >= $warn and . < $high)] | length' "$SESSIONS_FILE" 2>/dev/null || echo 0)

  (( context_warn_count > 0 )) && append_alert "Sev-3" "context_warn" "$context_warn_count" "$CONTEXT_WARN"
  (( context_high_count > 0 )) && append_alert "Sev-2" "context_high" "$context_high_count" "$CONTEXT_HIGH"
  (( context_crit_count > 0 )) && append_alert "Sev-2" "context_crit" "$context_crit_count" "$CONTEXT_CRIT"
else
  append_gap "context_scan" "sessions_file_missing"
fi

# 4) Dangling sessions.
checks=$((checks + 1))
if [[ -f "$SESSIONS_FILE" ]]; then
  dangling=0
  while IFS= read -r sid; do
    [[ -z "$sid" ]] && continue
    if ! is_safe_path_token "$sid"; then
      append_gap "dangling_sessions" "invalid_session_id"
      continue
    fi
    if [[ ! -f "$SESSIONS_DIR/${sid}.jsonl" ]]; then
      dangling=$((dangling + 1))
    fi
  done < <(jq -r '.[].sessionId // empty' "$SESSIONS_FILE" 2>/dev/null)

  (( dangling > 0 )) && append_alert "Sev-2" "dangling_sessions" "$dangling" 0
fi

# 5) Token spike against previous snapshot.
checks=$((checks + 1))
if [[ -f "$SNAPSHOT_FILE" ]]; then
  lines=$(wc -l < "$SNAPSHOT_FILE" | tr -d ' ')
  if [[ "$lines" =~ ^[0-9]+$ ]] && (( lines >= 2 )); then
    prev=$(tail -2 "$SNAPSHOT_FILE" | head -1 | jq -r '.totalTokensUsed // .tokens // 0' 2>/dev/null || echo 0)
    cur=$(tail -1 "$SNAPSHOT_FILE" | jq -r '.totalTokensUsed // .tokens // 0' 2>/dev/null || echo 0)
    if [[ "$prev" =~ ^[0-9]+$ ]] && [[ "$cur" =~ ^[0-9]+$ ]] && (( prev > 0 )) && (( cur > prev * 2 )); then
      append_alert "Sev-3" "token_spike" "$cur" "$(( prev * 2 ))"
    fi
  fi
else
  append_gap "token_spike" "snapshot_file_missing"
fi

alerts_count=$(jq -r 'length' <<<"$alerts")
status="OK"
if (( alerts_count > 0 )); then
  status="ALERT"
fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
result=$(jq -cn \
  --arg ts "$ts" \
  --arg status "$status" \
  --argjson checks "$checks" \
  --argjson alerts "$alerts" \
  --argjson gaps "$gaps" \
  '{ts:$ts,status:$status,checks:$checks,alerts:$alerts,gaps:$gaps}')

echo "$result" >> "$OUTPUT_FILE"
echo "$result"
