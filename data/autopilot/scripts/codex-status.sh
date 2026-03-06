#!/bin/bash
# codex-status.sh v3 — 确定性检测 Codex TUI 状态
# 用法: codex-status.sh <window_name>
# 输出 JSON: {"status":"<state>","context":"XX%","context_num":N,...}
# 状态: working | idle | idle_low_context | permission | permission_with_remember | shell | absent
# Exit codes: 0=working, 1=idle/permission, 2=shell, 3=absent/error

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
    echo '{"status":"'"${CODEX_STATE_ABSENT:-absent}"'","detail":"jq not found"}'
    exit 3
fi

TMUX="${TMUX_BIN:-$(command -v tmux || echo /opt/homebrew/bin/tmux)}"
SESSION="autopilot"
WINDOW="${1:?用法: codex-status.sh <window>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/autopilot-constants.sh" ]; then
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/autopilot-constants.sh"
fi
LOW_CONTEXT_THRESHOLD="${LOW_CONTEXT_THRESHOLD:-25}"
CODEX_STATE_WORKING="${CODEX_STATE_WORKING:-working}"
CODEX_STATE_IDLE="${CODEX_STATE_IDLE:-idle}"
CODEX_STATE_IDLE_LOW_CONTEXT="${CODEX_STATE_IDLE_LOW_CONTEXT:-idle_low_context}"
CODEX_STATE_PERMISSION="${CODEX_STATE_PERMISSION:-permission}"
CODEX_STATE_PERMISSION_WITH_REMEMBER="${CODEX_STATE_PERMISSION_WITH_REMEMBER:-permission_with_remember}"
CODEX_STATE_SHELL="${CODEX_STATE_SHELL:-shell}"
CODEX_STATE_ABSENT="${CODEX_STATE_ABSENT:-absent}"
MANUAL_BLOCK_REGEX="${MANUAL_BLOCK_REGEX:-BLOCKED[^│]*|manual[^│]*|人工[^│]*|需要证书[^│]*|证书[^│]*|签名[^│]*|certificate[^│]*|signing[^│]*|cert[^│]*}"

WEEKLY_LIMIT_PCT=-1
MANUAL_BLOCK_REASON=""

emit_json() {
    local status="$1" extra_args=()
    shift
    # Remaining args are --arg key value pairs
    while [ $# -ge 2 ]; do
        extra_args+=(--arg "$1" "$2")
        shift 2
    done
    jq -n \
      --arg status "$status" \
      --arg context "$CONTEXT" \
      --argjson context_num "$CONTEXT_NUM" \
      --argjson weekly_limit_pct "$WEEKLY_LIMIT_PCT" \
      --arg manual_block_reason "$MANUAL_BLOCK_REASON" \
      "${extra_args[@]}" \
      '{status:$status,context:$context,context_num:$context_num,weekly_limit_pct:$weekly_limit_pct,manual_block_reason:$manual_block_reason} + ($ARGS.named | del(.status,.context,.context_num,.weekly_limit_pct,.manual_block_reason) | to_entries | map({(.key):.value}) | add // {})' 2>/dev/null
}

# ---- 基础检查 ----
if ! "$TMUX" has-session -t "$SESSION" 2>/dev/null; then
    echo "{\"status\":\"${CODEX_STATE_ABSENT}\",\"detail\":\"tmux session not found\"}"
    exit 3
fi

if ! "$TMUX" list-windows -t "$SESSION" -F '#{window_name}' | grep -qFx "$WINDOW"; then
    echo "{\"status\":\"${CODEX_STATE_ABSENT}\",\"detail\":\"window not found\"}"
    exit 3
fi

# ---- Shell 检测: 用子进程树替代 pane_current_command ----
# pane_current_command 只报告 tmux pane 的顶层进程（总是 zsh），
# 但 Codex 作为 zsh 的子进程运行: zsh → zsh → node → codex
# 所以改为检查 pane PID 的子进程树中是否有 codex/node 进程
PANE_PID=$("$TMUX" list-panes -t "${SESSION}:${WINDOW}" -F '#{pane_pid}' | head -1)

_has_codex_child() {
    # 检查 pane_pid 全量子进程树，避免深层 zsh/node/codex 链路漏检
    local root_pid="$1"
    local queue="$root_pid"
    local current_pid children cpid cmd

    while [ -n "$queue" ]; do
        current_pid="${queue%% *}"
        if [ "$queue" = "$current_pid" ]; then
            queue=""
        else
            queue="${queue#* }"
        fi

        children=$(pgrep -P "$current_pid" 2>/dev/null || true)
        [ -z "$children" ] && continue
        for cpid in $children; do
            cmd=$(ps -p "$cpid" -o comm= 2>/dev/null || true)
            # codex binary 名为 codex 或通过 node 运行
            if [[ "$cmd" == *codex* || "$cmd" == "node" ]]; then
                return 0
            fi
            if [ -z "$queue" ]; then
                queue="$cpid"
            else
                queue="${queue} ${cpid}"
            fi
        done
    done
    return 1
}

if [ -n "$PANE_PID" ] && ! _has_codex_child "$PANE_PID"; then
    # 子进程树中没有 codex — 再 double-check pane 内容是否有 TUI 特征
    PANE_PEEK=$("$TMUX" capture-pane -t "${SESSION}:${WINDOW}" -p -S -5 2>&1 || true)
    if ! echo "$PANE_PEEK" | grep -qE "context left|esc to interrupt|esc to cancel|›"; then
        echo "{\"status\":\"${CODEX_STATE_SHELL}\",\"detail\":\"no codex process in pane $PANE_PID subtree\"}"
        exit 2
    fi
fi

# ---- 捕获 pane 输出 ----
PANE=$("$TMUX" capture-pane -t "${SESSION}:${WINDOW}" -p -S -25 2>&1)

# ---- 提取 context ----
CONTEXT=$(echo "$PANE" | grep -o '[0-9]*% context left' | tail -1 | grep -o '[0-9]*%' || echo "unknown")
CONTEXT_NUM=$(echo "$CONTEXT" | tr -d '%')
# 安全处理：非数字时设为 -1（标记为 unknown）
if ! [[ "$CONTEXT_NUM" =~ ^[0-9]+$ ]]; then
    CONTEXT_NUM=-1
fi

# Weekly limit 文案会随 TUI 版本变动，做多模式匹配并取最后一条
WEEKLY_LIMIT_LINE=$(echo "$PANE" | grep -iE 'weekly[[:space:]_-]*(limit|usage|quota)|((limit|usage|quota)[[:space:]_-]*weekly)' | tail -1 || true)
if [ -n "$WEEKLY_LIMIT_LINE" ]; then
    LIMIT_PCT=$(echo "$WEEKLY_LIMIT_LINE" | grep -oE '[0-9]{1,3}[[:space:]]*%' | tail -1 | tr -dc '0-9')
    if [[ "$LIMIT_PCT" =~ ^[0-9]+$ ]]; then
        WEEKLY_LIMIT_PCT="$LIMIT_PCT"
    fi
fi
MANUAL_BLOCK_REASON=$(echo "$PANE" | grep -oEi "$MANUAL_BLOCK_REGEX" | head -1 | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | head -c 120 || true)

# ============================================================
# 检测 1: "esc to interrupt" — 100% 确定性工作中标志
# ============================================================
if echo "$PANE" | grep -qE "esc to interrupt"; then
    LAST_ACTIVITY=$(echo "$PANE" | grep -oE "• [A-Z][^ │(]*[^│(]*" | tail -1 | head -c 120 || echo "")
    emit_json "$CODEX_STATE_WORKING" "last_activity" "$LAST_ACTIVITY"
    exit 0
fi

# ---- 取活动区域（跳过底栏）----
ACTIVITY_LINES=$(echo "$PANE" | tail -15 | head -12)

# ============================================================
# 检测 2: "• <Verb>" 活动行
#   a) 通用后缀: (ing|ed|te|d|ote) + 空格
#   b) 不规则动词白名单: Ran, Wrote, Read, Built, Sent, Found, Made, Took, Set, Got, Put, Did
#   c) 独立动词 + └ 树形输出
#   d) 特殊短语
# ============================================================

# 2a + 2b: 通用 + 不规则（容忍 Thinking... / 小写首字母 / 冒号等）
if echo "$ACTIVITY_LINES" | grep -qiE "^  ?• (([A-Za-z][a-z]+(ing|ed|te|d|ote)([ :].*|[.]{3}|…|$))|(ran|wrote|read|set|got|put|did|built|sent|found|made|took)([ :].*|$))"; then
    LAST_ACTIVITY=$(echo "$ACTIVITY_LINES" | grep -oE "• [^│]{1,120}" | tail -1 | head -c 120 || echo "")
    emit_json "$CODEX_STATE_WORKING" "last_activity" "$LAST_ACTIVITY"
    exit 0
fi

# 2c: 独立动词行 + 下一行有 └（容忍 Thinking...）
if echo "$ACTIVITY_LINES" | grep -qiE "^  ?• [A-Za-z][a-z]+([.]{3}|…)?$" && echo "$ACTIVITY_LINES" | grep -qE "^ +└"; then
    LAST_ACTIVITY=$(echo "$ACTIVITY_LINES" | grep -oE "• [^│]{1,120}" | tail -1 | head -c 120 || echo "")
    emit_json "$CODEX_STATE_WORKING" "last_activity" "$LAST_ACTIVITY"
    exit 0
fi

# 2d: 特殊短语
if echo "$ACTIVITY_LINES" | grep -qE "^  ?• (Context compacted|Waiting for background|Compacting context)"; then
    LAST_ACTIVITY=$(echo "$ACTIVITY_LINES" | grep -oE "• (Context compacted|Waiting for background|Compacting context)" | tail -1 | head -c 120 || echo "")
    emit_json "$CODEX_STATE_WORKING" "last_activity" "$LAST_ACTIVITY"
    exit 0
fi

# ============================================================
# 检测 3: 权限确认
# ============================================================
if echo "$ACTIVITY_LINES" | grep -qiE "Yes, proceed|Press +enter +to +confirm|don't ask again|Allow once|Allow always|Esc to cancel"; then
    if echo "$ACTIVITY_LINES" | grep -qiE "don't ask again|Allow always"; then
        emit_json "$CODEX_STATE_PERMISSION_WITH_REMEMBER" "detail" "can permanently allow"
    else
        emit_json "$CODEX_STATE_PERMISSION" "detail" "waiting for permission"
    fi
    exit 1
fi

# ============================================================
# 检测 4: 空转 — 区分低 context 和正常
# ============================================================
PROMPT_LINE=$(echo "$PANE" | grep "^›" | tail -1 | head -c 120 || echo "")

# context unknown 时不触发 compact（可能 TUI 还没渲染完），当普通 idle
if [ "$CONTEXT_NUM" -ge 1 ] && [ "$CONTEXT_NUM" -le "$LOW_CONTEXT_THRESHOLD" ]; then
    emit_json "$CODEX_STATE_IDLE_LOW_CONTEXT" "prompt" "$PROMPT_LINE"
    exit 1
fi

emit_json "$CODEX_STATE_IDLE" "prompt" "$PROMPT_LINE"
exit 1
