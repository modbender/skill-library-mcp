#!/bin/bash
# One-click setup script for restaurant review cross-check skill

set -e

echo "================================================"
echo "🚀 餐厅推荐交叉验证 - 自动化安装脚本"
echo "================================================"
echo ""

# Check Python version
echo "1️⃣ 检查 Python 环境..."
python3 --version || {
    echo "❌ 未找到 Python 3，请先安装 Python 3.8+"
    exit 1
}

# Install Python dependencies
echo ""
echo "2️⃣ 安装 Python 依赖包..."
echo "   - playwright (浏览器自动化)"
echo "   - beautifulsoup4 (HTML 解析)"
echo "   - requests (HTTP 请求)"
echo "   - pandas, numpy (数据处理)"
echo "   - thefuzz (模糊匹配)"
echo ""

python3 -m pip install --upgrade pip -q --break-system-packages
python3 -m pip install playwright beautifulsoup4 requests pandas numpy thefuzz -q --break-system-packages

echo "✅ Python 依赖安装完成"

# Install Playwright browsers
echo ""
echo "3️⃣ 安装 Playwright 浏览器..."
echo "   这将下载 Chromium 浏览器（约 170MB）"
echo ""

python3 -m playwright install chromium --with-deps 2>/dev/null || python3 -m playwright install chromium

echo "✅ 浏览器安装完成"

# Setup sessions
echo ""
echo "4️⃣ 配置浏览器会话..."
echo ""
echo "================================================"
echo "📝 接下来需要配置登录会话"
echo "================================================"
echo ""
echo "为了让脚本自动登录大众点评和小红书，您需要："
echo ""
echo "1. 脚本会自动打开浏览器"
echo "2. 您在浏览器中手动登录账号"
echo "3. 登录后关闭浏览器"
echo "4. 脚本会自动保存登录状态"
echo ""
echo "💡 登录状态会保存 1-2 周，过期后重新登录即可"
echo ""

read -p "现在配置登录会话吗？(y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$(dirname "$0")"

    echo ""
    echo "🔐 配置大众点评..."
    python3 scripts/session_manager.py --dianping || {
        echo "⚠️ 大众点评配置失败，可以稍后手动配置"
    }

    echo ""
    echo "🔐 配置小红书..."
    python3 scripts/session_manager.py --xiaohongshu || {
        echo "⚠️ 小红书配置失败，可以稍后手动配置"
    }

    echo ""
    echo "✅ 配置完成！"
else
    echo ""
    echo "⏭️ 跳过登录配置"
    echo "💡 稍后可以运行: python3 scripts/session_manager.py"
fi

# Create symlink for easy access
echo ""
echo "5️⃣ 创建快捷命令..."
cd "$(dirname "$0")"
chmod +x scripts/crosscheck_real.py
ln -sf scripts/crosscheck_real.py crosscheck-auto
echo "✅ 快捷命令创建完成: ./crosscheck-auto"

# Done
echo ""
echo "================================================"
echo "✅ 安装完成！"
echo "================================================"
echo ""
echo "📖 使用方法："
echo ""
echo "  # 查询餐厅推荐"
echo "  ./crosscheck-auto '深圳市南山区' '美食'"
echo ""
echo "  # 或使用完整路径"
echo "  python3 scripts/crosscheck_real.py '深圳市南山区' '美食'"
echo ""
echo "  # 管理登录会话"
echo "  python3 scripts/session_manager.py"
echo ""
echo "  # 重置登录状态"
echo "  python3 scripts/session_manager.py --reset"
echo ""
echo "📚 文档："
echo "  - 使用说明: README.md"
echo "  - 数据结构: references/data_schema.md"
echo "  - API 限制: references/api_limitations.md"
echo ""
echo "⚠️ 注意事项："
echo "  - 仅供个人研究使用"
echo "  - 遵守平台服务条款"
echo "  - 不要频繁请求"
echo ""
