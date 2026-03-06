#!/bin/bash
# Markdown 转 PDF (WeasyPrint 方案)
# 支持完美中文显示、代码高亮、表格样式

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/convert-weasyprint.py"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <输入.md> [输出.pdf]"
    echo ""
    echo "示例:"
    echo "  $0 document.md"
    echo "  $0 document.md output.pdf"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${INPUT_FILE%.md}.pdf}"

# 检查输入文件
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ 错误: 输入文件不存在: $INPUT_FILE"
    exit 1
fi

# 检查 Python 依赖
if ! python3 -c "import markdown, weasyprint" 2>/dev/null; then
    echo "⚠️  Python 依赖未安装，正在安装..."
    python3 -m pip install -q markdown weasyprint
fi

# 检查中文字体
if ! fc-list | grep -q "Noto Sans CJK"; then
    echo "⚠️  中文字体未安装，正在安装..."
    yum install -y -q google-noto-sans-cjk-fonts
fi

# 检查 emoji 字体
if ! fc-list | grep -q "Noto.*Emoji"; then
    echo "⚠️  Emoji 字体未安装，正在安装..."
    yum install -y -q google-noto-emoji-color-fonts google-noto-emoji-fonts
fi

# 执行转换
echo "📄 开始转换..."
echo "   输入: $INPUT_FILE"
echo "   输出: $OUTPUT_FILE"
echo ""

python3 "$PYTHON_SCRIPT" "$INPUT_FILE" "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 转换成功！"
    echo "📁 文件位置: $OUTPUT_FILE"
    echo "📊 文件大小: $(du -h "$OUTPUT_FILE" | cut -f1)"
else
    echo ""
    echo "❌ 转换失败"
    exit 1
fi
