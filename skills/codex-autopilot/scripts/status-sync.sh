#!/bin/bash
# status-sync.sh — 统一更新项目 status.json（原子写入）
#
# 用法:
#   status-sync.sh <project_dir> <event> [key=value ...]
# 事件:
#   commit | review_triggered | review_clean | review_issues
#   nudge_sent | compact_sent | shell_recovery

set -euo pipefail

PROJECT_DIR="${1:?usage: status-sync.sh <project_dir> <event> [key=value ...]}"
EVENT="${2:?usage: status-sync.sh <project_dir> <event> [key=value ...]}"
shift 2 || true

[ -d "$PROJECT_DIR" ] || exit 0
command -v jq >/dev/null 2>&1 || exit 0

LOCK_DIR="$HOME/.autopilot/locks"
mkdir -p "$LOCK_DIR"

sanitize() {
    echo "$1" | tr -cd 'a-zA-Z0-9_-'
}

normalize_int() {
    local val
    val=$(echo "${1:-}" | tr -dc '0-9')
    echo "${val:-0}"
}

safe="$(sanitize "$(basename "$PROJECT_DIR")")"
[ -n "$safe" ] || safe="project"
LOCK_PATH="${LOCK_DIR}/status-sync-${safe}.lock.d"

acquire_lock() {
    if mkdir "$LOCK_PATH" 2>/dev/null; then
        echo "$$" > "${LOCK_PATH}/pid"
        return 0
    fi

    local existing_pid
    existing_pid=$(cat "${LOCK_PATH}/pid" 2>/dev/null || echo 0)
    existing_pid=$(normalize_int "$existing_pid")

    if [ "$existing_pid" -gt 0 ] && kill -0 "$existing_pid" 2>/dev/null; then
        return 1
    fi

    rm -rf "$LOCK_PATH" 2>/dev/null || true
    mkdir "$LOCK_PATH" 2>/dev/null || return 1
    echo "$$" > "${LOCK_PATH}/pid"
    return 0
}

if ! acquire_lock; then
    exit 0
fi
trap 'rm -rf "$LOCK_PATH"' EXIT

window=""
reason=""
state=""
head=""
since_review=""
new_commits=""
p0=""
p1=""
issues=""

for kv in "$@"; do
    key="${kv%%=*}"
    value="${kv#*=}"
    [ "$key" != "$kv" ] || continue
    case "$key" in
        window) window="$value" ;;
        reason) reason="$value" ;;
        state) state="$value" ;;
        head) head="$value" ;;
        since_review) since_review="$value" ;;
        new_commits) new_commits="$value" ;;
        p0) p0="$value" ;;
        p1) p1="$value" ;;
        issues) issues="$value" ;;
    esac
done

issues="${issues:0:240}"
NOW_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
STATUS_FILE="${PROJECT_DIR}/status.json"

# 文件不存在或损坏时，补最小骨架
if [ ! -s "$STATUS_FILE" ] || ! jq -e . "$STATUS_FILE" >/dev/null 2>&1; then
    project_name="$(basename "$PROJECT_DIR")"
    jq -n \
      --arg project "$project_name" \
      --arg now "$NOW_UTC" \
      '{project:$project,phase:"dev",phases:{dev:{status:"pending"},review:{status:"pending"},test:{status:"pending"},deploy:{status:"pending"},prd:{status:"pending"}},updated_at:$now}' \
      > "${STATUS_FILE}.tmp.$$"
    mv -f "${STATUS_FILE}.tmp.$$" "$STATUS_FILE"
fi

jq \
  --arg now "$NOW_UTC" \
  --arg event "$EVENT" \
  --arg window "$window" \
  --arg reason "$reason" \
  --arg state "$state" \
  --arg head "$head" \
  --arg since_review "$since_review" \
  --arg new_commits "$new_commits" \
  --arg p0 "$p0" \
  --arg p1 "$p1" \
  --arg issues "$issues" \
  '
  def ensure_shape:
    . + {phases:(.phases // {})}
    | .phases.dev = (.phases.dev // {"status":"pending"})
    | .phases.review = (.phases.review // {"status":"pending"})
    | .phases.test = (.phases.test // {"status":"pending"})
    | .phases.deploy = (.phases.deploy // {"status":"pending"})
    | .phases.prd = (.phases.prd // {"status":"pending"});

  def stamp_meta:
    .updated_at = $now
    | .autopilot = (.autopilot // {})
    | .autopilot.last_event = $event
    | .autopilot.last_sync_at = $now
    | (if $window != "" then .autopilot.last_window = $window else . end)
    | (if $reason != "" then .autopilot.last_reason = $reason else . end)
    | (if $state != "" then .autopilot.last_state = $state else . end)
    | (if $head != "" then .autopilot.last_head = $head else . end)
    | (if $since_review != "" then .autopilot.last_since_review = ($since_review | tonumber? // .autopilot.last_since_review // 0) else . end)
    | (if $new_commits != "" then .autopilot.last_new_commits = ($new_commits | tonumber? // .autopilot.last_new_commits // 0) else . end)
    | (if $issues != "" then .autopilot.last_issues = $issues else . end);

  def on_commit:
    .phase = "dev"
    | .phases.dev.status = "in_progress"
    | (if $head != "" then .phases.dev.last_commit = $head else . end)
    | (if $new_commits != "" then .phases.dev.new_commits = ($new_commits | tonumber? // .phases.dev.new_commits // 0) else . end)
    | (if $since_review != "" then .phases.dev.since_review = ($since_review | tonumber? // .phases.dev.since_review // 0) else . end);

  def on_review_triggered:
    .phase = "review"
    | .phases.review.status = "in_progress"
    | .phases.review.round = ((.phases.review.round // 0) + 1)
    | (if $since_review != "" then .phases.review.since_review = ($since_review | tonumber? // .phases.review.since_review // 0) else . end);

  def on_review_clean:
    .phase = "test"
    | .phases.review.status = "done"
    | .phases.review.p0 = 0
    | .phases.review.p1 = 0
    | .phases.review.issues = [];

  def on_review_issues:
    .phase = "review"
    | .phases.review.status = "in_progress"
    | (if $p0 != "" then .phases.review.p0 = ($p0 | tonumber? // .phases.review.p0 // 0) else . end)
    | (if $p1 != "" then .phases.review.p1 = ($p1 | tonumber? // .phases.review.p1 // 0) else . end)
    | (if $issues != "" then .phases.review.issues = [$issues] else . end);

  def on_prd_verify_pass:
    .phases.prd.status = "verified"
    | .phases.prd.last_result = "pass"
    | .phases.prd.last_verified_at = $now;

  def on_prd_verify_fail:
    .phase = "dev"
    | .phases.prd.status = "failed"
    | .phases.prd.last_result = "fail"
    | .phases.prd.last_verified_at = $now
    | (if $issues != "" then .phases.prd.last_issues = $issues else . end);

  def on_prd_bugfix_synced:
    .phases.prd.status = "in_progress"
    | .phases.prd.bugfix_sync_count = ((.phases.prd.bugfix_sync_count // 0) + 1)
    | .phases.prd.last_sync_at = $now;

  def on_unknown_event:
    .autopilot.unknown_event_count = ((.autopilot.unknown_event_count // 0) + 1)
    | .autopilot.last_unknown_event = $event
    | .autopilot.last_unknown_event_at = $now;

  ensure_shape
  | stamp_meta
  | if $event == "commit" then on_commit
    elif $event == "review_triggered" then on_review_triggered
    elif $event == "review_clean" then on_review_clean
    elif $event == "review_issues" then on_review_issues
    elif $event == "prd_verify_pass" then on_prd_verify_pass
    elif $event == "prd_verify_fail" then on_prd_verify_fail
    elif $event == "prd_bugfix_synced" then on_prd_bugfix_synced
    elif $event == "compact_sent" then .autopilot.compact_count = ((.autopilot.compact_count // 0) + 1)
    elif $event == "nudge_sent" then .autopilot.nudge_count = ((.autopilot.nudge_count // 0) + 1)
    elif $event == "shell_recovery" then .autopilot.recoveries = ((.autopilot.recoveries // 0) + 1)
    else on_unknown_event
    end
  ' "$STATUS_FILE" > "${STATUS_FILE}.tmp.$$"

mv -f "${STATUS_FILE}.tmp.$$" "$STATUS_FILE"
