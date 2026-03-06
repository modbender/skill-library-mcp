#!/bin/bash
# Mermaid工作流技能快速开始脚本

echo "========================================"
echo "Mermaid工作流技能 - 快速开始"
echo "========================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

echo "✅ Python3已安装: $(python3 --version)"

# 检查mmdc
if ! command -v mmdc &> /dev/null; then
    echo "⚠️ Mermaid CLI (mmdc) 未安装"
    echo "请安装: npm install -g @mermaid-js/mermaid-cli"
    echo "或使用npx: npx @mermaid-js/mermaid-cli"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Mermaid CLI已安装: $(mmdc --version)"
fi

# 创建示例目录
EXAMPLE_DIR="quick_start_example"
mkdir -p "$EXAMPLE_DIR"
cd "$EXAMPLE_DIR"

echo ""
echo "1. 创建Mermaid图表定义文件..."
python3 ../scripts/create_mermaid.py \
  --type roadmap \
  --title "快速开始示例路线图" \
  --output example_roadmap.mmd

python3 ../scripts/create_mermaid.py \
  --type architecture \
  --title "示例系统架构" \
  --output example_architecture.mmd

echo "✅ 图表定义文件已创建"

echo ""
echo "2. 转换为PNG图片..."
# 创建Puppeteer配置文件
cat > puppeteer-config.json << EOF
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
EOF

python3 ../scripts/convert_mermaid.py \
  --input example_roadmap.mmd \
  --output example_roadmap.png \
  --puppeteer-config puppeteer-config.json

python3 ../scripts/convert_mermaid.py \
  --input example_architecture.mmd \
  --output example_architecture.png \
  --puppeteer-config puppeteer-config.json

echo "✅ PNG图片已生成"

echo ""
echo "3. 创建Markdown报告..."
cat > example_report.md << 'EOF'
# 示例报告

## 项目路线图
[ROADMAP_IMAGE]

## 系统架构
[ARCHITECTURE_IMAGE]

## 说明
这是一个使用Mermaid工作流技能生成的示例报告。
EOF

echo "✅ Markdown报告已创建"

echo ""
echo "4. 插入图片到报告..."
python3 ../scripts/insert_to_md.py \
  --md-file example_report.md \
  --image example_roadmap.png \
  --placeholder "[ROADMAP_IMAGE]" \
  --caption "项目开发路线图"

python3 ../scripts/insert_to_md.py \
  --md-file example_report.md \
  --image example_architecture.png \
  --placeholder "[ARCHITECTURE_IMAGE]" \
  --caption "系统架构图"

echo "✅ 图片已插入到报告"

echo ""
echo "5. 查看生成的文件..."
echo "生成的文件:"
ls -la *.mmd *.png *.md

echo ""
echo "========================================"
echo "✅ 快速开始完成！"
echo "生成的文件在: $EXAMPLE_DIR/"
echo ""
echo "查看报告:"
echo "  cat $EXAMPLE_DIR/example_report.md"
echo ""
echo "清理示例:"
echo "  rm -rf $EXAMPLE_DIR"
echo "========================================"