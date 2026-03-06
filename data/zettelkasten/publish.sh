#!/bin/bash
echo "📦 Preparing to publish Zettelkasten to Clawhub..."
echo ""

# 检查文件
if [ ! -f "SKILL.md" ]; then
    echo "❌ SKILL.md not found"
    exit 1
fi

echo "✅ Required files found"
echo ""

# 尝试不同的发布方式
echo "🔧 Attempting method 1: Basic publish command..."
clawhub publish . --slug zettelkasten --name "Zettelkasten - 卡片盒笔记法" --version 1.0.0 --changelog "Initial release with AI insights"

if [ $? -ne 0 ]; then
    echo ""
    echo "🔧 Attempting method 2: Using tar.gz archive..."
    
    # 创建归档
    tar -czf zettelkasten-1.0.0.tar.gz .
    
    # 尝试用API发布
    echo "📤 Publishing via API..."
    curl -X POST "https://api.clawhub.com/v1/skills" \
      -H "Authorization: Bearer $(cat ~/.clawhub/credentials)" \
      -F "slug=zettelkasten" \
      -F "name=Zettelkasten - 卡片盒笔记法" \
      -F "version=1.0.0" \
      -F "archive=@zettelkasten-1.0.0.tar.gz"
fi

echo ""
echo "🎉 Publish attempt completed!"