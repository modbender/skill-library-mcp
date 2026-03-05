#!/bin/bash
# 一键安装依赖

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SKILL_DIR"

echo "🔧 正在安装 docx-formatter 依赖..."

# 检查是否已有虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境并安装依赖
echo "📥 安装 python-docx..."
source .venv/bin/activate
uv pip install python-docx

echo "✅ 依赖安装完成！"
echo ""
echo "使用方法："
echo "  docx-formatter input.md -o output.docx --author '单位名称'"
