#!/bin/bash
# Codex TUI pane 监控器
# 用法: ./pane_monitor.sh <tmux-session-name>
# 后台运行，检测审批等待和任务完成，发送通知
#
# 配置：通过环境变量或修改下方默认值
#   CODEX_AGENT_CHAT_ID   — Chat ID (Telegram/Discord/WhatsApp etc.)
#   CODEX_AGENT_NAME      — OpenClaw agent 名称（默认 main）

set -uo pipefail

SESSION="${1:?Usage: $0 <tmux-session-name>}"
CHAT_ID="${CODEX_AGENT_CHAT_ID:-YOUR_CHAT_ID}"
AGENT_NAME="${CODEX_AGENT_NAME:-main}"
CHANNEL="${CODEX_AGENT_CHANNEL:-telegram}"
CHECK_INTERVAL=5  # 秒
LAST_STATE=""
NOTIFIED_APPROVAL=""
CAPTURE_LINES=30  # 抓取行数（增大以减少漏报）

LOG_FILE="/tmp/codex_monitor_${SESSION}.log"

log() { echo "[$(date '+%H:%M:%S')] $1" >> "$LOG_FILE"; }

# 清理函数：退出时删除 PID 文件
cleanup() {
    local pid_file="/tmp/codex_monitor_${SESSION}.pid"
    rm -f "$pid_file"
    log "Monitor exiting, cleaned up PID file"
}
trap cleanup EXIT

log "Monitor started for session: $SESSION"

while true; do
    # 检查 session 是否存在
    if ! tmux has-session -t "$SESSION" 2>/dev/null; then
        log "Session $SESSION gone, exiting"
        exit 0
    fi

    OUTPUT=$(tmux capture-pane -t "$SESSION" -p -S -"$CAPTURE_LINES" 2>/dev/null)

    # 检测审批等待
    if echo "$OUTPUT" | grep -q "Would you like to run\|Press enter to confirm\|approve this\|allow this"; then
        # 提取要执行的命令
        CMD=$(echo "$OUTPUT" | grep '^\s*\$' | tail -1 | sed 's/^\s*\$ //')
        STATE="approval:$CMD"

        if [ "$STATE" != "$NOTIFIED_APPROVAL" ]; then
            NOTIFIED_APPROVAL="$STATE"
            MSG="⏸️ Codex 等待审批
📋 命令: ${CMD:-unknown}
🔧 session: $SESSION"
            # 1. 通知用户
            if ! openclaw message send --channel "$CHANNEL" --target "$CHAT_ID" --message "$MSG" --silent 2>>"$LOG_FILE"; then
                log "⚠️ Telegram notify failed for approval"
            fi
            # 2. 唤醒 agent（后台执行，不阻塞 monitor 循环）
            AGENT_MSG="[Codex Monitor] 审批等待，请处理。
session: $SESSION
command: ${CMD:-unknown}
请 tmux send-keys -t $SESSION '1' Enter 批准，或 '3' Enter 拒绝。"
            openclaw agent --agent "$AGENT_NAME" --message "$AGENT_MSG" --deliver --channel "$CHANNEL" --timeout 120 2>>"$LOG_FILE" &
            WAKE_PID=$!
            log "Agent wake fired (pid $WAKE_PID)"
            log "Approval detected: $CMD"
        fi

    # 检测回到空闲（任务完成，? for shortcuts 出现）
    elif echo "$OUTPUT" | grep -q "? for shortcuts"; then
        if [ "$LAST_STATE" = "working" ]; then
            LAST_STATE="idle"
            NOTIFIED_APPROVAL=""
            # notify hook 已经处理 turn complete，这里不重复通知
            log "Back to idle"
        fi

    # 检测正在工作
    elif echo "$OUTPUT" | grep -q "esc to interrupt\|Thinking\|Creating\|Editing\|Running"; then
        LAST_STATE="working"
    fi

    sleep "$CHECK_INTERVAL"
done
