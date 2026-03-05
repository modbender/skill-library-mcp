#!/bin/bash
# ClawHub 半自动化发布助手

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "═══════════════════════════════════════════════════════════"
echo "🚀 ClawHub 半自动化发布助手"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 使用 agent-browser 获取页面元素
echo "1️⃣ 使用 agent-browser 打开 ClawHub..."
agent-browser open https://clawhub.com/publish 2>&1

echo ""
echo "2️⃣ 获取页面元素..."
echo ""
agent-browser snapshot -i 2>&1 | tee /tmp/clawhub-elements.txt

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📋 操作指南"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 检查是否需要登录
if grep -q "Sign in" /tmp/clawhub-elements.txt; then
    echo "⚠️  需要先登录 GitHub"
    echo ""
    echo "步骤:"
    echo "1. 在打开的浏览器窗口中点击 'Sign in with GitHub'"
    echo "2. 完成 GitHub 授权登录"
    echo "3. 重新运行此脚本"
    echo ""
    echo "登录后，按回车继续..."
    read
    
    # 重新获取快照
    echo "重新获取页面..."
    agent-browser open https://clawhub.com/publish 2>&1
    sleep 2
    agent-browser snapshot -i 2>&1 | tee /tmp/clawhub-elements.txt
fi

echo ""
echo "📁 文件上传:"
echo "   文件: ~/Desktop/qqbot-v1.0.0.zip"
echo "   请手动拖拽或使用文件选择器上传"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "📋 表单信息（复制粘贴）"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "【名称】"
echo "qqbot"
echo ""
echo "【版本】"
echo "1.0.0"
echo ""
echo "【描述】"
cat << 'EOF'
QQ 官方机器人配置指南，包含完整部署流程和常见问题解决方案

一键配置 QQ 官方机器人，支持私聊、群聊、频道消息。

功能特点:
✅ WebSocket 实时连接
✅ 支持私聊、群聊、频道消息
✅ 内置 AI 处理器接口
✅ 完整的故障排除指南
✅ 自动 IP 白名单监控脚本

安装命令: openclaw skill install qqbot
EOF

echo ""
echo "【作者】"
echo "小皮"
echo ""
echo "【许可证】"
echo "MIT"
echo ""
echo "【标签】"
echo "qq, bot, im, 机器人, qq-bot"
echo ""
echo "【分类】"
echo "IM / 通讯"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ 信息已准备好，请在浏览器中手动填写并提交"
echo ""
echo "完成后，按回车关闭浏览器..."
read

agent-browser close 2>&1 || true

echo ""
echo "🎉 完成！"
