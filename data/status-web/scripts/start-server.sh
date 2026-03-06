#!/bin/bash
# 小雨 Bot 状态监测页面启动脚本

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$SKILL_DIR/assets"

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

# 检查 server.js 是否存在
if [ ! -f "$ASSETS_DIR/server.js" ]; then
    echo "错误: 未找到 server.js 文件"
    exit 1
fi

# 启动服务器
echo "正在启动小雨 Bot 状态监测页面..."
echo "服务器文件: $ASSETS_DIR/server.js"
echo "静态资源目录: $ASSETS_DIR"
echo "访问地址: http://localhost:8888"

cd "$ASSETS_DIR"
exec node server.js