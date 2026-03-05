#!/bin/bash
#
# Cue Research - 深度研究执行脚本 (v1.0.3)
# 使用内置 client.js，无需额外 npm 包
# 超时：60分钟 | 进度推送：每5分钟

set -e

# 配置
TIMEOUT=3600  # 60分钟
PROGRESS_INTERVAL=300  # 5分钟
CUECUE_BASE_URL="${CUECUE_BASE_URL:-https://cuecue.cn}"
CUECUE_API_KEY="${CUECUE_API_KEY}"

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_SCRIPT="$SCRIPT_DIR/cuecue-client.js"

# 日志配置
LOG_DIR="$HOME/.cuecue/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/research-$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# 参数检查
if [ $# -lt 2 ]; then
    echo "Usage: $0 <topic> <chat_id> [mode]"
    exit 1
fi

TOPIC="$1"
CHAT_ID="$2"
MODE="${3:-default}"

# 检查 API Key
if [ -z "$CUECUE_API_KEY" ]; then
    echo "❌ Error: CUECUE_API_KEY not set"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not installed"
    exit 1
fi

# 检查 client.js
if [ ! -f "$CLIENT_SCRIPT" ]; then
    echo "❌ Error: cuecue-client.js not found at $CLIENT_SCRIPT"
    exit 1
fi

# 生成任务ID
TASK_ID="cuecue_$(date +%s%N | cut -c1-16)"

log "=========================================="
log "🔬 启动深度研究: $TOPIC (模式: $MODE)"
log "   Chat ID: $CHAT_ID"
log "   Task ID: $TASK_ID"

# 保存任务信息
TASK_DIR="$HOME/.cuecue/users/$CHAT_ID/tasks"
mkdir -p "$TASK_DIR"
TASK_FILE="$TASK_DIR/$TASK_ID.json"

cat > "$TASK_FILE" << EOF
{
    "task_id": "$TASK_ID",
    "topic": "$TOPIC",
    "mode": "$MODE",
    "chat_id": "$CHAT_ID",
    "status": "running",
    "created_at": "$(date -Iseconds)",
    "progress": "初始化"
}
EOF

log "   任务文件: $TASK_FILE"

# 创建临时输出文件
TEMP_OUTPUT=$(mktemp)
log "   临时文件: $TEMP_OUTPUT"

# 临时文件不自动清理，由 notifier.sh 处理

# 启动 client.js 在后台运行
log "🚀 启动 client.js..."

# 使用 nohup 确保进程在后台稳定运行
nohup bash -c "
    CUECUE_API_KEY='$CUECUE_API_KEY' \
    CUECUE_BASE_URL='$CUECUE_BASE_URL' \
    timeout $TIMEOUT node '$CLIENT_SCRIPT' \
        '$TOPIC' \
        --mode '$MODE' \
        --verbose \
        > '$TEMP_OUTPUT' 2>&1
    EXIT_CODE=\$?
    echo \"===CLIENT_EXIT===\$EXIT_CODE\" >> '$TEMP_OUTPUT'
" > /dev/null 2>&1 &

# 获取后台进程组 ID（$! 返回的是最后一个后台进程的 PID）
NOHUP_PID=$!
sleep 0.5

# 查找实际的 node 进程 PID
# nohup 会启动一个 shell，我们需要找到 shell 下的 node 子进程
NODE_PID=""
for i in {1..10}; do
    NODE_PID=$(pgrep -P $NOHUP_PID -f "cuecue-client.js" | head -1)
    if [ -n "$NODE_PID" ]; then
        break
    fi
    sleep 0.2
done

# 如果找不到子进程，使用 nohup 的 PID
if [ -z "$NODE_PID" ]; then
    NODE_PID=$NOHUP_PID
fi

log "✅ Client 已启动 (nohup PID: $NOHUP_PID, node PID: $NODE_PID)"

# 等待并提取报告 URL
log "⏳ 等待报告 URL (最多60秒)..."
REPORT_URL=""
WAIT_COUNT=0
MAX_WAIT=60

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    
    # 检查是否已有输出
    if [ -s "$TEMP_OUTPUT" ]; then
        # 从 JSON_RESULT 中提取
        if grep -q "===JSON_RESULT===" "$TEMP_OUTPUT" 2>/dev/null; then
            REPORT_URL=$(grep -A1 "===JSON_RESULT===" "$TEMP_OUTPUT" | tail -1 | jq -r '.reportUrl // empty' 2>/dev/null)
            if [ -n "$REPORT_URL" ]; then
                log "   ✅ 从 JSON_RESULT 获取到 URL: $REPORT_URL"
                break
            fi
        fi
        
        # 备选：直接从输出中提取 cuecue.cn 链接
        if [ -z "$REPORT_URL" ]; then
            REPORT_URL=$(grep -oP 'https://cuecue\.cn/c/[^ ]+' "$TEMP_OUTPUT" | head -1)
            if [ -n "$REPORT_URL" ]; then
                log "   ✅ 从输出提取到 URL: $REPORT_URL"
                break
            fi
        fi
    fi
    
    # 检查进程是否还在运行
    if ! kill -0 $NODE_PID 2>/dev/null; then
        log "   ⚠️ Client 进程已退出 (等待 ${WAIT_COUNT}秒)"
        # 进程已退出，再检查一次输出
        if [ -s "$TEMP_OUTPUT" ]; then
            REPORT_URL=$(grep -oP 'https://cuecue\.cn/c/[^ ]+' "$TEMP_OUTPUT" | head -1)
            if [ -n "$REPORT_URL" ]; then
                log "   ✅ 从已退出进程的输出中提取到 URL: $REPORT_URL"
                break
            fi
        fi
        break
    fi
done

if [ -n "$REPORT_URL" ]; then
    # 更新任务文件
    jq --arg url "$REPORT_URL" '.report_url = $url | .status = "running"' "$TASK_FILE" > "$TASK_FILE.tmp" && mv "$TASK_FILE.tmp" "$TASK_FILE"
    
    log "✅ 研究启动成功"
    log "   主题: $TOPIC"
    log "   任务ID: $TASK_ID"
    log "   报告链接: $REPORT_URL"
    
    # 输出给用户
    echo "✅ 研究已启动"
    echo "   主题: $TOPIC"
    echo "   任务ID: $TASK_ID"
    echo "   报告链接: $REPORT_URL"
    echo ""
    echo "⏳ 预计耗时：5-30分钟"
    echo "🔔 完成后将自动通知您"
    
    # 启动 notifier 监控进程
    log "🚀 启动 notifier (监控 PID: $NODE_PID)..."
    nohup "$SCRIPT_DIR/notifier.sh" "$TASK_ID" "$CHAT_ID" "$NODE_PID" "$TEMP_OUTPUT" >> "$LOG_DIR/notifier-error.log" 2>&1 &
    NOTIFIER_PID=$!
    log "   Notifier PID: $NOTIFIER_PID"
    
    # 验证 notifier 是否成功启动
    sleep 1
    if kill -0 $NOTIFIER_PID 2>/dev/null; then
        log "   ✅ Notifier 启动成功"
    else
        log "   ❌ Notifier 启动失败，检查 $LOG_DIR/notifier-error.log"
    fi
    
    # 保存 PID 到任务文件
    jq --arg pid "$NODE_PID" --arg npid "$NOTIFIER_PID" \
        '.research_pid = $pid | .notifier_pid = $npid' "$TASK_FILE" > "$TASK_FILE.tmp" && mv "$TASK_FILE.tmp" "$TASK_FILE"
    
    log "=========================================="
    exit 0
else
    log "❌ 无法获取报告 URL"
    
    # 检查 client 输出
    if [ -s "$TEMP_OUTPUT" ]; then
        log "   Client 输出内容:"
        head -20 "$TEMP_OUTPUT" | while read line; do
            log "   > $line"
        done
    else
        log "   Client 无输出"
    fi
    
    # 更新任务状态为失败
    jq '.status = "failed" | .error = "无法获取报告URL"' "$TASK_FILE" > "$TASK_FILE.tmp" && mv "$TASK_FILE.tmp" "$TASK_FILE"
    
    echo "❌ 研究启动失败：无法获取报告链接"
    
    # 清理进程
    kill $NODE_PID 2>/dev/null || true
    
    log "=========================================="
    exit 1
fi
