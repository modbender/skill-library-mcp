#!/bin/bash
# 交互式 ClawHub 发布脚本 - 使用 agent-browser

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "═══════════════════════════════════════════════════════════"
echo "🚀 交互式 ClawHub 发布 - agent-browser"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 确保浏览器已关闭
agent-browser close 2>/dev/null || true

# 1. 打开 ClawHub
echo "1️⃣ 正在打开 ClawHub..."
agent-browser open https://clawhub.com/publish 2>&1
echo ""

# 2. 获取页面快照
echo "2️⃣ 获取页面元素..."
echo ""
agent-browser snapshot -i 2>&1 | tee /tmp/clawhub-snapshot.txt

echo ""

# 3. 检查是否需要登录
if grep -q "Sign in" /tmp/clawhub-snapshot.txt; then
    echo "═══════════════════════════════════════════════════════════"
    echo "⚠️  需要登录 GitHub"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "👤 请在浏览器窗口中完成以下操作："
    echo ""
    echo "   1. 点击 'Sign in with GitHub' 按钮"
    echo "   2. 在弹出的 GitHub 页面中登录并授权"
    echo "   3. 授权完成后回到 ClawHub 页面"
    echo ""
    echo "⏳ 完成后，请按回车键继续..."
    read
    
    # 重新获取快照
    echo ""
    echo "🔄 刷新页面..."
    agent-browser open https://clawhub.com/publish 2>&1
    sleep 2
    
    echo ""
    echo "📸 获取新页面元素..."
    agent-browser snapshot -i 2>&1 | tee /tmp/clawhub-snapshot.txt
    echo ""
fi

# 4. 查找表单元素
echo "═══════════════════════════════════════════════════════════"
echo "📋 准备填写表单"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 检查是否有文件上传输入框
if grep -q "file" /tmp/clawhub-snapshot.txt; then
    echo "✅ 找到文件上传区域"
    grep -i "file" /tmp/clawhub-snapshot.txt | head -3
else
    echo "⚠️  未找到文件上传区域，可能需要滚动或等待页面加载"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📄 表单信息（请复制到浏览器）"
echo "═══════════════════════════════════════════════════════════"
echo ""

cat << 'FORM'
【名称 / Name】
qqbot

【版本 / Version】
1.0.0

【作者 / Author】
小皮

【许可证 / License】
MIT

【标签 / Tags】（逐个添加）
qq
bot
im
机器人
qq-bot

【分类 / Category】
IM / 通讯

【描述 / Description】（复制全部）:
═══════════════════════════════════════════════════════════
QQ 官方机器人配置指南，包含完整部署流程和常见问题解决方案

一键配置 QQ 官方机器人，支持私聊、群聊、频道消息。

功能特点:
✅ WebSocket 实时连接
✅ 支持私聊、群聊、频道消息
✅ 内置 AI 处理器接口
✅ 完整的故障排除指南
✅ 自动 IP 白名单监控脚本

安装命令: openclaw skill install qqbot
═══════════════════════════════════════════════════════════

【文件 / File】
📁 ~/Desktop/qqbot-v1.0.0.zip (14K)
FORM

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ 操作指南"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. 在浏览器窗口中："
echo "   - 点击文件上传按钮"
echo "   - 选择 ~/Desktop/qqbot-v1.0.0.zip"
echo ""
echo "2. 复制上方表单信息，粘贴到对应字段"
echo ""
echo "3. 检查无误后，点击 'Submit' 或 '发布'"
echo ""
echo "⏳ 完成后，请按回车键关闭浏览器..."
read

echo ""
echo "🧹 关闭浏览器..."
agent-browser close 2>&1 || true

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎉 完成！"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ 发布后，你可以在 ClawHub 搜索 'qqbot' 查看"
echo ""
