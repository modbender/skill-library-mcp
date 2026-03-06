#!/bin/bash
# OpenClaw 内置浏览器 Skill - 快速安装脚本

echo "========================================"
echo "OpenClaw 内置浏览器 Skill - 安装"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "browser_toggle.py" ]; then
    echo "❌ 请在 Skill 目录下运行此脚本"
    echo "   cd /home/ereala/.openclaw/workspace/skills/browser-toggle"
    exit 1
fi

# 设置执行权限
echo "📋 设置执行权限..."
chmod +x browser_toggle.py
chmod +x install.sh

# 创建符号链接（可选）
echo ""
echo "📁 创建全局命令..."
if [ -w "/usr/local/bin" ]; then
    ln -sf "$(pwd)/browser_toggle.py" /usr/local/bin/openclaw-browser
    echo "✅ 已创建全局命令：openclaw-browser"
else
    echo "⚠️ 无法创建全局命令（需要 sudo）"
    echo "   可以使用完整路径运行："
    echo "   $(pwd)/browser_toggle.py --enable"
fi

# 测试
echo ""
echo "🧪 测试安装..."
python3 browser_toggle.py --status

echo ""
echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo ""
echo "使用方法："
echo "  启用内置浏览器：python3 browser_toggle.py --enable"
echo "  禁用内置浏览器：python3 browser_toggle.py --disable"
echo "  查看状态：python3 browser_toggle.py --status"
echo ""
echo "或（如果创建了全局命令）："
echo "  openclaw-browser --enable"
echo "  openclaw-browser --disable"
echo "  openclaw-browser --status"
echo ""
echo "========================================"
