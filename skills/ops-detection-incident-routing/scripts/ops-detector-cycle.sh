#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${PWD}/workspace"
STATE_FILE="./incident-state.json"
DETECTOR_OUT="${PWD}/ops-detector.jsonl"
ROUTER_OUT="${PWD}/router-actions.jsonl"
LIVE=false
CRITICAL_JOBS="${CRITICAL_JOBS:-}"
HEARTBEAT_JOB="${HEARTBEAT_JOB:-${PAYMASTER_JOB:-}}"

usage() {
  cat <<USAGE
Usage: ops-detector-cycle.sh [options]

Options:
  --workspace <dir>      Base workspace directory (default: ./workspace)
  --state-file <file>    Incident state file path (default: ./incident-state.json)
  --detector-out <file>  Detector JSONL output path
  --router-out <file>    Router JSONL output path
  --critical-jobs <csv>  Comma-separated job IDs/prefixes for failure detection
  --heartbeat-job <id>   Job ID/prefix for run-gap checks
  --paymaster-job <id>   Deprecated alias for --heartbeat-job
  --live                 Router runs in live mode (acquires in-flight lock)
  --dry-run              Router runs in dry-run mode (default)
  -h, --help             Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --state-file) STATE_FILE="$2"; shift 2 ;;
    --detector-out) DETECTOR_OUT="$2"; shift 2 ;;
    --router-out) ROUTER_OUT="$2"; shift 2 ;;
    --critical-jobs) CRITICAL_JOBS="$2"; shift 2 ;;
    --heartbeat-job|--paymaster-job) HEARTBEAT_JOB="$2"; shift 2 ;;
    --live) LIVE=true; shift ;;
    --dry-run) LIVE=false; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }

mkdir -p "$(dirname "$DETECTOR_OUT")" "$(dirname "$ROUTER_OUT")"

DETECTOR_ARGS=(
  --workspace "$WORKSPACE"
  --output-file "$DETECTOR_OUT"
)
[[ -n "$CRITICAL_JOBS" ]] && DETECTOR_ARGS+=(--critical-jobs "$CRITICAL_JOBS")
[[ -n "$HEARTBEAT_JOB" ]] && DETECTOR_ARGS+=(--heartbeat-job "$HEARTBEAT_JOB")

detector_json="$(bash "$SCRIPT_DIR/ops-threshold-detector.sh" "${DETECTOR_ARGS[@]}")"
[[ -n "${detector_json// }" ]] || { echo "detector produced empty output" >&2; exit 2; }
jq -e . >/dev/null 2>&1 <<<"$detector_json" || { echo "detector produced invalid JSON" >&2; exit 2; }

echo "$detector_json" | bash "$SCRIPT_DIR/ops-incident-router.sh" \
  --state-file "$STATE_FILE" \
  --router-out "$ROUTER_OUT" \
  $([[ "$LIVE" == "true" ]] && echo --live || echo --dry-run)

echo "cycle_complete ts=$(date -u +%Y-%m-%dT%H:%M:%SZ) detector_out=$DETECTOR_OUT router_out=$ROUTER_OUT"
