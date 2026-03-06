#!/bin/bash
# tmux-send.sh v5 — 向 autopilot tmux pane 发送消息并按 Enter
# 用法:
#   tmux-send.sh [--track|--no-track] [--source <source>] [--source-channel <channel_id>] <window_name> <message>
#
# v5: 三级发送策略 + 验证 + 重试
#   Level 1: send-keys -l (≤300 字符，最可靠)
#   Level 2: 分块 send-keys (≤800 字符，每 100 字符一块 + 50ms 延迟)
#   Level 3: paste-buffer -p (bracketed paste mode，>800 字符)
#   所有级别: 发送后验证 prompt 是否包含消息前缀，失败则降级重试
#
# v4: paste-buffer 无 bracketed paste，TUI 框架不识别 → 消息丢失
# v3: 长消息 paste-buffer（有 bug），短消息 send-keys

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/autopilot-lib.sh"

TMUX="${TMUX_BIN:-$(command -v tmux || echo /opt/homebrew/bin/tmux)}"
SESSION="autopilot"
TRACK_ENABLED="auto"
TRACK_SOURCE=""
TRACK_SOURCE_CHANNEL=""

usage() {
    echo "用法: tmux-send.sh [--track|--no-track] [--source <source>] [--source-channel <channel_id>] <window> <message>" >&2
}

resolve_track_enabled() {
    # auto 模式下：从 autopilot 脚本内部触发默认不追踪，人工/外部触发默认追踪。
    if [ "$TRACK_ENABLED" = "true" ] || [ "$TRACK_ENABLED" = "false" ]; then
        return 0
    fi

    local parent_cmd
    parent_cmd=$(ps -p "$PPID" -o command= 2>/dev/null || true)
    if echo "$parent_cmd" | grep -q '/\.autopilot/scripts/'; then
        TRACK_ENABLED=false
    else
        TRACK_ENABLED=true
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --track)
            TRACK_ENABLED=true
            shift
            ;;
        --no-track)
            TRACK_ENABLED=false
            shift
            ;;
        --source)
            shift || true
            TRACK_SOURCE="${1:-}"
            [ -n "$TRACK_SOURCE" ] || { echo "ERROR: --source 缺少参数" >&2; usage; exit 1; }
            shift
            ;;
        --source-channel)
            shift || true
            TRACK_SOURCE_CHANNEL="${1:-}"
            [ -n "$TRACK_SOURCE_CHANNEL" ] || { echo "ERROR: --source-channel 缺少参数" >&2; usage; exit 1; }
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "ERROR: 未知参数: $1" >&2
            usage
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

resolve_track_enabled

WINDOW="${1:?用法: tmux-send.sh <window> <message>}"
MESSAGE="${2:?缺少消息参数}"
LOCK_DIR="$HOME/.autopilot/locks"
STATE_DIR="$HOME/.autopilot/state"
mkdir -p "$LOCK_DIR" "$STATE_DIR"

# ---- 配置 ----
MAX_DIRECT=300          # send-keys -l 直发上限（中文 ~100 字）
MAX_CHUNKED=800         # 分块 send-keys 上限
CHUNK_SIZE=100          # 每块字符数
CHUNK_DELAY=0.2         # 块间延迟（秒）— 200ms 防 TUI 乱码
VERIFY_WAIT=0.5         # 发送后等待验证的时间（秒）
VERIFY_PREFIX_LEN=20    # 验证时取消息前 N 字符匹配
MAX_RETRIES=2           # 最大重试次数（含降级）
PRE_SEND_PANE=""

log() {
    echo "[tmux-send $(date '+%H:%M:%S')] $*" >&2
}

resolve_project_dir_for_window() {
    local target_window="$1"
    local config_yaml="${AUTOPILOT_CONFIG_FILE:-$HOME/.autopilot/config.yaml}"
    local fallback_conf="$HOME/.autopilot/watchdog-projects.conf"
    local entry w d

    while IFS= read -r entry || [ -n "$entry" ]; do
        [ -n "$entry" ] || continue
        w="${entry%%:*}"
        d="${entry#*:}"
        [ "$d" = "$entry" ] && continue
        if [ "$w" = "$target_window" ]; then
            echo "$d"
            return 0
        fi
    done < <(autopilot_load_projects_entries "$config_yaml" "$fallback_conf" 2>/dev/null || true)

    return 1
}

resolve_head_before_for_window() {
    local target_window="$1"
    local safe_window="$2"
    local head="" project_dir="" head_file=""

    project_dir=$(resolve_project_dir_for_window "$target_window" 2>/dev/null || true)
    if [ -n "$project_dir" ]; then
        head=$(git -C "$project_dir" rev-parse HEAD 2>/dev/null || true)
    fi

    if ! [[ "$head" =~ ^[0-9a-f]{7,40}$ ]]; then
        head_file="${STATE_DIR}/watchdog-commits/${safe_window}-head"
        head=$(cat "$head_file" 2>/dev/null || echo "")
    fi

    if [[ "$head" =~ ^[0-9a-f]{7,40}$ ]]; then
        echo "$head"
    else
        echo "none"
    fi
}

persist_tracked_task() {
    local task_text="$1"
    local tracked_file="${STATE_DIR}/tracked-task-${SAFE_WINDOW}.json"
    local tracked_tmp="${tracked_file}.tmp"
    local source="${TRACK_SOURCE}"
    local source_channel="${TRACK_SOURCE_CHANNEL}"
    local mapped_channel mapped_channel_id
    local head_before started_at

    # 未显式指定来源时，优先按窗口自动推导 Discord 来源信息。
    if [ -z "$source" ] || [ -z "$source_channel" ]; then
        mapped_channel=$(get_discord_channel_for_window "$WINDOW" 2>/dev/null || true)
        if [ -n "$mapped_channel" ]; then
            [ -n "$source" ] || source="discord:#${mapped_channel}"
            if [ -z "$source_channel" ]; then
                mapped_channel_id=$(get_discord_channel_id_for_channel "$mapped_channel" 2>/dev/null || true)
                source_channel="$mapped_channel_id"
            fi
        fi
    fi
    [ -n "$source" ] || source="manual:tmux-send"
    started_at=$(now_ts)
    head_before=$(resolve_head_before_for_window "$WINDOW" "$SAFE_WINDOW")

    if command -v jq >/dev/null 2>&1; then
        jq -n \
            --arg task "$task_text" \
            --arg source "$source" \
            --arg source_channel "$source_channel" \
            --arg head_before "$head_before" \
            --arg window "$WINDOW" \
            --argjson started_at "$started_at" \
            '{
                task: $task,
                source: $source,
                source_channel: $source_channel,
                window: $window,
                head_before: $head_before,
                started_at: $started_at,
                status: "in-progress"
            }' > "$tracked_tmp" \
            && mv -f "$tracked_tmp" "$tracked_file"
    else
        log "jq 不可用，跳过 tracked-task 写入"
    fi
}

SAFE_WINDOW="$(sanitize "$WINDOW")"
[ -n "$SAFE_WINDOW" ] || SAFE_WINDOW="window"
SEND_LOCK="${LOCK_DIR}/tmux-send-${SAFE_WINDOW}.lock.d"

build_buffer_name() {
    local ts_ns
    ts_ns=$(date +%s%N 2>/dev/null || date +%s)
    ts_ns=$(echo "$ts_ns" | tr -dc '0-9')
    [ -n "$ts_ns" ] || ts_ns=$(date +%s)
    echo "autopilot-msg-${SAFE_WINDOW}-$$-${ts_ns}-${RANDOM}"
}

acquire_send_lock() {
    if mkdir "$SEND_LOCK" 2>/dev/null; then
        echo "$$" > "${SEND_LOCK}/pid"
        return 0
    fi

    # 10s 超时自动过期（防死锁）
    local lock_age=0
    if [ -d "$SEND_LOCK" ]; then
        lock_age=$(( $(date +%s) - $(file_mtime "$SEND_LOCK") ))
    fi
    if [ "$lock_age" -gt 10 ]; then
        rm -rf "$SEND_LOCK" 2>/dev/null || true
        mkdir "$SEND_LOCK" 2>/dev/null || return 1
        echo "$$" > "${SEND_LOCK}/pid"
        return 0
    fi

    return 1
}

if ! acquire_send_lock; then
    echo "ERROR: send lock busy for window '$WINDOW'" >&2
    exit 3
fi

TMPFILE=""
BUFFER_NAME=""
cleanup() {
    if [ -n "$BUFFER_NAME" ]; then
        "$TMUX" delete-buffer -b "$BUFFER_NAME" >/dev/null 2>&1 || true
    fi
    if [ -n "$TMPFILE" ] && [ -f "$TMPFILE" ]; then
        rm -f "$TMPFILE"
    fi
    rm -rf "$SEND_LOCK" 2>/dev/null || true
}
trap cleanup EXIT

# ---- 前置检查 ----
if ! "$TMUX" has-session -t "$SESSION" 2>/dev/null; then
    echo "ERROR: tmux session '$SESSION' 不存在" >&2
    exit 1
fi

if ! "$TMUX" list-windows -t "$SESSION" -F '#{window_name}' | grep -qx "$WINDOW"; then
    echo "ERROR: window '$WINDOW' 不存在" >&2
    exit 1
fi

# ---- 检测 codex 是否在运行（子进程树检查，非 pane_current_command）----
PANE_PID=$("$TMUX" list-panes -t "${SESSION}:${WINDOW}" -F '#{pane_pid}' | head -1)
_tmux_send_has_codex() {
    # BFS 全量子进程树搜索（与 codex-status.sh 一致）
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
if [ -n "$PANE_PID" ] && ! _tmux_send_has_codex "$PANE_PID"; then
    echo "ERROR: window '$WINDOW' 中 codex 未运行 (pane PID $PANE_PID 子进程树无 codex)，跳过发送" >&2
    exit 2
fi

capture_pre_send_snapshot() {
    PRE_SEND_PANE=$("$TMUX" capture-pane -t "${SESSION}:${WINDOW}" -p 2>/dev/null | tail -8)
}

# ---- 消息预处理 ----
SINGLE_LINE=$(echo "$MESSAGE" | tr '\n' ' ' | tr '\r' ' ' | sed 's/  */ /g; s/^ *//; s/ *$//')
MSG_LEN=${#SINGLE_LINE}

# ---- 验证函数：检查消息是否进入了 Codex prompt ----
verify_message_received() {
    # 两轮验证：快速检查 + 延迟检查
    # Codex TUI 可能立即开始处理，prompt 内容消失很快
    local attempt
    for attempt in 1 2; do
        if [ "$attempt" -eq 1 ]; then
            sleep "$VERIFY_WAIT"
        else
            sleep 1.0  # 第二轮等久一点，让 TUI 有时间显示状态
        fi
        
        local pane_content
        pane_content=$("$TMUX" capture-pane -t "${SESSION}:${WINDOW}" -p 2>/dev/null | tail -8)
        
        # 检查 1: 消息前缀还在 prompt 中（还没被提交）
        local prefix="${SINGLE_LINE:0:$VERIFY_PREFIX_LEN}"
        if echo "$pane_content" | grep -qF "$prefix"; then
            return 0
        fi
        
        # 检查 2: Codex 已经开始处理（说明消息已被接收并提交）
        if echo "$pane_content" | grep -qE '(esc to interrupt|Working|Thinking|Exploring|Ran |Reading|Searching|Analyzed|Preparing)'; then
            return 0
        fi
        
        # 检查 3: prompt 变化（需要与发送前快照不同，避免空 › 行误判）
        local prompt_line pre_prompt_line
        prompt_line=$(echo "$pane_content" | grep -E '^[[:space:]]*›' | tail -1 || true)
        pre_prompt_line=$(echo "$PRE_SEND_PANE" | grep -E '^[[:space:]]*›' | tail -1 || true)
        if [ -n "$prompt_line" ] \
            && [ "$pane_content" != "$PRE_SEND_PANE" ] \
            && [ "$prompt_line" != "$pre_prompt_line" ] \
            && ! echo "$prompt_line" | grep -qF "$prefix"; then
            return 0
        fi
    done
    
    return 1  # 两轮都未确认
}

# ---- Level 1: send-keys 直发 ----
send_direct() {
    log "Level 1: send-keys 直发 (${MSG_LEN} 字符)"
    capture_pre_send_snapshot
    "$TMUX" send-keys -t "${SESSION}:${WINDOW}" -l -- "$SINGLE_LINE"
    sleep 0.2
    "$TMUX" send-keys -t "${SESSION}:${WINDOW}" Enter
}

# ---- Level 2: 分块 send-keys ----
send_chunked() {
    log "Level 2: 分块 send-keys (${MSG_LEN} 字符, 块大小 ${CHUNK_SIZE})"
    capture_pre_send_snapshot
    local offset=0
    local remaining="$MSG_LEN"
    
    while [ "$offset" -lt "$MSG_LEN" ]; do
        local chunk="${SINGLE_LINE:$offset:$CHUNK_SIZE}"
        "$TMUX" send-keys -t "${SESSION}:${WINDOW}" -l -- "$chunk"
        offset=$((offset + CHUNK_SIZE))
        
        # 块间延迟，让 TUI 有时间处理输入缓冲
        if [ "$offset" -lt "$MSG_LEN" ]; then
            sleep "$CHUNK_DELAY"
        fi
    done
    
    sleep 0.2
    "$TMUX" send-keys -t "${SESSION}:${WINDOW}" Enter
}

# ---- Level 3: paste-buffer (bracketed paste mode) ----
send_paste_buffer() {
    log "Level 3: paste-buffer -p bracketed paste (${MSG_LEN} 字符)"
    capture_pre_send_snapshot
    TMPFILE=$(mktemp /tmp/tmux-paste.XXXXXX)
    printf '%s' "$SINGLE_LINE" > "$TMPFILE"
    
    BUFFER_NAME=$(build_buffer_name)
    "$TMUX" load-buffer -b "$BUFFER_NAME" "$TMPFILE"
    
    # -p = bracketed paste mode (发送 \e[200~ ... \e[201~ 序列)
    # 这让 TUI 框架正确识别为粘贴操作而非逐键输入
    "$TMUX" paste-buffer -b "$BUFFER_NAME" -t "${SESSION}:${WINDOW}" -d -p
    BUFFER_NAME=""
    
    sleep 0.5
    "$TMUX" send-keys -t "${SESSION}:${WINDOW}" Enter
    
    rm -f "$TMPFILE"
    TMPFILE=""
}

# ---- 主发送逻辑：三级策略 + 验证 + 重试 ----
send_success=false

# 安全重试：只在 Codex 确实没收到消息时才重试，避免发重复消息
safe_retry() {
    local level="$1"
    # 先检查 Codex 是否已经在工作（说明消息已收到，只是验证时机问题）
    local pane_now
    pane_now=$("$TMUX" capture-pane -t "${SESSION}:${WINDOW}" -p 2>/dev/null | tail -5)
    if echo "$pane_now" | grep -qE '(esc to interrupt|Working|Thinking|Exploring|Ran |Reading)'; then
        log "Codex 已在工作状态，消息已被接收（验证时机偏差）"
        send_success=true
        return 0
    fi
    # Codex 确实还在 idle，准备重试（不发 C-u，ink TUI 不支持）
    log "Level ${level} 验证失败且 Codex 仍 idle，准备重试"
    sleep 0.3
    return 1  # 需要重试
}

if [ "$MSG_LEN" -le "$MAX_DIRECT" ]; then
    # 短消息：Level 1 直发
    send_direct
    if verify_message_received; then
        send_success=true
    elif ! safe_retry 1; then
        send_chunked  # 降级到 Level 2
        if verify_message_received; then
            send_success=true
        else
            safe_retry 2 && send_success=true
        fi
    fi

elif [ "$MSG_LEN" -le "$MAX_CHUNKED" ]; then
    # 中等消息：Level 2 分块
    send_chunked
    if verify_message_received; then
        send_success=true
    elif ! safe_retry 2; then
        send_paste_buffer  # 降级到 Level 3
        if verify_message_received; then
            send_success=true
        else
            safe_retry 3 && send_success=true
        fi
    fi

else
    # 超长消息：Level 3 paste-buffer (bracketed)
    send_paste_buffer
    if verify_message_received; then
        send_success=true
    elif ! safe_retry 3; then
        # 截断到 MAX_CHUNKED 用 Level 2 重试
        log "截断到 ${MAX_CHUNKED} 字符重试"
        SINGLE_LINE="${SINGLE_LINE:0:$MAX_CHUNKED}"
        MSG_LEN=${#SINGLE_LINE}
        send_chunked
        if verify_message_received; then
            send_success=true
        else
            safe_retry 4 && send_success=true
        fi
    fi
fi

# ---- 结果输出 ----
if $send_success; then
    echo "OK: 已发送 ${MSG_LEN} 字符到 ${SESSION}:${WINDOW}"
    # 兼容旧逻辑：保留 manual-task 标记，供 watchdog 的 nudge 保护使用。
    date +%s > "${STATE_DIR}/manual-task-${SAFE_WINDOW}"
    # 新逻辑：把手动消息纳入 tracked-task 追踪。
    if [ "$TRACK_ENABLED" = "true" ]; then
        persist_tracked_task "$SINGLE_LINE"
    fi
    exit 0
else
    log "ERROR: 验证未通过，发送结果未确认"
    echo "ERROR: 发送 ${MSG_LEN} 字符到 ${SESSION}:${WINDOW} 失败（未通过验证）" >&2
    exit 4
fi
