#!/bin/bash
# SSH Batch Manager - Systemd 服务管理脚本

SERVICE_NAME="ssh-batch-ui"

case "$1" in
    start)
        echo "🚀 启动 SSH Batch Manager Web UI..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "🛑 停止 SSH Batch Manager Web UI..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "🔄 重启 SSH Batch Manager Web UI..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    enable)
        echo "✅ 启用开机自启..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    disable)
        echo "❌ 禁用开机自启..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    logs)
        echo "📋 查看日志..."
        journalctl -u $SERVICE_NAME -f
        ;;
    *)
        echo "用法：$0 {start|stop|restart|status|enable|disable|logs}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看状态"
        echo "  enable  - 启用开机自启"
        echo "  disable - 禁用开机自启"
        echo "  logs    - 查看日志（实时）"
        exit 1
        ;;
esac

# 显示访问地址
if [ "$1" != "logs" ]; then
    echo ""
    echo "🌐 访问地址：http://localhost:8765"
fi
