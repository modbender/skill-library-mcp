#!/usr/bin/env bash
set -euo pipefail

# reconcile-tasks.sh — Butler-style reconciler.
# Finds cc-* tasks that look completed (report exists) but haven't been "delivered" yet
# (according to local state). Emits a concise markdown summary.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LIST_SCRIPT="$SCRIPT_DIR/list-tasks.sh"
STATE_KEY="global"
NAMESPACE=""
STATE_PATH_BASE="$BASE_DIR/state"
STATE_PATH="$STATE_PATH_BASE/task-delivery-state.json"

SOCKET="${TMPDIR:-/tmp}/clawdbot-tmux-sockets/clawdbot.sock"
LINES_N=20
MARK_LABEL=""
MARK_ALL=false

# statuses that imply "done enough to deliver"
DONE_STATUSES_REGEX='^(likely_done|done_session_ended|dead)$'

while [[ $# -gt 0 ]]; do
  case "$1" in
    --socket) SOCKET="$2"; shift 2 ;;
    --lines)  LINES_N="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2"; shift 2 ;;
    --state-key) STATE_KEY="$2"; shift 2 ;;
    --mark)   MARK_LABEL="$2"; shift 2 ;;
    --mark-all) MARK_ALL=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# derive state key
if [[ -n "$NAMESPACE" && "$STATE_KEY" == "global" ]]; then
  STATE_KEY="$NAMESPACE"
fi
# sanitize for filename
state_file_key="$(echo "$STATE_KEY" | tr -cd 'a-zA-Z0-9._-')"
if [[ -z "$state_file_key" ]]; then state_file_key="global"; fi
STATE_PATH="$STATE_PATH_BASE/task-delivery-state.${state_file_key}.json"

if [[ ! -f "$STATE_PATH" ]]; then
  mkdir -p "$(dirname "$STATE_PATH")"
  echo '{"version":1,"tasks":{}}' > "$STATE_PATH"
fi

# read tasks list
list_args=(--json --socket "$SOCKET" --lines "$LINES_N")
if [[ -n "$NAMESPACE" ]]; then
  list_args+=(--namespace "$NAMESPACE")
fi
json="$({ bash "$LIST_SCRIPT" "${list_args[@]}"; } 2>/dev/null || echo '[]')"

# helper: mac/linux stat mtime
mtime() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    echo "0"; return
  fi
  if stat -f %m "$f" >/dev/null 2>&1; then
    stat -f %m "$f"
  else
    stat -c %Y "$f"
  fi
}

# iterate tasks and build pending list
pending_items=()

# Use jq to select candidates first
candidates="$(echo "$json" | jq -c --arg re "$DONE_STATUSES_REGEX" '.[] | select(.reportExists==true) | select(.status|test($re))')"

while IFS= read -r item; do
  [[ -z "$item" ]] && continue
  label="$(echo "$item" | jq -r '.label')"
  session="$(echo "$item" | jq -r '.session')"
  report="$(echo "$item" | jq -r '.reportJsonPath')"
  last_lines="$(echo "$item" | jq -r '.lastLines')"

  r_mtime="$(mtime "$report")"

  # last delivered mtime
  delivered_mtime="$(jq -r --arg l "$label" '.tasks[$l].deliveredReportMtime // 0' "$STATE_PATH")"

  if [[ "$r_mtime" -gt 0 && "$r_mtime" -gt "$delivered_mtime" ]]; then
    pending_items+=("$(jq -n \
      --arg label "$label" \
      --arg session "$session" \
      --arg report "$report" \
      --arg lastLines "$last_lines" \
      --argjson reportMtime "$r_mtime" \
      '{label:$label, session:$session, report:$report, reportMtime:$reportMtime, lastLines:$lastLines}'
    )")
  fi

done <<< "$candidates"

# ── Mark delivered (state update) ──────────────────────────────────
# Usage:
#   reconcile-tasks.sh --mark <label>
#   reconcile-tasks.sh --mark-all
if [[ -n "$MARK_LABEL" || "$MARK_ALL" == "true" ]]; then
  tmp_state="$(mktemp)"
  cp "$STATE_PATH" "$tmp_state"

  mark_one() {
    local lbl="$1"
    local rep="/tmp/cc-${lbl}-completion-report.json"
    local m
    m="$(mtime "$rep")"
    [[ "$m" -le 0 ]] && return 0

    # atomic-ish rewrite via temp + mv
    local tmp_out
    tmp_out="$(mktemp)"
    jq --arg l "$lbl" --argjson m "$m" --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      '.tasks[$l] = ((.tasks[$l] // {}) + {deliveredReportMtime:$m, deliveredAt:$at})' \
      "$tmp_state" > "$tmp_out"
    mv "$tmp_out" "$tmp_state"
  }

  if [[ "$MARK_ALL" == "true" ]]; then
    # mark all candidates that have a report mtime
    while IFS= read -r item; do
      [[ -z "$item" ]] && continue
      lbl="$(echo "$item" | jq -r '.label')"
      mark_one "$lbl"
    done <<< "$candidates"
  else
    mark_one "$MARK_LABEL"
  fi

  mv "$tmp_state" "$STATE_PATH"
  exit 0
fi

# output
if [[ ${#pending_items[@]} -eq 0 ]]; then
  # No pending deliveries.
  exit 0
fi

now_local="$(date '+%Y-%m-%d %H:%M:%S')"

cat <<EOF
【Claude Code 管家巡检】发现 ${#pending_items[@]} 个“已完成但未推送”的任务（${now_local}）
EOF

echo

i=0
for p in "${pending_items[@]}"; do
  i=$((i+1))
  label="$(echo "$p" | jq -r '.label')"
  session="$(echo "$p" | jq -r '.session')"
  report="$(echo "$p" | jq -r '.report')"
  last_lines="$(echo "$p" | jq -r '.lastLines')"

  {
    printf "%s) **%s**\n" "$i" "$label"
    printf -- "- session: %s\n" "$session"
    printf -- "- report: %s\n" "$report"
    printf -- "- attach:\n"
    printf '%s\n' '```'
    printf 'tmux -S "%s" attach -t "%s"\n' "$SOCKET" "$session"
    printf '%s\n' '```'
  }

  if [[ -n "$last_lines" && "$last_lines" != "null" ]]; then
    printf -- "- last lines:\n"
    printf '%s\n' '```'
    printf '%s\n' "$last_lines"
    printf '%s\n' '```'
  fi

  echo

done

cat <<'EOF'
建议：我现在可以直接基于 report + transcript 做一次正式汇总并推送。你回复“推送 <label>”即可。
EOF
