#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="./incident-state.json"
DETECTOR_FILE=""
ROUTER_OUT=""
LIVE=false

usage() {
  cat <<USAGE
Usage: ops-incident-router.sh [options]

Options:
  --state-file <file>      Guard state file path (default: ./incident-state.json)
  --detector-file <file>   Detector JSONL file (uses last line)
  --router-out <file>      Append router decisions/actions to this JSONL file
  --live                   Acquire in-flight lock via incident-state-update.sh
  --dry-run                Do not acquire in-flight lock (default)
  -h, --help               Show help

Input:
  If --detector-file is omitted, read one detector JSON object from stdin.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --state-file) STATE_FILE="$2"; shift 2 ;;
    --detector-file) DETECTOR_FILE="$2"; shift 2 ;;
    --router-out) ROUTER_OUT="$2"; shift 2 ;;
    --live) LIVE=true; shift ;;
    --dry-run) LIVE=false; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }

if [[ -n "$ROUTER_OUT" ]]; then
  mkdir -p "$(dirname "$ROUTER_OUT")"
fi

if [[ -n "$DETECTOR_FILE" ]]; then
  [[ -f "$DETECTOR_FILE" ]] || { echo "detector file not found: $DETECTOR_FILE" >&2; exit 2; }
  detector_json="$(tail -1 "$DETECTOR_FILE")"
else
  detector_json="$(cat)"
fi

[[ -n "${detector_json// }" ]] || { echo "empty detector input" >&2; exit 2; }
jq -e . >/dev/null 2>&1 <<<"$detector_json" || { echo "invalid detector JSON input" >&2; exit 2; }

status="$(jq -r '.status // "UNKNOWN"' <<<"$detector_json" 2>/dev/null || echo "UNKNOWN")"
if [[ "$status" == "OK" ]]; then
  info='{"action":"noop","reason":"no_alerts"}'
  echo "$info"
  [[ -n "$ROUTER_OUT" ]] && echo "$info" >> "$ROUTER_OUT"
  exit 0
fi

map_trigger_to_check_id() {
  case "$1" in
    cron_failure) echo "cron_failure" ;;
    heartbeat_gap|paymaster_gap) echo "heartbeat_gap" ;;
    context_crit|context_100pct) echo "context_crit" ;;
    context_high|context_90pct) echo "context_high" ;;
    context_warn|context_80pct) echo "context_warn" ;;
    dangling_sessions) echo "dangling_sessions" ;;
    token_spike) echo "token_spike" ;;
    *) echo "unknown_${1}" ;;
  esac
}

alerts='[]'
if jq -e '.alerts' >/dev/null 2>&1 <<<"$detector_json"; then
  alerts="$(jq -c '.alerts // []' <<<"$detector_json")"
fi
jq -e 'type == "array"' >/dev/null 2>&1 <<<"$alerts" || { echo "detector alerts must be an array" >&2; exit 2; }

if [[ "$(jq -r 'length' <<<"$alerts")" == "0" ]]; then
  info='{"action":"noop","reason":"alerts_empty"}'
  echo "$info"
  [[ -n "$ROUTER_OUT" ]] && echo "$info" >> "$ROUTER_OUT"
  exit 0
fi

while IFS= read -r alert; do
  trigger="$(jq -r '.trigger // "unknown"' <<<"$alert")"
  severity="$(jq -r '.sev // "Sev-3"' <<<"$alert")"
  check_id="$(map_trigger_to_check_id "$trigger")"

  guard_raw="$(bash "$SCRIPT_DIR/incident-guard-check.sh" --check-id "$check_id" --severity "$severity" --state-file "$STATE_FILE")"
  allowed="$(jq -r '.allowed // false' <<<"$guard_raw")"
  reason="$(jq -r '.reason // "unknown"' <<<"$guard_raw")"

  if [[ "$allowed" == "true" ]]; then
    action_json="$(jq -cn \
      --arg action "spawn" \
      --arg check_id "$check_id" \
      --arg severity "$severity" \
      --arg mode "$([[ "$LIVE" == "true" ]] && echo live || echo dry-run)" \
      --arg task "Investigate incident: ${check_id}. Gather evidence, classify severity, propose low-risk remediations with rollback." \
      '{action:$action,check_id:$check_id,severity:$severity,mode:$mode,task:$task}')"

    echo "$action_json"
    [[ -n "$ROUTER_OUT" ]] && echo "$action_json" >> "$ROUTER_OUT"

    if [[ "$LIVE" == "true" ]]; then
      bash "$SCRIPT_DIR/incident-state-update.sh" --action start --check-id "$check_id" --severity "$severity" --state-file "$STATE_FILE" >/dev/null
    fi
  else
    blocked_json="$(jq -cn \
      --arg action "blocked" \
      --arg check_id "$check_id" \
      --arg severity "$severity" \
      --arg reason "$reason" \
      '{action:$action,check_id:$check_id,severity:$severity,reason:$reason}')"

    echo "$blocked_json"
    [[ -n "$ROUTER_OUT" ]] && echo "$blocked_json" >> "$ROUTER_OUT"
  fi
done < <(jq -c '.[]' <<<"$alerts")
