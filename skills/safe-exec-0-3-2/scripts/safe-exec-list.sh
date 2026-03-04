#!/bin/bash
# safe-exec-list - 列出所有待处理的批准请求

SAFE_EXEC_DIR="$HOME/.openclaw/safe-exec"
PENDING_DIR="$SAFE_EXEC_DIR/pending"

if [[ ! -d "$PENDING_DIR" ]]; then
    echo "没有待处理的请求"
    exit 0
fi

REQUESTS=("$PENDING_DIR"/*.json)

if [[ ! -e "${REQUESTS[0]}" ]]; then
    echo "没有待处理的请求"
    exit 0
fi

echo "📋 待处理的批准请求："
echo ""

for request_file in "${REQUESTS[@]}"; do
    if [[ -f "$request_file" ]]; then
        request_id=$(basename "$request_file" .json)
        command=$(jq -r '.command' "$request_file")
        risk=$(jq -r '.risk' "$request_file")
        reason=$(jq -r '.reason' "$request_file")
        timestamp=$(jq -r '.timestamp' "$request_file")
        time_str=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "未知时间")
        
        echo "📌 请求 ID: $request_id"
        echo "   风险: ${risk^^}"
        echo "   命令: $command"
        echo "   原因: $reason"
        echo "   时间: $time_str"
        echo ""
    fi
done

echo "批准命令: safe-exec-approve <request_id>"
echo "拒绝命令: safe-exec-reject <request_id>"
