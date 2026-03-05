#!/bin/bash

# Word Reader 技能安装脚本
# 此脚本会自动安装依赖并设置技能

set -e

echo "=== Word Reader 技能安装 ==="
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
python_version=$(python3 --version 2>&1)
echo "   Python 版本: $python_version"

if ! python3 -c "import sys; assert sys.version_info >= (3, 6)"; then
    echo "❌ 错误：需要 Python 3.6 或更高版本"
    exit 1
fi

echo "✅ Python 版本检查通过"
echo ""

# 检查并安装依赖
echo "📦 检查依赖..."

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "   🔧 安装 pip..."
    python3 -m ensurepip --upgrade 2>/dev/null || {
        echo "   ❌ 无法安装 pip，尝试使用系统包管理器"
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v brew &> /dev/null; then
            brew install python3
        else
            echo "   ❌ 无法自动安装 pip，请手动安装"
            exit 1
        fi
    }
fi

# 检查 python-docx
if ! python3 -c "import docx" 2>/dev/null; then
    echo "   🔧 安装 python-docx..."
    if python3 -m pip install python-docx --break-system-packages 2>/dev/null; then
        echo "   ✅ python-docx 安装完成"
    elif python3 -m pip install python-docx 2>/dev/null; then
        echo "   ✅ python-docx 安装完成"
    else
        echo "❌ 无法安装 python-docx"
        exit 1
    fi
else
    echo "   ✅ python-docx 已安装"
fi

# 检查 antiword（可选）
if command -v antiword >/dev/null 2>&1; then
    echo "   ✅ antiword 已安装"
else
    echo "   ⚠️  antiword 未安装（可选，用于 .doc 格式支持）"
    echo "   推荐安装命令："
    echo "     Ubuntu/Debian: sudo apt-get install antiword"
    echo "     macOS: brew install antiword"
fi

echo ""

# 设置执行权限
echo "🔐 设置执行权限..."
chmod +x scripts/read_word.py
echo "✅ 执行权限已设置"
echo ""

# 验证安装
echo "🧪 验证安装..."
python3 scripts/read_word.py --help >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 安装验证成功"
else
    echo "❌ 安装验证失败"
    exit 1
fi

echo ""
echo "🎉 Word Reader 技能安装完成！"
echo ""
echo "📖 使用方法："
echo "   python3 scripts/read_word.py 文档.docx"
echo "   python3 scripts/read_word.py 文档.docx --format json"
echo "   python3 scripts/read_word.py 文档.docx --format markdown"
echo ""
echo "📖 更多帮助："
echo "   python3 scripts/read_word.py --help"
echo ""
echo "📖 运行演示："
echo "   ./demo.sh"