#!/bin/bash
# permission-guard.sh v3 — 权限提示守护进程
# 每 10 秒扫描所有 autopilot tmux 窗口，发现权限确认提示立即按 p Enter
#
# v3 修复：
# - 多行特征匹配（必须同时出现 "Press enter" + "(p)"）防误触发
# - 窗口名 sanitize 防路径注入
# - 与 auto-nudge.sh 共享锁目录
# - 冷却文件定期清理
# - subshell 内用 exit 替代 return

set -u
TMUX=/opt/homebrew/bin/tmux
SESSION="autopilot"
INTERVAL=10
COOLDOWN=60
LOG="$HOME/.autopilot/logs/permission-guard.log"
LOCK_DIR="$HOME/.autopilot/locks"
COOLDOWN_DIR="$HOME/.autopilot/state/permission-cooldown"
mkdir -p "$(dirname "$LOG")" "$LOCK_DIR" "$COOLDOWN_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

rotate_log() {
    local lines
    lines=$(wc -l < "$LOG" 2>/dev/null || echo 0)
    if [ "$lines" -gt 2000 ]; then
        tail -1000 "$LOG" > "${LOG}.tmp" && mv -f "${LOG}.tmp" "$LOG"
        log "📋 Log rotated (was ${lines} lines)"
    fi
    # 清理过期冷却文件
    find "$COOLDOWN_DIR" -type f -mtime +1 -delete 2>/dev/null
}

sanitize_name() {
    echo "$1" | tr -cd 'a-zA-Z0-9_-'
}

# 判断是否为真正的 Codex 权限对话框
# 必须同时满足两个特征才算（大幅降低误触发）：
#   1. 包含 "Press enter to confirm or esc to cancel"
#   2. 包含 "(p)" (permanent allow 选项)
is_permission_prompt() {
    local text="$1"
    echo "$text" | grep -qF "Press enter to confirm or esc to cancel" || return 1
    echo "$text" | grep -qF "(p)" || return 1
    return 0
}

is_in_cooldown() {
    local safe_name="$1"
    local cooldown_file="${COOLDOWN_DIR}/${safe_name}"
    if [ -f "$cooldown_file" ]; then
        local last_approve
        last_approve=$(cat "$cooldown_file" 2>/dev/null || echo 0)
        local now
        now=$(date +%s)
        if [ $((now - last_approve)) -lt "$COOLDOWN" ]; then
            return 0
        fi
    fi
    return 1
}

set_cooldown() {
    local safe_name="$1"
    date +%s > "${COOLDOWN_DIR}/${safe_name}"
}

check_and_approve() {
    local window="$1"
    local safe_name
    safe_name=$(sanitize_name "$window")

    # 跳过冷却中的窗口
    if is_in_cooldown "$safe_name"; then
        return
    fi

    # 只取最后 8 行，避免误匹配 pane 历史中的代码/文件内容
    local tail_content
    tail_content=$($TMUX capture-pane -t "${SESSION}:${window}" -p 2>/dev/null | tail -8) || return

    # 多行特征匹配
    if is_permission_prompt "$tail_content"; then
        # flock 防止与 auto-nudge.sh 同时操作同一窗口
        # 锁文件路径: ~/.autopilot/locks/<window>.lock（auto-nudge.sh 需使用同一路径）
        (
            flock -n 200 || { log "⏭ Skipped ${window} (locked)"; exit 0; }
            # 二次检查（拿到锁后 pane 可能已变）
            local recheck
            recheck=$($TMUX capture-pane -t "${SESSION}:${window}" -p 2>/dev/null | tail -8) || exit 0
            if is_permission_prompt "$recheck"; then
                $TMUX send-keys -t "${SESSION}:${window}" "p" Enter
                set_cooldown "$safe_name"
                log "✅ Auto-approved permission in ${window}"
            fi
        ) 200>"${LOCK_DIR}/${safe_name}.lock"
    fi
}

log "🚀 Permission guard v3 started (interval: ${INTERVAL}s, cooldown: ${COOLDOWN}s)"

cycle=0
while true; do
    windows=$($TMUX list-windows -t "$SESSION" -F '#{window_name}' 2>/dev/null) || {
        sleep "$INTERVAL"
        continue
    }

    while IFS= read -r window; do
        [ -n "$window" ] && check_and_approve "$window"
    done <<< "$windows"

    cycle=$((cycle + 1))
    if [ $((cycle % 100)) -eq 0 ]; then
        rotate_log
    fi

    sleep "$INTERVAL"
done
