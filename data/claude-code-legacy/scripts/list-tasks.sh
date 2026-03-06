#!/usr/bin/env bash
set -euo pipefail

# list-tasks.sh — List all cc-* tmux sessions with status summary.
# Calls status-tmux-task.sh per session, captures last N lines, outputs
# human-readable (default) or --json.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATUS_SCRIPT="$SCRIPT_DIR/status-tmux-task.sh"

SOCKET="${TMPDIR:-/tmp}/clawdbot-tmux-sockets/clawdbot.sock"
LINES_N=20
JSON_MODE=false
TARGET="local"
SSH_HOST=""
NAMESPACE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lines)   LINES_N="$2"; shift 2 ;;
    --socket)  SOCKET="$2"; shift 2 ;;
    --json)    JSON_MODE=true; shift ;;
    --target)  TARGET="$2"; shift 2 ;;
    --ssh-host) SSH_HOST="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ "$TARGET" == "ssh" && -z "$SSH_HOST" ]]; then
  echo "ERROR: --target ssh requires --ssh-host <alias>" >&2
  exit 2
fi

# ── Collect cc-* session names ──────────────────────────────────────
sessions=()
if [[ "$TARGET" == "ssh" ]]; then
  raw="$(ssh -o BatchMode=yes "$SSH_HOST" \
    "tmux -S '$SOCKET' list-sessions -F '#{session_name}' 2>/dev/null" 2>/dev/null || true)"
else
  raw="$(tmux -S "$SOCKET" list-sessions -F '#{session_name}' 2>/dev/null || true)"
fi

while IFS= read -r name; do
  [[ -z "$name" ]] && continue
  [[ "$name" != cc-* ]] && continue
  if [[ -n "$NAMESPACE" ]]; then
    [[ "$name" == cc-${NAMESPACE}-* ]] && sessions+=("$name")
  else
    sessions+=("$name")
  fi

done <<< "$raw"

# ── No sessions ────────────────────────────────────────────────────
if [[ ${#sessions[@]} -eq 0 ]]; then
  if $JSON_MODE; then
    echo "[]"
  else
    echo "No cc-* sessions found (socket: $SOCKET)"
  fi
  exit 0
fi

# ── Iterate sessions and build results ─────────────────────────────
json_items=()
now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for sess in "${sessions[@]}"; do
  label="${sess#cc-}"
  namespace=""
  if [[ -n "$NAMESPACE" ]]; then
    namespace="$NAMESPACE"
    label="${sess#cc-${NAMESPACE}-}"
  fi

  # --- call status-tmux-task.sh ---
  status_raw=""
  status="unknown"
  session_alive="false"
  report_exists="false"
  error_msg=""

  status_args=(--label "$label" --session "$sess" --socket "$SOCKET")
  if [[ "$TARGET" == "ssh" ]]; then
    status_args+=(--target ssh --ssh-host "$SSH_HOST")
  fi

  if status_raw="$(bash "$STATUS_SCRIPT" "${status_args[@]}" 2>&1)"; then
    # parse key=value lines
    while IFS='=' read -r k v; do
      case "$k" in
        STATUS)        status="$v" ;;
        SESSION_ALIVE) session_alive="$v" ;;
        REPORT_EXISTS) report_exists="$v" ;;
      esac
    done <<< "$status_raw"
  else
    error_msg="$status_raw"
  fi

  # --- report JSON path ---
  report_json_path="/tmp/${sess}-completion-report.json"

  # --- capture last N lines (best-effort) ---
  last_lines=""
  if [[ "$session_alive" == "true" ]]; then
    if [[ "$TARGET" == "ssh" ]]; then
      last_lines="$(ssh -o BatchMode=yes "$SSH_HOST" \
        "tmux -S '$SOCKET' capture-pane -p -J -t '$sess':0.0 -S -'$LINES_N'" 2>/dev/null || true)"
    else
      last_lines="$(tmux -S "$SOCKET" capture-pane -p -J -t "$sess":0.0 -S -"$LINES_N" 2>/dev/null || true)"
    fi
  fi

  # --- output ---
  if $JSON_MODE; then
    item="$(jq -n \
      --arg label "$label" \
      --arg session "$sess" \
      --arg status "$status" \
      --argjson sessionAlive "$([ "$session_alive" = "true" ] && echo true || echo false)" \
      --argjson reportExists "$([ "$report_exists" = "true" ] && echo true || echo false)" \
      --arg reportJsonPath "$report_json_path" \
      --arg lastLines "$last_lines" \
      --arg updatedAt "$now_iso" \
      --arg errorMsg "$error_msg" \
      --arg namespace "$namespace" \
      '(
        {
          label: $label,
          session: $session,
          status: $status,
          sessionAlive: $sessionAlive,
          reportExists: $reportExists,
          reportJsonPath: $reportJsonPath,
          lastLines: $lastLines,
          updatedAt: $updatedAt
        }
        + (if $namespace != "" then { namespace: $namespace } else {} end)
        + (if $errorMsg != "" then { error: $errorMsg } else {} end)
      )'
    )"
    json_items+=("$item")
  else
    alive_tag="alive"
    [[ "$session_alive" != "true" ]] && alive_tag="dead"
    report_tag=""
    [[ "$report_exists" == "true" ]] && report_tag=" [report ready]"

    printf "%-24s  status=%-20s  (%s)%s\n" "$sess" "$status" "$alive_tag" "$report_tag"
    if [[ -n "$error_msg" ]]; then
      echo "  error: $error_msg"
    fi
  fi
done

# ── Final JSON array ───────────────────────────────────────────────
if $JSON_MODE; then
  # Combine individual JSON objects into an array
  printf '%s\n' "${json_items[@]}" | jq -s '.'
fi
