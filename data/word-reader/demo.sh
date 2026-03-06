#!/bin/bash

# Word Reader 技能演示脚本
# 此脚本展示如何使用 word-reader 技能

echo "=== Word Reader 技能演示 ==="
echo ""

# 检查脚本是否存在
SCRIPT_PATH="/root/.openclaw/workspace/skills/word-reader/scripts/read_word.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ 错误：脚本不存在"
    echo "请确保技能已正确安装"
    exit 1
fi

# 检查脚本是否有执行权限
if [ ! -x "$SCRIPT_PATH" ]; then
    echo "❌ 错误：脚本没有执行权限"
    echo "正在添加执行权限..."
    chmod +x "$SCRIPT_PATH"
fi

echo "✅ 脚本已就绪"
echo ""

# 显示技能信息
echo "📋 技能信息："
echo "   名称：word-reader"
echo "   功能：读取 Word 文档（.docx 和 .doc 格式）"
echo "   位置：$SCRIPT_PATH"
echo ""

# 显示使用示例
echo "📖 使用示例："
echo ""

echo "1. 显示帮助信息："
echo "   python3 $SCRIPT_PATH --help"
echo ""

echo "2. 读取文档（文本格式）："
echo "   python3 $SCRIPT_PATH 文档路径.docx"
echo ""

echo "3. 读取文档（JSON 格式）："
echo "   python3 $SCRIPT_PATH 文档路径.docx --format json"
echo ""

echo "4. 读取文档（Markdown 格式）："
echo "   python3 $SCRIPT_PATH 文档路径.docx --format markdown"
echo ""

echo "5. 只提取文本内容："
echo "   python3 $SCRIPT_PATH 文档路径.docx --extract text"
echo ""

echo "6. 批量处理目录："
echo "   python3 $SCRIPT_PATH ./文档目录 --batch"
echo ""

echo "7. 保存结果到文件："
echo "   python3 $SCRIPT_PATH 文档路径.docx --format markdown --output output.md"
echo ""

echo "🔧 安装依赖："
echo "   pip3 install python-docx"
echo "   # 对于 .doc 格式支持："
echo "   # Ubuntu: sudo apt-get install antiword"
echo "   # macOS: brew install antiword"
echo ""

echo "📊 支持的功能："
echo "   ✅ 文本提取"
echo "   ✅ 表格解析"
echo "   ✅ 元数据获取"
echo "   ✅ 图片信息"
echo "   ✅ 多格式支持"
echo "   ✅ 批量处理"
echo ""

echo "💡 提示："
echo "   - 支持 .docx 和 .doc 格式"
echo "   - 输出格式：JSON、Text、Markdown"
echo "   - 如遇错误，请检查依赖是否安装"
echo ""

echo "演示完成！"
echo "如需使用，请替换 '文档路径.docx' 为实际的文档路径"