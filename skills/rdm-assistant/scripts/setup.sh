#!/bin/bash
# 研发经理助手 - 初始化脚本
# 用途: 设置技能的初始配置和权限

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 研发经理助手 - 初始化"
echo ""

# 设置脚本执行权限
echo "📝 设置工具脚本执行权限..."
chmod +x "$PROJECT_ROOT/tools/git-stats.sh"
chmod +x "$PROJECT_ROOT/tools/review-checklist.sh"
chmod +x "$PROJECT_ROOT/tools/report-generator.py"
echo "✅ 完成"

# 检查必要的依赖
echo ""
echo "🔍 检查依赖..."

# 检查 Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version | cut -d' ' -f3)"
else
    echo "⚠️  警告: Git 未安装"
fi

# 检查 Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version | cut -d' ' -f2)"
else
    echo "⚠️  警告: Python3 未安装"
fi

# 检查 YAMLint（可选）
if command -v yamllint &> /dev/null; then
    echo "✅ yamllint: 已安装"
else
    echo "ℹ️  提示: yamllint 未安装（可选，用于 YAML 格式检查）"
fi

# 创建必要的目录
echo ""
echo "📁 创建目录结构..."
mkdir -p "$PROJECT_ROOT/reports"
mkdir -p "$PROJECT_ROOT/config"
echo "✅ 完成"

# 复制配置文件（如果不存在）
CONFIG_FILE="$PROJECT_ROOT/config/skill-config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo ""
    echo "📋 配置文件已准备: $CONFIG_FILE"
    echo "📝 请根据实际情况修改配置文件"
else
    echo ""
    echo "ℹ️  配置文件已存在: $CONFIG_FILE"
fi

# 显示下一步指引
echo ""
echo "=========================================="
echo "✅ 初始化完成！"
echo "=========================================="
echo ""
echo "📚 下一步操作："
echo ""
echo "1. 配置技能"
echo "   编辑: $CONFIG_FILE"
echo ""
echo "2. 生成晨会报告"
echo "   cd \"$PROJECT_ROOT\""
echo "   ./tools/git-stats.sh /path/to/your/repo 7"
echo ""
echo "3. 使用报告生成器"
echo "   python3 tools/report-generator.py \\"
echo "     --template templates/晨会报告模板.md \\"
echo "     --config config/skill-config.yaml \\"
echo "     --output reports/晨会报告-$(date +%Y%m%d).md"
echo ""
echo "4. 代码审查"
echo "   ./tools/review-checklist.sh docs/代码审查检查清单.md"
echo ""
echo "=========================================="
