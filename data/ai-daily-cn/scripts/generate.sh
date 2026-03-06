#!/bin/bash
# AI Daily - 生成日报
# Usage: ./generate.sh [--date YYYY-MM-DD] [--output-dir PATH] [--debug]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# 检查 Python 版本
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    echo "Error: python3 not found"
    exit 1
fi

# 检查配置文件
if [ ! -f "$BASE_DIR/config/sources.json" ]; then
    echo "Error: config/sources.json not found"
    exit 1
fi

# 创建输出目录
mkdir -p "$BASE_DIR/output"

# 运行主脚本
echo "🚀 AI Daily - 开始生成日报..."
echo ""

$PYTHON "$SCRIPT_DIR/ai_daily.py" "$@"

echo ""
echo "✅ 生成完成！"
echo "📁 输出目录：$BASE_DIR/output"
