#!/bin/bash
# 小红书 MCP 环境检查脚本
# 用法: bash ~/.openclaw/skills/xiaohongshu/check_env.sh

MCP_URL="${XHS_MCP_URL:-http://localhost:18060/mcp}"
MCP_BIN=~/xiaohongshu-mcp/xiaohongshu-mcp-linux-amd64

echo "=== 1. 检查 MCP 是否安装 ==="
if [ -x "$MCP_BIN" ]; then
  echo "✅ MCP 已安装"
else
  echo "❌ MCP 未安装，请先执行安装流程"
  exit 1
fi

echo "=== 2. 检查 Xvfb 虚拟显示 ==="
if systemctl is-active --quiet xvfb 2>/dev/null; then
  echo "✅ Xvfb 服务运行中 (systemd)"
elif pgrep -x Xvfb > /dev/null; then
  echo "✅ Xvfb 运行中 (手动)"
else
  echo "⚠️ Xvfb 未运行，尝试启动 systemd 服务..."
  systemctl start xvfb 2>/dev/null
  sleep 1
  if systemctl is-active --quiet xvfb 2>/dev/null; then
    echo "✅ Xvfb 服务已启动"
  else
    echo "⚠️ systemd 服务不存在，手动启动..."
    Xvfb :99 -screen 0 1920x1080x24 &
    sleep 1
    echo "✅ Xvfb 已启动（非守护模式）"
  fi
fi

echo "=== 3. 检查 MCP 服务是否运行 ==="
if systemctl is-active --quiet xhs-mcp 2>/dev/null; then
  echo "✅ MCP 服务运行中 (systemd 守护)"
elif pgrep -f xiaohongshu-mcp-linux > /dev/null; then
  echo "✅ MCP 服务运行中 (手动)"
else
  echo "⚠️ MCP 服务未运行，尝试启动 systemd 服务..."
  systemctl start xhs-mcp 2>/dev/null
  sleep 2
  if systemctl is-active --quiet xhs-mcp 2>/dev/null; then
    echo "✅ MCP 服务已启动 (systemd)"
  else
    echo "⚠️ systemd 服务不存在，手动启动..."
    cd ~/xiaohongshu-mcp && DISPLAY=:99 nohup ./xiaohongshu-mcp-linux-amd64 > mcp.log 2>&1 &
    sleep 3
    if pgrep -f xiaohongshu-mcp-linux > /dev/null; then
      echo "✅ MCP 服务已启动（非守护模式）"
    else
      echo "❌ MCP 服务启动失败，请检查 ~/xiaohongshu-mcp/mcp.log"
      exit 1
    fi
  fi
fi

echo "=== 4. 检查生图 API 配置 ==="
IMG_API_TYPE="${IMG_API_TYPE:-gemini}"
IMG_OK=false

case "$IMG_API_TYPE" in
  gemini)
    if [ -n "${GEMINI_API_KEY:-}" ]; then
      echo "✅ Gemini API Key 已配置 (IMG_API_TYPE=gemini)"
      IMG_OK=true
    else
      echo "❌ Gemini API Key 未配置（需设置 GEMINI_API_KEY）"
    fi
    ;;
  openai)
    if [ -n "${IMG_API_KEY:-}" ]; then
      echo "✅ OpenAI 兼容 API Key 已配置 (IMG_API_TYPE=openai, BASE=${IMG_API_BASE:-https://api.openai.com/v1})"
      IMG_OK=true
    else
      echo "❌ OpenAI 兼容 API Key 未配置（需设置 IMG_API_KEY）"
    fi
    ;;
  hunyuan)
    if [ -n "${HUNYUAN_SECRET_ID:-}" ] && [ -n "${HUNYUAN_SECRET_KEY:-}" ]; then
      echo "✅ 腾讯云混元 API 已配置 (IMG_API_TYPE=hunyuan)"
      IMG_OK=true
    else
      echo "❌ 腾讯云混元 API 未配置（需设置 HUNYUAN_SECRET_ID 和 HUNYUAN_SECRET_KEY）"
    fi
    ;;
  *)
    echo "⚠️ 未知的 IMG_API_TYPE: $IMG_API_TYPE（支持 gemini/openai/hunyuan）"
    ;;
esac

# 如果当前类型未配置，检查是否有其他可用的
if [ "$IMG_OK" = false ]; then
  FALLBACKS=""
  [ -n "${GEMINI_API_KEY:-}" ] && FALLBACKS="${FALLBACKS} gemini(GEMINI_API_KEY)"
  [ -n "${IMG_API_KEY:-}" ] && FALLBACKS="${FALLBACKS} openai(IMG_API_KEY)"
  [ -n "${HUNYUAN_SECRET_ID:-}" ] && [ -n "${HUNYUAN_SECRET_KEY:-}" ] && FALLBACKS="${FALLBACKS} hunyuan(HUNYUAN_SECRET_ID+KEY)"
  if [ -n "$FALLBACKS" ]; then
    echo "💡 检测到其他可用的生图 API:$FALLBACKS"
    echo "   可通过 export IMG_API_TYPE=xxx 切换"
  else
    echo "⚠️ 未配置任何生图 API，封面生成功能不可用"
    echo "   请设置以下任一组环境变量："
    echo "   - GEMINI_API_KEY（推荐）"
    echo "   - IMG_API_KEY + IMG_API_BASE"
    echo "   - HUNYUAN_SECRET_ID + HUNYUAN_SECRET_KEY"
  fi
fi

echo "=== 5. 检查登录状态 ==="
SESSION_ID=$(curl -s -D /tmp/xhs_headers -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"openclaw","version":"1.0"}},"id":1}' > /dev/null && grep -i 'Mcp-Session-Id' /tmp/xhs_headers | tr -d '\r' | awk '{print $2}')

curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' > /dev/null

LOGIN_RESULT=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"check_login_status","arguments":{}},"id":2}')

echo "$LOGIN_RESULT"

if echo "$LOGIN_RESULT" | grep -q "未登录"; then
  echo "❌ 未登录，需要扫码登录"
  exit 2
else
  echo "✅ 已登录，可以正常使用"
  exit 0
fi
