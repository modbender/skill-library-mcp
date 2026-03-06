#!/bin/bash
#
# Cue Notifier - 研究完成通知脚本 (v1.0.3)
# 简化版：直接展示主题、耗时和报告链接

set -e

# 参数检查
if [ $# -lt 4 ]; then
    echo "Usage: $0 <task_id> <chat_id> <research_pid> <output_file>"
    exit 1
fi

TASK_ID="$1"
CHAT_ID="$2"
RESEARCH_PID="$3"
OUTPUT_FILE="$4"
CUECUE_BASE_URL="https://cuecue.cn"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 日志配置
LOG_DIR="$HOME/.cuecue/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/notifier-$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 获取任务信息
get_task_info() {
    local task_file="$HOME/.cuecue/users/$CHAT_ID/tasks/$TASK_ID.json"
    
    # 使用 >&2 避免 log 输出混入函数返回值
    log "   查找任务文件: $task_file" >&2
    
    if [ ! -f "$task_file" ]; then
        # 尝试其他可能的 chat_id 格式
        local alt_task_file="$HOME/.cuecue/users/default/tasks/$TASK_ID.json"
        if [ -f "$alt_task_file" ]; then
            log "   找到任务文件(alt): $alt_task_file" >&2
            cat "$alt_task_file"
            return 0
        fi
        
        # 列出所有可能的任务文件位置
        log "   ⚠️ 任务文件未找到，搜索所有位置..." >&2
        find "$HOME/.cuecue/users" -name "$TASK_ID.json" 2>/dev/null | while read f; do
            log "   找到: $f" >&2
        done
        
        echo "Error: Task not found: $TASK_ID" >&2
        return 1
    fi
    
    log "   找到任务文件: $task_file" >&2
    cat "$task_file"
}

# 检查研究是否完成
check_research_complete() {
    local pid="$1"
    local output_file="$2"
    
    # 检查进程是否还在运行
    if kill -0 $pid 2>/dev/null; then
        # 进程还在运行
        return 1
    else
        # 进程已退出
        return 0
    fi
}

# 从输出中提取报告 URL
extract_report_url() {
    local output_file="$1"
    
    if grep -q "===JSON_RESULT===" "$output_file" 2>/dev/null; then
        local json_result
        json_result=$(grep -A1 "===JSON_RESULT===" "$output_file" | tail -1)
        echo "$json_result" | jq -r '.reportUrl // empty'
    else
        # 尝试从输出中直接提取 cuecue.cn 链接
        grep -oP 'https://cuecue\.cn/c/[^ ]+' "$output_file" | head -1
    fi
}

# 发送消息
send_message() {
    local chat_id="$1"
    local text="$2"
    local channel="${OPENCLAW_CHANNEL:-feishu}"
    
    # 确保 chat_id 格式正确（处理 user: 前缀）
    if [[ "$chat_id" == user:* ]]; then
        chat_id="${chat_id#user:}"
    fi
    
    log "📤 Sending notification to $chat_id"
    log "   消息长度: ${#text} 字符"
    
    # 方法1: 使用 OpenClaw 的 message 工具（通过标准输入）
    log "   方法1: 尝试使用 message 工具..."
    
    # 创建临时消息文件
    local msg_file="/tmp/notifier_msg_${TASK_ID}_$(date +%s).txt"
    echo "$text" > "$msg_file"
    
    # 检查 message 命令是否可用
    if command -v message &> /dev/null; then
        log "     message 命令可用"
        local send_result
        send_result=$(message action=send target="$chat_id" < "$msg_file" 2>&1)
        local send_status=$?
        
        log "     message 返回状态: $send_status"
        log "     message 返回结果: ${send_result:0:200}"
        
        if [ $send_status -eq 0 ] && echo "$send_result" | grep -qE '"ok":true|sent|success|messageId'; then
            log "✓ Notification sent successfully via message tool"
            rm -f "$msg_file"
            return 0
        else
            log "     ⚠️ message 工具发送失败"
        fi
    else
        log "     message 命令不可用"
    fi
    
    # 方法2: 尝试使用环境变量中的 OpenClaw socket
    if [ -n "$OPENCLAW_MESSAGE_SOCKET" ]; then
        log "   方法2: 尝试使用 OpenClaw socket..."
        if [ -S "$OPENCLAW_MESSAGE_SOCKET" ]; then
            log "     Socket 存在: $OPENCLAW_MESSAGE_SOCKET"
            if echo '{"action":"send","target":"'"$chat_id"'","message":"'"$(cat "$msg_file")"'"}' | nc -U "$OPENCLAW_MESSAGE_SOCKET" 2>/dev/null; then
                log "✓ Notification sent via socket"
                rm -f "$msg_file"
                return 0
            else
                log "     ⚠️ Socket 发送失败"
            fi
        else
            log "     Socket 不存在: $OPENCLAW_MESSAGE_SOCKET"
        fi
    else
        log "     OPENCLAW_MESSAGE_SOCKET 未设置"
    fi
    
    # 方法3: 直接写入 OpenClaw 的消息队列
    log "   方法3: 尝试直接写入消息队列..."
    local queue_dir="${OPENCLAW_WORKSPACE:-$HOME/.openclaw}/message-queue"
    if [ -d "$queue_dir" ]; then
        local queue_file="$queue_dir/${TASK_ID}_$(date +%s).json"
        jq -n --arg chat_id "$chat_id" --arg text "$text" \
            '{target: $chat_id, message: $text, timestamp: now}' > "$queue_file"
        log "     ✓ 消息已写入队列: $queue_file"
        rm -f "$msg_file"
        return 0
    else
        log "     消息队列目录不存在: $queue_dir"
    fi
    
    # 备用：保存到本地通知队列
    log "   备用: 保存到本地通知队列..."
    local notification_file="$LOG_DIR/notifications/${TASK_ID}_$(date +%s).txt"
    mkdir -p "$(dirname "$notification_file")"
    {
        echo "TIME: $(date -Iseconds)"
        echo "CHANNEL: $channel"
        echo "CHAT_ID: $chat_id"
        echo "STATUS: queued"
        echo "---"
        cat "$msg_file"
    } > "$notification_file"
    log "✓ Notification saved to local queue: $notification_file"
    
    rm -f "$msg_file"
    return 0  # 返回成功，因为消息已保存
}

# 发送完成通知（带监控建议）
send_completion_notification() {
    local topic="$1"
    local report_url="$2"
    local elapsed="$3"
    
    local minutes=$((elapsed / 60))
    
    # 生成监控建议
    log "   生成监控建议..."
    local suggestion_file="/tmp/monitor_suggest_${TASK_ID}.json"
    "$SCRIPT_DIR/generate-monitor-suggestion.sh" "$report_url" "$topic" "$suggestion_file" >/dev/null 2>&1 || true
    
    # 读取监控建议（如果生成成功）
    local suggestion_text=""
    if [ -f "$suggestion_file" ]; then
        local monitor_title
        monitor_title=$(jq -r '.title // ""' "$suggestion_file" 2>/dev/null)
        local monitor_trigger
        monitor_trigger=$(jq -r '.semantic_trigger // ""' "$suggestion_file" 2>/dev/null)
        local monitor_reason
        monitor_reason=$(jq -r '.reason_for_user // ""' "$suggestion_file" 2>/dev/null)
        
        if [ -n "$monitor_title" ]; then
            suggestion_text="

📊 建议监控：${monitor_title}
🔔 触发条件：${monitor_trigger}
💡 原因：${monitor_reason}"
        fi
    fi
    
    # 构建消息
    local message="✅ 研究完成：${topic}

⏱️ 耗时：${minutes} 分钟
🔗 ${report_url}${suggestion_text}

💡 回复 Y 创建此监控，或描述你的监控需求"
    
    send_message "$CHAT_ID" "$message"
}

# 发送失败通知
send_failure_notification() {
    local topic="$1"
    local reason="${2:-未知错误}"
    
    local message="❌ 研究失败：${topic}

原因：${reason}

请稍后重试或联系管理员"
    
    send_message "$CHAT_ID" "$message"
}

# 更新任务状态
update_task_completed() {
    local report_url="$1"
    local task_file="$HOME/.cuecue/users/$CHAT_ID/tasks/$TASK_ID.json"
    
    if [ -f "$task_file" ]; then
        local completed_at
        completed_at=$(date -Iseconds)
        jq --arg url "$report_url" --arg time "$completed_at" \
            '.status = "completed" | .report_url = $url | .completed_at = $time | .notified = true' \
            "$task_file" > "$task_file.tmp" && mv "$task_file.tmp" "$task_file"
    fi
}

update_task_failed() {
    local reason="$1"
    local task_file="$HOME/.cuecue/users/$CHAT_ID/tasks/$TASK_ID.json"
    
    if [ -f "$task_file" ]; then
        jq --arg reason "$reason" \
            '.status = "failed" | .error = $reason' \
            "$task_file" > "$task_file.tmp" && mv "$task_file.tmp" "$task_file"
    fi
}

# 主逻辑
main() {
    log "📤 开始监控任务: $TASK_ID"
    log "   CHAT_ID: $CHAT_ID"
    log "   RESEARCH_PID: $RESEARCH_PID"
    log "   OUTPUT_FILE: $OUTPUT_FILE"
    
    # 检查环境
    log "   环境检查:"
    log "     OPENCLAW_CHANNEL: ${OPENCLAW_CHANNEL:-未设置}"
    log "     HOME: $HOME"
    
    # 获取任务信息
    local task_info
    task_info=$(get_task_info)
    
    if [ $? -ne 0 ]; then
        log "❌ 无法获取任务信息，退出"
        exit 1
    fi
    
    local topic
    topic=$(echo "$task_info" | jq -r '.topic // "unknown"')
    
    local created_at
    created_at=$(echo "$task_info" | jq -r '.created_at // empty')
    
    log "   主题: $topic"
    log "   创建时间: $created_at"
    log "   监控 PID: $RESEARCH_PID"
    
    # 轮询等待研究完成
    local check_interval=10  # 每10秒检查一次
    local max_wait=3600      # 最大等待1小时
    local elapsed=0
    
    while [ $elapsed -lt $max_wait ]; do
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
        
        if check_research_complete "$RESEARCH_PID"; then
            log "✅ 研究进程已结束"
            
            # 检查退出码
            local exit_code
            if grep -q "===CLIENT_EXIT===0" "$OUTPUT_FILE" 2>/dev/null; then
                exit_code=0
            else
                exit_code=1
            fi
            
            if [ $exit_code -eq 0 ]; then
                local report_url
                report_url=$(extract_report_url "$OUTPUT_FILE")
                
                if [ -n "$report_url" ]; then
                    # 计算总耗时
                    local total_elapsed
                    total_elapsed=$(($(date +%s) - $(date -d "$created_at" +%s)))
                    
                    # 发送完成通知
                    send_completion_notification "$topic" "$report_url" "$total_elapsed"
                    
                    # 更新任务状态
                    update_task_completed "$report_url"
                    
                    log "✅ 通知已发送"
                else
                    log "⚠️ 无法提取报告 URL"
                    send_failure_notification "$topic" "无法获取报告链接"
                    update_task_failed "无法获取报告链接"
                fi
            else
                log "❌ 研究进程异常退出"
                send_failure_notification "$topic" "研究进程异常退出"
                update_task_failed "进程异常退出"
            fi
            
            exit 0
        fi
        
        # 每5分钟记录一次日志
        if [ $((elapsed % 300)) -eq 0 ]; then
            log "⏳ 等待中... 已等待 ${elapsed}秒"
        fi
    done
    
    # 超时
    log "⏱️ 监控超时"
    send_failure_notification "$topic" "研究超时（超过1小时）"
    update_task_failed "超时"
    exit 1
}

# 执行
main
