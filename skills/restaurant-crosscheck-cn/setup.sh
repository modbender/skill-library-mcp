#!/bin/bash
set -e

echo ""
echo "🔧 本地生活交叉验证工具 — 一键安装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.8+，请先安装"
    exit 1
fi
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python ${PYTHON_VERSION}"

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
pip3 install playwright thefuzz --break-system-packages 2>/dev/null || pip3 install playwright thefuzz

# 安装浏览器
echo ""
echo "🌐 安装 Chromium 浏览器（约 200MB）..."
python3 -m playwright install chromium

# 创建会话目录
mkdir -p ~/.local/share/restaurant-crosscheck/sessions/dianping
mkdir -p ~/.local/share/restaurant-crosscheck/sessions/xiaohongshu

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "  cd scripts"
echo "  python3 session_manager.py all           # 登录平台"
echo "  python3 crosscheck.py '深圳南山区' '粤菜'  # 开始使用"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
