#!/bin/bash
# OpenClaw AI 实时消息处理器
# 监控 QQ Bot 发来的 AI 请求并回复

QUEUE_DIR="$HOME/.openclaw/workspace/qq_queue"

echo "🤖 OpenClaw AI 实时处理器已启动"
echo "📁 监控目录: $QUEUE_DIR"
echo "💡 收到消息后会立即显示，输入回复后按 Enter 发送"
echo ""

mkdir -p "$QUEUE_DIR"

while true; do
    # 查找新的 AI 请求
    for request_file in "$QUEUE_DIR"/ai_request_*.json; do
        [ -e "$request_file" ] || continue
        
        # 读取消息
        username=$(cat "$request_file" | python3 -c "import json,sys; print(json.load(sys.stdin).get('username','用户'))")
        message=$(cat "$request_file" | python3 -c "import json,sys; print(json.load(sys.stdin).get('message',''))")
        request_id=$(cat "$request_file" | python3 -c "import json,sys; print(json.load(sys.stdin).get('request_id',''))")
        
        echo ""
        echo "═══════════════════════════════════════════"
        echo "💬 [QQ消息] $username: $message"
        echo "═══════════════════════════════════════════"
        echo ""
        echo "🤖 请输入回复 (直接输入，按 Enter 发送):"
        
        # 读取回复
        read -r reply
        
        if [ -n "$reply" ]; then
            # 写入回复文件
            response_file="$QUEUE_DIR/ai_response_${request_id}.txt"
            echo "$reply" > "$response_file"
            echo "✅ 回复已发送!"
        else
            echo "⚠️ 回复为空，跳过"
        fi
        
        # 删除请求文件
        rm -f "$request_file"
        echo ""
    done
    
    sleep 1
done
