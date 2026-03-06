#!/usr/bin/env bash
# 检查 OneBot plugin 状态
set -euo pipefail

PLUGIN_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/plugins/onebot"

echo "🔌 OneBot Plugin Status"
echo ""

# 检查安装
if [ -d "$PLUGIN_DIR" ]; then
  echo "✅ Installed: $PLUGIN_DIR"
  if [ -d "$PLUGIN_DIR/dist" ]; then
    echo "✅ Compiled: dist/ exists"
  else
    echo "❌ Not compiled: run 'cd $PLUGIN_DIR && npm run build'"
  fi
else
  echo "❌ Not installed"
  echo "   Run: bash $(dirname "$0")/install.sh"
  exit 1
fi

# 检查配置
if command -v openclaw &>/dev/null; then
  openclaw channels status 2>/dev/null | grep -i onebot || echo "⚠️ OneBot not configured in openclaw.json"
fi

# 检查 NapCat 连通性
WS_URL="${ONEBOT_WS_URL:-}"
HTTP_URL="${ONEBOT_HTTP_URL:-}"
if [ -n "$HTTP_URL" ]; then
  if curl -sf "${HTTP_URL}/get_login_info" -m 3 &>/dev/null; then
    echo "✅ NapCat HTTP API reachable: $HTTP_URL"
  else
    echo "⚠️ NapCat HTTP API unreachable: $HTTP_URL"
  fi
fi
