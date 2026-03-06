#!/bin/bash
# Browser Relay 启动脚本
# 用法: ./start.sh [--restart]

RELAY_DIR="$(cd "$(dirname "$0")" && pwd)"
RELAY_PID_FILE="/tmp/browser-relay.pid"
TOKEN_FILE="/tmp/browser-relay-token"
LOG_FILE="/tmp/relay.log"

# 停止已有进程（仅通过 PID 文件精确停止）
stop_relay() {
    if [ -f "$RELAY_PID_FILE" ]; then
        local pid=$(cat "$RELAY_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            # 等待进程退出，最多 5 秒
            for i in $(seq 1 10); do
                kill -0 "$pid" 2>/dev/null || break
                sleep 0.5
            done
            # 如果仍未退出，发送 SIGKILL
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            echo "已停止旧进程 (PID: $pid)"
        fi
        rm -f "$RELAY_PID_FILE"
    fi
}

# 检查 Chromium CDP 是否可用
check_cdp() {
    if curl -s --connect-timeout 2 "http://127.0.0.1:9222/json" > /dev/null 2>&1; then
        return 0
    else
        echo "⚠ Chromium CDP (端口 9222) 未就绪"
        echo "  请先启动 Chromium: chromium --remote-debugging-port=9222"
        return 1
    fi
}

case "${1:-start}" in
    stop)
        stop_relay
        echo "✓ Relay 已停止"
        exit 0
        ;;
    restart|--restart)
        stop_relay
        ;;
    start)
        # 检查是否已在运行
        if [ -f "$RELAY_PID_FILE" ] && kill -0 "$(cat "$RELAY_PID_FILE")" 2>/dev/null; then
            echo "Relay 已在运行 (PID: $(cat "$RELAY_PID_FILE"))"
            echo "Token: $(cat "$TOKEN_FILE" 2>/dev/null)"
            exit 0
        fi
        ;;
esac

# 前置检查
check_cdp || exit 1

# 启动
cd "$RELAY_DIR"
if [ -d "venv" ]; then
    source venv/bin/activate
fi

nohup python3 -u relay.py > "$LOG_FILE" 2>&1 &
RELAY_PID=$!
echo "$RELAY_PID" > "$RELAY_PID_FILE"

# 等待启动
sleep 2

if kill -0 "$RELAY_PID" 2>/dev/null; then
    TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null)
    echo "✓ Relay 已启动"
    echo "  PID:   $RELAY_PID"
    echo "  端口:  18792"
    echo "  Token: $TOKEN"
    echo "  日志:  $LOG_FILE"
else
    echo "✗ 启动失败，查看日志: $LOG_FILE"
    cat "$LOG_FILE"
    exit 1
fi
