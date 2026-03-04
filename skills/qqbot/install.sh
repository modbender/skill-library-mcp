#!/bin/bash
# QQ Bot 快速安装脚本

echo "🤖 QQ 官方机器人安装脚本"
echo "=========================="
echo ""

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import requests, aiohttp, websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装依赖..."
    pip3 install requests aiohttp websockets --user -q
fi
echo "✅ 依赖检查完成"
echo ""

# 创建工作目录
WORKSPACE="$HOME/.openclaw/workspace"
mkdir -p "$WORKSPACE/qq_queue"

echo "📁 复制文件到工作区..."
cp qq_official_bot.py "$WORKSPACE/"
cp qq_bot_daemon.sh "$WORKSPACE/"
cp qq_ai_handler.sh "$WORKSPACE/"
chmod +x "$WORKSPACE/qq_bot_daemon.sh"
chmod +x "$WORKSPACE/qq_ai_handler.sh"

echo "✅ 文件复制完成"
echo ""

# 配置提示
echo "⚙️  配置步骤:"
echo "1. 编辑 $WORKSPACE/qq_official_bot.py"
echo "   设置 APP_ID 和 APP_SECRET"
echo ""
echo "2. 确保已在 QQ 开放平台配置 IP 白名单"
echo "   访问: https://bot.q.qq.com/console/"
echo ""
echo "3. 启动机器人:"
echo "   $WORKSPACE/qq_bot_daemon.sh start"
echo ""
echo "4. 启动 AI 处理器 (可选):"
echo "   $WORKSPACE/qq_ai_handler.sh"
echo ""
echo "📖 详细说明请查看 SKILL.md"
