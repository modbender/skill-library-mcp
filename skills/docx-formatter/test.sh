#!/bin/bash
# 测试脚本

cd "$(dirname "$0")/.."

echo "测试公文格式生成器..."

python3 docx-formatter.py \
  --title "测试文档标题" \
  --author "测试作者\n（2026年2月1日）" \
  --content examples/content.json \
  --output examples/test-output.docx

echo "完成！请检查 examples/test-output.docx"
