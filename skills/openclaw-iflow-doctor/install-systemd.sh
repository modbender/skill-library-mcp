#!/bin/bash

# OpenClaw iFlow Doctor systemd 服务安装脚本
# Bug #2 修复：添加开机自启功能

set -e

SERVICE_FILE="openclaw-iflow-doctor.service"
SERVICE_DEST="/etc/systemd/system/$SERVICE_FILE"

echo "=== OpenClaw iFlow Doctor systemd 服务安装 ==="

# 检查是否 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 复制服务文件
echo "复制服务文件到 $SERVICE_DEST..."
cp "$SERVICE_FILE" "$SERVICE_DEST"

# 重载 systemd
echo "重载 systemd 配置..."
systemctl daemon-reload

# 启用服务（开机自启）
echo "启用服务（开机自启）..."
systemctl enable openclaw-iflow-doctor

# 启动服务
echo "启动服务..."
systemctl start openclaw-iflow-doctor

# 检查状态
echo ""
echo "=== 服务状态 ==="
systemctl status openclaw-iflow-doctor --no-pager

echo ""
echo "=== 安装完成 ==="
echo "常用命令："
echo "  systemctl status openclaw-iflow-doctor  # 查看状态"
echo "  systemctl stop openclaw-iflow-doctor    # 停止服务"
echo "  systemctl start openclaw-iflow-doctor   # 启动服务"
echo "  journalctl -u openclaw-iflow-doctor -f  # 查看日志"
