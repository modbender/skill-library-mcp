#!/bin/bash
# monitor-all.sh v2 — 统一监控所有项目，事件驱动输出
# 用法: monitor-all.sh
# 输出: JSON，只包含有变化的项目。无变化时输出 {"changes":false}
# 新增: report(结构化汇总) + daily_tokens(按项目当日 token 统计)
# 
# 检测逻辑：
#   1. 对每个项目运行 codex-status.sh
#   2. 读取 git HEAD 和最近 commit 信息
#   3. 对比 state 文件中的上次状态
#   4. 只输出发生变化的项目
#
# 变化定义：
#   - 状态变化（working→idle, idle→working, shell, compact 等）
#   - 新 commit 产生（HEAD 变了）
#   - context 跨过阈值（>LOW_CONTEXT_THRESHOLD, >LOW_CONTEXT_CRITICAL_THRESHOLD）
#   - 连续 3 轮无 commit 但 working（追踪但不告警）

set -uo pipefail
# NOTE: do NOT add set -e; codex-status.sh returns exit 1 for idle/permission,
# and many grep/jq commands may legitimately return non-zero.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/autopilot-lib.sh"
if [ -f "${SCRIPT_DIR}/autopilot-constants.sh" ]; then
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/autopilot-constants.sh"
fi
LOW_CONTEXT_THRESHOLD="${LOW_CONTEXT_THRESHOLD:-25}"
LOW_CONTEXT_CRITICAL_THRESHOLD="${LOW_CONTEXT_CRITICAL_THRESHOLD:-15}"

STATE_DIR="$HOME/.autopilot/state"
LOCK_DIR="$HOME/.autopilot/locks"
MONITOR_LOCK="${LOCK_DIR}/monitor-all.lock.d"
mkdir -p "$STATE_DIR" "$LOCK_DIR"

TMUX="/opt/homebrew/bin/tmux"

format_token_count() {
    local n
    n=$(normalize_int "${1:-0}")
    if [ "$n" -ge 1000000 ]; then
        awk -v v="$n" 'BEGIN { printf "%.2fM", v/1000000 }'
    elif [ "$n" -ge 1000 ]; then
        awk -v v="$n" 'BEGIN { printf "%.1fk", v/1000 }'
    else
        printf "%s" "$n"
    fi
}

acquire_script_lock() {
    if mkdir "$MONITOR_LOCK" 2>/dev/null; then
        echo "$$" > "${MONITOR_LOCK}/pid"
        return 0
    fi

    local existing_pid
    existing_pid=$(cat "${MONITOR_LOCK}/pid" 2>/dev/null || echo 0)
    existing_pid=$(normalize_int "$existing_pid")

    if [ "$existing_pid" -gt 0 ] && kill -0 "$existing_pid" 2>/dev/null; then
        return 1
    fi

    rm -rf "$MONITOR_LOCK" 2>/dev/null || true
    mkdir "$MONITOR_LOCK" 2>/dev/null || return 1
    echo "$$" > "${MONITOR_LOCK}/pid"
    return 0
}

if ! acquire_script_lock; then
    echo '{"changes":false}'
    exit 0
fi
trap 'rm -rf "$MONITOR_LOCK" 2>/dev/null || true' EXIT

REPORT_ONLY=false
if [ -n "${MONITOR_REPORT_ONLY:-}" ]; then
    case "${MONITOR_REPORT_ONLY,,}" in
        1|true|yes)
            REPORT_ONLY=true
            ;;
    esac
fi
while [ $# -gt 0 ]; do
    case "$1" in
        --report-only)
            REPORT_ONLY=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

# 项目配置（优先读取 watchdog-projects.conf，格式 window:project_dir，兼容旧三列）
PROJECT_CONFIG_FILE="$HOME/.autopilot/watchdog-projects.conf"
DEFAULT_PROJECTS=(
    "Shike:/Users/wes/Shike"
    "agent-simcity:/Users/wes/projects/agent-simcity"
    "replyher_android-2:/Users/wes/replyher_android-2"
)
PROJECTS=()

load_projects() {
    PROJECTS=()

    if [ -f "$PROJECT_CONFIG_FILE" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            line="${line%$'\r'}"
            case "$line" in
                ""|\#*)
                    continue
                    ;;
            esac

            local window rest dir
            window="${line%%:*}"
            rest="${line#*:}"
            [ "$rest" = "$line" ] && continue
            dir="${rest%%:*}"

            [ -z "$window" ] && continue
            [ -z "$dir" ] && continue
            PROJECTS+=("${window}:${dir}")
        done < "$PROJECT_CONFIG_FILE"
    fi

    if [ ${#PROJECTS[@]} -eq 0 ]; then
        PROJECTS=("${DEFAULT_PROJECTS[@]}")
    fi
}

CHANGES=()
ALL_STATUS=()
PHASE_TRACKING=()
REVIEW_STATUS_TRACKING=()

load_projects

TOKEN_SUMMARY_JSON='{"date":"","timezone":"","totals":{"input_tokens":0,"cached_input_tokens":0,"output_tokens":0,"reasoning_output_tokens":0,"total_tokens":0},"projects":[],"top_project":null}'
if [ -x "${SCRIPT_DIR}/codex-token-daily.py" ]; then
    token_cmd=("${SCRIPT_DIR}/codex-token-daily.py")
    for entry in "${PROJECTS[@]}"; do
        token_cmd+=("--project" "$entry")
    done
    TOKEN_SUMMARY_JSON=$("${token_cmd[@]}" 2>/dev/null || echo "$TOKEN_SUMMARY_JSON")
fi
if ! echo "$TOKEN_SUMMARY_JSON" | jq -e . >/dev/null 2>&1; then
    TOKEN_SUMMARY_JSON='{"date":"","timezone":"","totals":{"input_tokens":0,"cached_input_tokens":0,"output_tokens":0,"reasoning_output_tokens":0,"total_tokens":0},"projects":[],"top_project":null}'
fi

WORKING_COUNT=0
IDLE_COUNT=0
PERMISSION_COUNT=0
SHELL_COUNT=0
ABSENT_COUNT=0

for entry in "${PROJECTS[@]}"; do
    WINDOW="${entry%%:*}"
    DIR="${entry##*:}"
    STATE_FILE="$STATE_DIR/${WINDOW}.json"

    # --- 当前状态 ---
    STATUS_JSON=$("$SCRIPT_DIR/codex-status.sh" "$WINDOW" 2>/dev/null) || true
    CUR_STATUS=$(echo "$STATUS_JSON" | jq -r '.status // ""' 2>/dev/null || true)
    CUR_CONTEXT=$(echo "$STATUS_JSON" | jq -r '.context_num // -1' 2>/dev/null || true)
    [ -z "$CUR_STATUS" ] && CUR_STATUS="absent"
    [ -z "$CUR_CONTEXT" ] && CUR_CONTEXT=-1
    case "$CUR_STATUS" in
        working) WORKING_COUNT=$((WORKING_COUNT + 1)) ;;
        idle|idle_low_context) IDLE_COUNT=$((IDLE_COUNT + 1)) ;;
        permission|permission_with_remember) PERMISSION_COUNT=$((PERMISSION_COUNT + 1)) ;;
        shell) SHELL_COUNT=$((SHELL_COUNT + 1)) ;;
        absent|*) ABSENT_COUNT=$((ABSENT_COUNT + 1)) ;;
    esac

    # Git 信息
    CUR_HEAD=$(cd "$DIR" && git rev-parse --short HEAD 2>/dev/null || echo "none")
    CUR_COMMIT_MSG=$(cd "$DIR" && git log --oneline -1 --format="%s" 2>/dev/null | head -c 80 || echo "")
    CUR_COMMIT_TIME=$(cd "$DIR" && git log -1 --format="%ct" 2>/dev/null || echo "0")
    COMMITS_30M=$(cd "$DIR" && git log --oneline --since="30 minutes ago" 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    TOKENS_TODAY=$(echo "$TOKEN_SUMMARY_JSON" | jq -r --arg window "$WINDOW" '.projects[] | select(.window==$window) | .total_tokens // 0' | head -1)
    TOKENS_TODAY=$(normalize_int "$TOKENS_TODAY")
    TOKENS_TODAY_HUMAN=$(format_token_count "$TOKENS_TODAY")

    # Codex 最后输出（用于智能 nudge）
    LAST_OUTPUT=""
    if [ "$CUR_STATUS" = "idle" ] || [ "$CUR_STATUS" = "idle_low_context" ]; then
        LAST_OUTPUT=$("$TMUX" capture-pane -t "autopilot:${WINDOW}" -p -S -20 2>/dev/null | head -15 | tr '\n' '|' || echo "")
    fi

    # --- 读取上次状态 ---
    PREV_STATUS="unknown"
    PREV_HEAD="none"
    PREV_CONTEXT=-1
    PREV_WORKING_NO_COMMIT=0
    if [ -f "$STATE_FILE" ]; then
        PREV_STATUS=$(jq -r '.status // "unknown"' "$STATE_FILE" 2>/dev/null || echo "unknown")
        PREV_HEAD=$(jq -r '.head // "none"' "$STATE_FILE" 2>/dev/null || echo "none")
        PREV_CONTEXT=$(jq -r '.context_num // -1' "$STATE_FILE" 2>/dev/null || echo "-1")
        PREV_WORKING_NO_COMMIT=$(jq -r '.working_no_commit // 0' "$STATE_FILE" 2>/dev/null || echo "0")
    fi

    # --- 判断变化 ---
    HAS_CHANGE=false
    CHANGE_REASONS=""

    # 状态变化
    if [ "$CUR_STATUS" != "$PREV_STATUS" ]; then
        HAS_CHANGE=true
        CHANGE_REASONS="${CHANGE_REASONS}status:${PREV_STATUS}→${CUR_STATUS} "
    fi

    # 新 commit
    NEW_COMMITS=0
    if [ "$CUR_HEAD" != "$PREV_HEAD" ] && [ "$PREV_HEAD" != "none" ]; then
        HAS_CHANGE=true
        NEW_COMMITS=$(cd "$DIR" && git log --oneline "${PREV_HEAD}..${CUR_HEAD}" 2>/dev/null | wc -l | tr -d ' ' || echo "1")
        CHANGE_REASONS="${CHANGE_REASONS}commits:+${NEW_COMMITS} "
    fi

    # Context 跨阈值
    if [ "$PREV_CONTEXT" -gt "$LOW_CONTEXT_THRESHOLD" ] && [ "$CUR_CONTEXT" -le "$LOW_CONTEXT_THRESHOLD" ] && [ "$CUR_CONTEXT" -gt 0 ]; then
        HAS_CHANGE=true
        CHANGE_REASONS="${CHANGE_REASONS}context:${PREV_CONTEXT}%→${CUR_CONTEXT}%(low) "
    fi
    if [ "$PREV_CONTEXT" -gt "$LOW_CONTEXT_CRITICAL_THRESHOLD" ] && [ "$CUR_CONTEXT" -le "$LOW_CONTEXT_CRITICAL_THRESHOLD" ] && [ "$CUR_CONTEXT" -gt 0 ]; then
        HAS_CHANGE=true
        CHANGE_REASONS="${CHANGE_REASONS}context:critical(${CUR_CONTEXT}%) "
    fi

    # Working 无 commit 计数
    WORKING_NO_COMMIT=0
    if [ "$CUR_STATUS" = "working" ] && [ "$CUR_HEAD" = "$PREV_HEAD" ]; then
        WORKING_NO_COMMIT=$((PREV_WORKING_NO_COMMIT + 1))
    fi

    # 首次运行（无历史状态）也算变化
    if [ "$PREV_STATUS" = "unknown" ]; then
        HAS_CHANGE=true
        CHANGE_REASONS="initial "
    fi

    # --- 保存当前状态（原子写入）---
    jq -n \
      --arg status "$CUR_STATUS" \
      --argjson context_num "$CUR_CONTEXT" \
      --arg head "$CUR_HEAD" \
      --arg commit_msg "$CUR_COMMIT_MSG" \
      --argjson commit_time "$CUR_COMMIT_TIME" \
      --argjson commits_30m "$COMMITS_30M" \
      --argjson working_no_commit "$WORKING_NO_COMMIT" \
      --argjson tokens_today "$TOKENS_TODAY" \
      --argjson last_check "$(date +%s)" \
      '{status:$status,context_num:$context_num,head:$head,commit_msg:$commit_msg,commit_time:$commit_time,commits_30m:$commits_30m,working_no_commit:$working_no_commit,tokens_today:$tokens_today,last_check:$last_check}' \
      > "$STATE_FILE.tmp" && mv -f "$STATE_FILE.tmp" "$STATE_FILE"

    # --- 构建项目状态行 ---
    STATUS_EMOJI="✅"
    if [ "$CUR_STATUS" = "idle" ] || [ "$CUR_STATUS" = "idle_low_context" ]; then STATUS_EMOJI="⚠️"; fi
    if [ "$CUR_STATUS" = "shell" ]; then STATUS_EMOJI="🔄"; fi
    if [ "$CUR_STATUS" = "permission" ] || [ "$CUR_STATUS" = "permission_with_remember" ]; then STATUS_EMOJI="🔑"; fi

    # 多维度状态：读取 status.json
    LIFECYCLE=""
    PHASE_SUMMARY="unknown"
    REVIEW_SUMMARY="pending"
    if [ -f "${DIR}/status.json" ]; then
        phase=$(jq -r '.phase // "unknown"' "${DIR}/status.json" 2>/dev/null)
        dev_st=$(jq -r '.phases.dev.status // "pending"' "${DIR}/status.json" 2>/dev/null)
        review_st=$(jq -r '.phases.review.status // "pending"' "${DIR}/status.json" 2>/dev/null)
        test_st=$(jq -r '.phases.test.status // "pending"' "${DIR}/status.json" 2>/dev/null)
        deploy_st=$(jq -r '.phases.deploy.status // "pending"' "${DIR}/status.json" 2>/dev/null)

        # Build lifecycle string
        [ "$dev_st" = "done" ] && LIFECYCLE="✅dev" || LIFECYCLE="🔨dev"
        if [ "$review_st" = "done" ]; then
            LIFECYCLE="${LIFECYCLE} → ✅review"
        elif [ "$review_st" = "in_progress" ]; then
            r_p0=$(jq -r '.phases.review.p0 // 0' "${DIR}/status.json" 2>/dev/null)
            r_p1=$(jq -r '.phases.review.p1 // 0' "${DIR}/status.json" 2>/dev/null)
            LIFECYCLE="${LIFECYCLE} → 🔍review(${r_p0}P0 ${r_p1}P1)"
        else
            LIFECYCLE="${LIFECYCLE} → ⏳review"
        fi
        if [ "$test_st" = "done" ]; then
            LIFECYCLE="${LIFECYCLE} → ✅test"
        elif [ "$test_st" = "in_progress" ]; then
            bugs=$(jq -r '.phases.test.bugs | length // 0' "${DIR}/status.json" 2>/dev/null)
            LIFECYCLE="${LIFECYCLE} → 🔧test(${bugs}bugs)"
        else
            LIFECYCLE="${LIFECYCLE} → ⏳test"
        fi
        [ "$deploy_st" = "done" ] && LIFECYCLE="${LIFECYCLE} → ✅deploy" || LIFECYCLE="${LIFECYCLE} → ⏳deploy"
        PHASE_SUMMARY="$phase"
        REVIEW_SUMMARY="$review_st"
    fi
    PHASE_TRACKING+=("$PHASE_SUMMARY")
    REVIEW_STATUS_TRACKING+=("$REVIEW_SUMMARY")
    # 队列任务信息
    safe_window=$(echo "$WINDOW" | tr -cd 'a-zA-Z0-9_-')
    QUEUE_COUNT=$("${SCRIPT_DIR}/task-queue.sh" count "$safe_window" 2>/dev/null || echo 0)
    QUEUE_COUNT=$(normalize_int "$QUEUE_COUNT")
    QUEUE_IN_PROGRESS=$(grep -c '^\- \[→\]' "${HOME}/.autopilot/task-queue/${safe_window}.md" 2>/dev/null || true)
    QUEUE_IN_PROGRESS=$(normalize_int "$QUEUE_IN_PROGRESS")
    QUEUE_INFO=""
    if [ "$QUEUE_COUNT" -gt 0 ] || [ "$QUEUE_IN_PROGRESS" -gt 0 ]; then
        QUEUE_INFO=" | 📋q:${QUEUE_COUNT}待/${QUEUE_IN_PROGRESS}进"
    fi

    PROJECT_LINE="${STATUS_EMOJI} ${WINDOW}: ${CUR_STATUS} | phase ${PHASE_SUMMARY:-unknown} | review ${REVIEW_SUMMARY:-pending} | c30m ${COMMITS_30M} | tok/day ${TOKENS_TODAY_HUMAN}${QUEUE_INFO}"
    [ -n "$CUR_COMMIT_MSG" ] && PROJECT_LINE="${PROJECT_LINE} | ${CUR_COMMIT_MSG}"
    [ -n "$LIFECYCLE" ] && PROJECT_LINE="${PROJECT_LINE}"$'\n'"  ${LIFECYCLE}"

    ALL_STATUS+=("$PROJECT_LINE")

    if $HAS_CHANGE; then
        # 构建变化 JSON（使用 jq 安全转义）
        CHANGE_JSON=$(jq -n \
          --arg window "$WINDOW" \
          --arg dir "$DIR" \
          --arg status "$CUR_STATUS" \
          --arg prev_status "$PREV_STATUS" \
          --argjson context "$CUR_CONTEXT" \
          --arg head "$CUR_HEAD" \
          --arg prev_head "$PREV_HEAD" \
          --argjson new_commits "$NEW_COMMITS" \
          --argjson commits_30m "$COMMITS_30M" \
          --arg commit_msg "$CUR_COMMIT_MSG" \
          --argjson working_no_commit "$WORKING_NO_COMMIT" \
          --argjson tokens_today "$TOKENS_TODAY" \
          --arg reasons "$CHANGE_REASONS" \
          --arg last_output "$LAST_OUTPUT" \
          '{window:$window,dir:$dir,status:$status,prev_status:$prev_status,context:$context,head:$head,prev_head:$prev_head,new_commits:$new_commits,commits_30m:$commits_30m,commit_msg:$commit_msg,working_no_commit:$working_no_commit,tokens_today:$tokens_today,reasons:$reasons,last_output:$last_output}')
        CHANGES+=("$CHANGE_JSON")
    fi
done

TOTAL_PROJECTS=${#PROJECTS[@]}
CHANGED_COUNT=${#CHANGES[@]}
REPORT_TS_LOCAL=$(date '+%Y-%m-%d %H:%M')
REPORT_TS_UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

PHASE_COUNTS_JSON=$(printf '%s\n' "${PHASE_TRACKING[@]}" | jq -R . | jq -s 'map(select(length>0)) | group_by(.) | map({(.[0]): length}) | add // {}' 2>/dev/null || echo "{}")
REVIEW_STATUS_COUNTS_JSON=$(printf '%s\n' "${REVIEW_STATUS_TRACKING[@]}" | jq -R . | jq -s 'map(select(length>0)) | group_by(.) | map({(.[0]): length}) | add // {}' 2>/dev/null || echo "{}")
PROGRESS_JSON=$(jq -n --argjson changed "$CHANGED_COUNT" --argjson total "$TOTAL_PROJECTS" '{changed:$changed,total:$total}')

TOKEN_DATE=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.date // ""')
TOKEN_TOTAL=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.totals.total_tokens // 0')
TOKEN_INPUT=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.totals.input_tokens // 0')
TOKEN_CACHED=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.totals.cached_input_tokens // 0')
TOKEN_OUTPUT=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.totals.output_tokens // 0')
TOKEN_REASONING=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.totals.reasoning_output_tokens // 0')
TOKEN_TOP_WINDOW=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.top_project.window // ""')
TOKEN_TOP_TOTAL=$(echo "$TOKEN_SUMMARY_JSON" | jq -r '.top_project.total_tokens // 0')

REPORT_HEADER="📊 monitor ${REPORT_TS_LOCAL} | progress ${CHANGED_COUNT}/${TOTAL_PROJECTS} | working ${WORKING_COUNT} idle ${IDLE_COUNT} permission ${PERMISSION_COUNT} shell ${SHELL_COUNT} absent ${ABSENT_COUNT}"
TOKEN_HEADER="🧠 daily tokens ${TOKEN_DATE}: total $(format_token_count "$TOKEN_TOTAL") | input $(format_token_count "$TOKEN_INPUT") | cached $(format_token_count "$TOKEN_CACHED") | output $(format_token_count "$TOKEN_OUTPUT") | reasoning $(format_token_count "$TOKEN_REASONING")"
if [ -n "$TOKEN_TOP_WINDOW" ] && [ "$TOKEN_TOP_TOTAL" -gt 0 ]; then
    TOKEN_HEADER="${TOKEN_HEADER} | top ${TOKEN_TOP_WINDOW} $(format_token_count "$TOKEN_TOP_TOTAL")"
fi

ALL_STATUS_ENHANCED=("$REPORT_HEADER" "$TOKEN_HEADER")
for project_line in "${ALL_STATUS[@]}"; do
    ALL_STATUS_ENHANCED+=("$project_line")
done
SUMMARY_JSON=$(printf '%s\n' "${ALL_STATUS_ENHANCED[@]}" | jq -R . | jq -s .)

REPORT_JSON=$(jq -n \
  --arg generated_at "$REPORT_TS_UTC" \
  --arg generated_at_local "$REPORT_TS_LOCAL" \
  --argjson total_projects "$TOTAL_PROJECTS" \
  --argjson changed_projects "$CHANGED_COUNT" \
  --argjson working "$WORKING_COUNT" \
  --argjson idle "$IDLE_COUNT" \
  --argjson permission "$PERMISSION_COUNT" \
  --argjson shell "$SHELL_COUNT" \
  --argjson absent "$ABSENT_COUNT" \
  --argjson daily_tokens "$TOKEN_SUMMARY_JSON" \
  --argjson lifecycle_phase_counts "$PHASE_COUNTS_JSON" \
  --argjson review_status_counts "$REVIEW_STATUS_COUNTS_JSON" \
  --argjson progress "$PROGRESS_JSON" \
  '{generated_at:$generated_at,generated_at_local:$generated_at_local,counts:{total_projects:$total_projects,changed_projects:$changed_projects,working:$working,idle:$idle,permission:$permission,shell:$shell,absent:$absent},daily_tokens:$daily_tokens,lifecycle_phase_counts:$lifecycle_phase_counts,review_status_counts:$review_status_counts,progress:$progress}')

write_heartbeat_file() {
    local status="$1"
    local error="$2"
    jq -n \
      --arg lastStatus "$status" \
      --arg error "$error" \
      --arg wakeMode "now" \
      --arg generated_at "$REPORT_TS_UTC" \
      --argjson summary "$SUMMARY_JSON" \
      --argjson report "$REPORT_JSON" \
      '{lastStatus:$lastStatus,error:$error,wakeMode:$wakeMode,generated_at:$generated_at,summary:$summary,report:$report}' \
      > "$HEARTBEAT_FILE"
}

# --- 保底心跳：如果超过 2 小时没有任何变化，强制输出一次全局状态 ---
HEARTBEAT_FILE="$STATE_DIR/.last_report"
FORCE_REPORT=false
if [ -f "$HEARTBEAT_FILE" ]; then
    LAST_REPORT_AGE=$(( $(date +%s) - $(stat -f %m "$HEARTBEAT_FILE" 2>/dev/null || echo 0) ))
    [ "$LAST_REPORT_AGE" -ge 7200 ] && FORCE_REPORT=true
else
    FORCE_REPORT=true  # 首次运行
fi

# --- 输出 ---
if [ ${#CHANGES[@]} -eq 0 ] && ! $FORCE_REPORT; then
    write_heartbeat_file "skipped" "no changes"
    echo '{"changes":false}'
elif [ ${#CHANGES[@]} -eq 0 ] && $FORCE_REPORT; then
    write_heartbeat_file "ok" ""
    jq -n \
      --argjson summary "$SUMMARY_JSON" \
      --argjson daily_tokens "$TOKEN_SUMMARY_JSON" \
      --argjson report "$REPORT_JSON" \
      '{changes:true,heartbeat:true,projects:[],summary:$summary,daily_tokens:$daily_tokens,report:$report}'
else
    PROJECTS_JSON=$(printf '%s\n' "${CHANGES[@]}" | jq -s .)
    
    # 计算总进度信息
    TOTAL_COMMITS=0
    for entry in "${PROJECTS[@]}"; do
        D="${entry##*:}"
        C=$(cd "$D" && git rev-list --count HEAD 2>/dev/null || echo "0")
        TOTAL_COMMITS=$((TOTAL_COMMITS + C))
    done

    write_heartbeat_file "ok" ""
    jq -n \
      --argjson projects "$PROJECTS_JSON" \
      --argjson summary "$SUMMARY_JSON" \
      --argjson total_commits "$TOTAL_COMMITS" \
      --argjson daily_tokens "$TOKEN_SUMMARY_JSON" \
      --argjson report "$REPORT_JSON" \
      '{changes:true,projects:$projects,summary:$summary,total_commits:$total_commits,daily_tokens:$daily_tokens,report:$report}'
fi

# Layer 2: 消费 watchdog 写的增量 review trigger 文件
if ! $REPORT_ONLY && [ -x "${SCRIPT_DIR}/consume-review-trigger.sh" ]; then
    # 后台执行，不阻塞 monitor-all 的 JSON 输出
    "${SCRIPT_DIR}/consume-review-trigger.sh" >> "$HOME/.autopilot/logs/watchdog.log" 2>&1 &
elif $REPORT_ONLY; then
    >&2 echo "monitor-all: report-only mode active, skipping review trigger consumption"
fi
