#!/bin/bash
# SSH Batch Manager - 启动 Web UI

UI_FILE="/home/subline/.openclaw/workspace/skills/ssh-batch-manager/ssh-manager.html"

echo "🚀 SSH Batch Manager - Web UI"
echo ""
echo "📄 文件位置：$UI_FILE"
echo ""

# 检查文件是否存在
if [ ! -f "$UI_FILE" ]; then
    echo "❌ UI 文件不存在"
    exit 1
fi

# 尝试用默认浏览器打开
if command -v xdg-open &> /dev/null; then
    echo "🌐 使用默认浏览器打开..."
    xdg-open "$UI_FILE"
elif command -v gnome-open &> /dev/null; then
    gnome-open "$UI_FILE"
elif command -v open &> /dev/null; then
    open "$UI_FILE"
else
    echo "⚠️  未找到浏览器，请手动打开："
    echo ""
    echo "  file://$UI_FILE"
    echo ""
fi

echo ""
echo "💡 提示："
echo "  - 在浏览器中打开上述文件路径即可使用"
echo "  - 或者使用 OpenClaw browser 工具加载此页面"
