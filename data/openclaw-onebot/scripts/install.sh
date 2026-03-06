#!/usr/bin/env bash
# OpenClaw OneBot 11 Plugin — 安装脚本
# Install script for OneBot 11 channel plugin
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/plugins/onebot"

echo "📦 Installing OpenClaw OneBot plugin..."

# 创建插件目录
mkdir -p "$PLUGIN_DIR"

# 复制源码
cp -r "$SKILL_DIR"/src "$PLUGIN_DIR"/
cp "$SKILL_DIR"/index.ts "$PLUGIN_DIR"/
cp "$SKILL_DIR"/package.json "$PLUGIN_DIR"/
cp "$SKILL_DIR"/package-lock.json "$PLUGIN_DIR"/
cp "$SKILL_DIR"/tsconfig.json "$PLUGIN_DIR"/

# 安装依赖并编译
cd "$PLUGIN_DIR"
npm install --omit=dev 2>/dev/null
npm run build 2>/dev/null

echo "✅ OneBot plugin installed to $PLUGIN_DIR"
echo ""
echo "📝 Next steps:"
echo "   1. Add to openclaw.json:"
echo '      "channels": { "onebot": { "enabled": true, "wsUrl": "ws://your-host:port", "httpUrl": "http://your-host:port" } }'
echo "   2. Restart gateway: openclaw gateway restart"
