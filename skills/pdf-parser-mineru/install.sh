#!/bin/bash
# MinerU 安装脚本

set -e  # 遇到错误立即退出

echo "========================================"
echo "  PDF Process Skill - MinerU 安装脚本"
echo "========================================"
echo ""

# 检查 Python 版本
echo "1. 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   检测到 Python 版本: $python_version"

# 检查 Python 版本是否在 3.10-3.13 范围内
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]); then
    echo "   ❌ 错误: Python 版本过低。需要 Python 3.10 或更高版本"
    echo "   当前版本: $python_version"
    exit 1
fi

if [ "$python_major" -gt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -gt 13 ]); then
    echo "   ⚠️  警告: Python 版本过高。推荐使用 Python 3.10-3.13"
fi

echo "   ✓ Python 版本符合要求"
echo ""

# 检查 pip
echo "2. 检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "   ❌ 错误: 未找到 pip3"
    exit 1
fi
echo "   ✓ pip3 已安装"
echo ""

# 更新 pip
echo "3. 更新 pip..."
python3 -m pip install --upgrade pip
echo "   ✓ pip 已更新"
echo ""

# 安装 uv
echo "4. 安装 uv (快速包管理器)..."
if ! command -v uv &> /dev/null; then
    pip3 install uv
    echo "   ✓ uv 安装成功"
else
    echo "   ✓ uv 已安装"
fi
echo ""

# 安装 MinerU
echo "5. 安装 MinerU (包含所有功能)..."
echo "   这可能需要几分钟时间，请耐心等待..."
uv pip install -U "mineru[all]"
echo "   ✓ MinerU 安装成功"
echo ""

# 验证安装
echo "6. 验证安装..."
if command -v mineru &> /dev/null; then
    mineru_version=$(mineru --version 2>&1)
    echo "   ✓ mineru 命令可用"
    echo "   版本: $mineru_version"
else
    echo "   ❌ 错误: mineru 命令不可用"
    echo "   请检查安装是否成功"
    exit 1
fi
echo ""

# 测试帮助命令
echo "7. 测试 mineru --help..."
mineru --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ mineru 命令运行正常"
else
    echo "   ❌ 警告: mineru 命令运行异常"
fi
echo ""

echo "========================================"
echo "  ✅ 安装完成！"
echo "========================================"
echo ""
echo "现在可以使用 PDF Process Skill 了！"
echo ""
echo "测试命令:"
echo "  python .claude/skills/pdf-process/script/pdf_parser.py \\"
echo '    \'{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/test.pdf", "output_dir": "/tmp/output"}}\''
echo ""
echo "更多信息请查看:"
echo "  .claude/skills/pdf-process/README.md"
echo ""
