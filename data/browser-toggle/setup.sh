#!/bin/bash
# OpenClaw Browser Toggle Skill - 标准安装脚本
# 用法：bash setup.sh [安装目录]

set -e

SKILL_NAME="browser-toggle"
SKILL_VERSION="1.0.0"
INSTALL_DIR="${1:-$HOME/.openclaw/workspace/skills/$SKILL_NAME}"

echo "========================================"
echo "OpenClaw Browser Toggle Skill v$SKILL_VERSION"
echo "========================================"
echo ""
echo "📁 安装目录：$INSTALL_DIR"
echo ""

# 检查 OpenClaw 是否安装
if [ ! -d "$HOME/.openclaw" ]; then
    echo "❌ 未检测到 OpenClaw 安装"
    echo "   请先安装 OpenClaw: https://github.com/openclaw/openclaw"
    exit 1
fi

# 创建安装目录
echo "📋 创建安装目录..."
mkdir -p "$INSTALL_DIR"

# 复制文件
echo "📦 复制文件..."
cp -r "$(dirname "$0")"/* "$INSTALL_DIR/"

# 设置执行权限
echo "🔧 设置执行权限..."
chmod +x "$INSTALL_DIR/browser_toggle.py"
chmod +x "$INSTALL_DIR/install.sh"
chmod +x "$INSTALL_DIR/setup.sh" 2>/dev/null || true

# 创建符号链接（可选）
echo ""
echo "🔗 创建全局命令..."
if [ -w "/usr/local/bin" ]; then
    ln -sf "$INSTALL_DIR/browser_toggle.py" /usr/local/bin/openclaw-browser
    echo "✅ 已创建全局命令：openclaw-browser"
else
    echo "⚠️  无法创建全局命令（需要 sudo）"
    echo "   可以使用完整路径运行："
    echo "   $INSTALL_DIR/browser_toggle.py --enable"
fi

# 测试安装
echo ""
echo "🧪 测试安装..."
python3 "$INSTALL_DIR/browser_toggle.py" --status

# 显示使用说明
echo ""
echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo ""
echo "使用方法："
echo "  启用内置浏览器：$INSTALL_DIR/browser_toggle.py --enable"
echo "  禁用内置浏览器：$INSTALL_DIR/browser_toggle.py --disable"
echo "  查看状态：$INSTALL_DIR/browser_toggle.py --status"
echo ""
echo "启用后需要重启 OpenClaw："
echo "  openclaw gateway restart"
echo ""
echo "详细文档：$INSTALL_DIR/README.md"
echo "使用指南：$INSTALL_DIR/使用指南.md"
echo ""
echo "========================================"
