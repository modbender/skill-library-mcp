#!/bin/bash
#
# Monitor Notify - 监控触发通知
# 当监控条件满足时发送通知并保存记录

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUECUE_BASE_URL="https://cuecue.cn"

# 参数检查
if [ $# -lt 3 ]; then
    echo "Usage: $0 <monitor_id> <chat_id> <message>"
    exit 1
fi

MONITOR_ID="$1"
CHAT_ID="$2"
MESSAGE="$3"

# 获取监控详情
get_monitor_info() {
    local monitor_id="$1"
    local chat_id="$2"
    local monitor_file="$HOME/.cuecue/users/$chat_id/monitors/${monitor_id}.json"
    
    if [ -f "$monitor_file" ]; then
        cat "$monitor_file"
    else
        echo '{}'
    fi
}

# 保存通知记录
save_notification() {
    local monitor_id="$1"
    local chat_id="$2"
    local message="$3"
    local monitor_info="$4"
    
    local notif_dir="$HOME/.cuecue/users/$chat_id/notifications"
    mkdir -p "$notif_dir"
    
    local timestamp
    timestamp=$(date +%s)
    
    local notif_file="${notif_dir}/${monitor_id}_${timestamp}.json"
    
    local monitor_title
    monitor_title=$(echo "$monitor_info" | jq -r '.title // "未命名监控"')
    
    local category
    category=$(echo "$monitor_info" | jq -r '.category // "Data"')
    
    local triggered_at
    triggered_at=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 构建通知记录
    cat > "$notif_file" << EOF
{
  "monitor_id": "$monitor_id",
  "monitor_title": "$monitor_title",
  "category": "$category",
  "message": "$message",
  "triggered_at": "$triggered_at",
  "timestamp": $timestamp
}
EOF
    
    echo "$notif_file"
}

# 发送消息（复用 notifier.sh 的逻辑）
send_message() {
    local chat_id="$1"
    local text="$2"
    local channel="${OPENCLAW_CHANNEL:-feishu}"
    
    # 优先尝试使用 openclaw
    if command -v openclaw &> /dev/null; then
        if echo "$text" | openclaw message send --channel "$channel" --target "$chat_id" 2>/dev/null; then
            return 0
        fi
    fi
    
    # 备用方案
    echo "$text"
}

# 获取监控信息
MONITOR_INFO=$(get_monitor_info "$MONITOR_ID" "$CHAT_ID")

# 保存通知记录
NOTIF_FILE=$(save_notification "$MONITOR_ID" "$CHAT_ID" "$MESSAGE" "$MONITOR_INFO")

# 提取监控标题
MONITOR_TITLE=$(echo "$MONITOR_INFO" | jq -r '.title // "未命名监控"')

# 构建通知消息
NOTIFICATION="🔔 监控触发提醒

📊 监控: ${MONITOR_TITLE}
⏰ 时间: $(date '+%Y-%m-%d %H:%M:%S')

${MESSAGE}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 使用 /cn 查看最近通知"

# 发送通知
send_message "$CHAT_ID" "$NOTIFICATION"
echo "✅ 监控触发通知已发送并保存"
