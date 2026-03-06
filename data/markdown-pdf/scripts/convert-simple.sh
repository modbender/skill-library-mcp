#!/bin/bash

# 简单的 Markdown 转 PDF 脚本
# 使用 wkhtmltopdf 或浏览器工具

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 检查参数
if [[ $# -lt 1 ]]; then
  echo "用法: $0 <input.md> [output.pdf]"
  exit 1
fi

INPUT="$1"
OUTPUT="${2:-${1%.md}.pdf}"

# 技能目录
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 检查输入文件
if [[ ! -f "$INPUT" ]]; then
  echo -e "${RED}错误: 文件不存在: $INPUT${NC}"
  exit 1
fi

# 转换为绝对路径
INPUT="$(realpath "$INPUT")"
OUTPUT="$(realpath "$(dirname "$OUTPUT")")/$(basename "$OUTPUT")"

echo -e "${GREEN}开始转换...${NC}"
echo "输入: $INPUT"
echo "输出: $OUTPUT"

# 创建临时 HTML 文件
TEMP_HTML=$(mktemp --suffix=.html)

# 读取 Markdown 内容
MD_CONTENT=$(cat "$INPUT")

# 创建简单的 HTML
cat > "$TEMP_HTML" << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans CJK SC", "Helvetica Neue", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 40px auto;
      padding: 0 20px;
    }
    h1, h2, h3, h4, h5, h6 {
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
    }
    h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    h3 { font-size: 1.25em; }
    h4 { font-size: 1em; }
    p { margin-bottom: 16px; }
    ul, ol { padding-left: 2em; margin-bottom: 16px; }
    pre {
      background: #f6f8fa;
      border-radius: 6px;
      padding: 16px;
      overflow: auto;
      margin-bottom: 16px;
    }
    code {
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 0.9em;
      background: rgba(175, 184, 193, 0.2);
      padding: 0.2em 0.4em;
      border-radius: 3px;
    }
    pre code { background: transparent; padding: 0; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
    table th, table td { border: 1px solid #d0d7de; padding: 6px 13px; }
    table th { background: #f6f8fa; font-weight: 600; }
    table tr:nth-child(2n) { background: #f6f8fa; }
    blockquote { padding: 0 1em; color: #656d76; border-left: 0.25em solid #d0d7de; margin-bottom: 16px; }
    a { color: #0969da; text-decoration: none; }
    a:hover { text-decoration: underline; }
    hr { height: 0.25em; padding: 0; margin: 24px 0; background: #d0d7de; border: 0; }
    img { max-width: 100%; height: auto; display: block; margin: 16px 0; }
  </style>
</head>
<body>
  <div class="content">
EOF

# 使用 pandoc 将 Markdown 转换为 HTML 并追加到文件
if command -v pandoc &> /dev/null; then
  pandoc "$INPUT" -t html -o /tmp/md_temp.html 2>/dev/null || {
    # 如果 pandoc 失败，使用简单替换
    sed 's/^#\(#\+\) /\1\1 /' "$INPUT" | sed 's/^###/##/' | sed 's/^##/#/' >> "$TEMP_HTML"
  }
  cat /tmp/md_temp.html >> "$TEMP_HTML" 2>/dev/null || echo "<pre>$MD_CONTENT</pre>" >> "$TEMP_HTML"
else
  echo "<pre>$MD_CONTENT</pre>" >> "$TEMP_HTML"
fi

cat >> "$TEMP_HTML" << EOF
  </div>
</body>
</html>
EOF

# 尝试使用可用的工具转换为 PDF
if command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
  CHROME=$(command -v chromium-browser || command -v chromium)
  echo "使用 Chromium 转换..."
  "$CHROME" --headless --disable-gpu --print-to-pdf="$OUTPUT" "$TEMP_HTML" 2>/dev/null
elif command -v wkhtmltopdf &> /dev/null; then
  echo "使用 wkhtmltopdf 转换..."
  wkhtmltopdf "$TEMP_HTML" "$OUTPUT" 2>/dev/null
else
  # 保存 HTML 文件供用户手动转换
  echo -e "${RED}未找到 PDF 转换工具${NC}"
  echo "HTML 文件已保存到: $TEMP_HTML"
  echo "请使用以下方法之一转换为 PDF:"
  echo "1. 在浏览器中打开 HTML 文件，然后打印为 PDF"
  echo "2. 安装 wkhtmltopdf: yum install -y wkhtmltopdf"
  echo "3. 安装 Chromium: yum install -y chromium"
  exit 1
fi

# 清理临时文件
rm -f "$TEMP_HTML" /tmp/md_temp.html

if [[ -f "$OUTPUT" ]]; then
  echo -e "${GREEN}✓ 转换成功！${NC}"
  echo "PDF 文件: $OUTPUT"
  ls -lh "$OUTPUT"
else
  echo -e "${RED}✗ 转换失败${NC}"
  exit 1
fi
