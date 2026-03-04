#!/bin/bash
# Stock Monitor 一键启动脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HOME/.stock_monitor"
PID_FILE="$LOG_DIR/monitor.pid"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "⚠️  监控进程已在运行 (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        echo "🚀 启动 Stock Monitor 后台进程..."
        mkdir -p "$LOG_DIR"
        nohup python3 "$SCRIPT_DIR/monitor_daemon.py" > "$LOG_DIR/monitor.log" 2>&1 &
        echo $! > "$PID_FILE"
        echo "✅ 已启动 (PID: $!)"
        echo "📋 日志: $LOG_DIR/monitor.log"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "🛑 停止监控进程 (PID: $PID)..."
                kill "$PID"
                rm "$PID_FILE"
                echo "✅ 已停止"
            else
                echo "⚠️  进程不存在"
                rm "$PID_FILE"
            fi
        else
            echo "⚠️  没有运行中的进程"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "✅ 监控运行中 (PID: $(cat $PID_FILE))"
            echo "📋 最近日志:"
            tail -5 "$LOG_DIR/monitor.log" 2>/dev/null || echo "  暂无日志"
        else
            echo "⏹️  监控未运行"
        fi
        ;;
        
    log)
        tail -f "$LOG_DIR/monitor.log"
        ;;
        
    *)
        echo "Stock Monitor 控制脚本"
        echo ""
        echo "用法: ./control.sh [start|stop|status|log]"
        echo ""
        echo "  start   - 启动后台监控"
        echo "  stop    - 停止监控"
        echo "  status  - 查看状态"
        echo "  log     - 查看实时日志"
        ;;
esac
