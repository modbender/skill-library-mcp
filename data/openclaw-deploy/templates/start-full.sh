#!/bin/bash
# OpenClaw Full Version Startup Script

SCRIPT="$(cd "$(dirname "$0")" && pwd)/openclaw"

# 查找 Node.js
if command -v node >/dev/null 2>&1; then
    NODE_CMD="node"
elif [ -x "$SCRIPT/../node/bin/node" ]; then
    NODE_CMD="$SCRIPT/../node/bin/node"
elif [ -x "$HOME/.nvm/versions/node/v22.22.0/bin/node" ]; then
    NODE_CMD="$HOME/.nvm/versions/node/v22.22.0/bin/node"
else
    echo "❌ 错误: 未找到 Node.js"
    echo "   请先安装 Node.js 22.x: ./install-node.sh"
    exit 1
fi

# 检查应用
if [ ! -f "$SCRIPT/app/openclaw.mjs" ]; then
    echo "❌ 错误: OpenClaw 应用文件不存在"
    exit 1
fi

export OPENCLAW_CONFIG="$SCRIPT/.openclaw/openclaw.json"

echo "🚀 启动 OpenClaw (完整版)..."
echo "   配置文件: $OPENCLAW_CONFIG"
echo "   Node.js: $NODE_CMD"
echo ""
exec "$NODE_CMD" "$SCRIPT/app/openclaw.mjs" gateway start "$@"
