#!/bin/bash
# 最小化发布脚本 - 只发布必要文件到ClawHub

set -e

echo "=========================================="
echo "📦 AIOps Agent 最小化发布"
echo "=========================================="
echo ""

# 临时目录
TEMP_DIR="/tmp/aiops-agent-publish"
VERSION="1.0.1"

# 清理旧的临时目录
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "1️⃣ 复制必要文件..."

# 核心文件
cp SKILL.md "$TEMP_DIR/"
cp README.md "$TEMP_DIR/"
cp CHANGELOG.md "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp LICENSE "$TEMP_DIR/" 2>/dev/null || true

# 源代码
if [ -d "src" ]; then
    echo "   - 复制 src/ 目录"
    cp -r src "$TEMP_DIR/"
fi

# 配置示例
if [ -f ".env.example" ]; then
    cp .env.example "$TEMP_DIR/"
fi

# Makefile
if [ -f "Makefile" ]; then
    cp Makefile "$TEMP_DIR/"
fi

echo ""
echo "2️⃣ 统计文件数量..."
FILE_COUNT=$(find "$TEMP_DIR" -type f | wc -l | tr -d ' ')
echo "   总文件数: $FILE_COUNT"

if [ "$FILE_COUNT" -gt 100 ]; then
    echo "   ⚠️  警告: 文件数量较多（$FILE_COUNT），可能触发速率限制"
else
    echo "   ✅ 文件数量适中（$FILE_COUNT），速率限制风险低"
fi

echo ""
echo "3️⃣ 准备发布..."
cd "$TEMP_DIR"

# 显示文件列表
echo ""
echo "📋 将要发布的文件:"
find . -type f | sort

echo ""
echo "=========================================="
echo "🚀 开始发布到ClawHub"
echo "=========================================="
echo ""

# 发布
clawhub publish . \
    --slug aiops-agent \
    --name "AIOps Agent" \
    --version "$VERSION" \
    --tags "aiops,devops,sre,automation" \
    --changelog "修复语法错误，18/18测试通过，补充依赖说明"

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo "=========================================="
    echo "✅ 发布成功！"
    echo "=========================================="
    echo ""
    echo "验证:"
    clawhub search aiops
    echo ""
    echo "URL: https://clawhub.ai/jame-mei-ltp/aiops-agent"
    
    # 清理临时目录
    cd -
    rm -rf "$TEMP_DIR"
    echo "🧹 已清理临时文件"
else
    echo "=========================================="
    echo "❌ 发布失败"
    echo "=========================================="
    echo ""
    echo "临时文件保留在: $TEMP_DIR"
    echo "可以检查内容后手动重试"
    exit 1
fi
