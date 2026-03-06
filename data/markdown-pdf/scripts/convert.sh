#!/bin/bash

# Markdown 转 PDF 转换脚本（使用 pandoc）
# 用法: ./convert.sh <输入.md> [输出.pdf]

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [[ $# -lt 1 ]]; then
  echo -e "${RED}错误: 缺少输入文件${NC}"
  echo "用法: $0 <输入.md> [输出.pdf]"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${1%.md}.pdf}"

# 检查输入文件
if [[ ! -f "$INPUT_FILE" ]]; then
  echo -e "${RED}错误: 文件不存在: $INPUT_FILE${NC}"
  exit 1
fi

# 检查 pandoc
if ! command -v pandoc &> /dev/null; then
  echo -e "${YELLOW}pandoc 未安装，正在安装...${NC}"
  yum install -y pandoc
fi

# 检查中文字体
if ! fc-list | grep -q "Noto Sans CJK SC"; then
  echo -e "${YELLOW}正在安装中文字体...${NC}"
  yum install -y google-noto-sans-cjk-sc-fonts
fi

# 转换为绝对路径
INPUT_FILE="$(realpath "$INPUT_FILE")"
OUTPUT_FILE="$(realpath "$(dirname "$OUTPUT_FILE")")/$(basename "$OUTPUT_FILE")"

echo -e "${GREEN}开始转换...${NC}"
echo "输入: $INPUT_FILE"
echo "输出: $OUTPUT_FILE"

# 使用 pandoc 转换
pandoc "$INPUT_FILE" -o "$OUTPUT_FILE" \
  --pdf-engine=xelatex \
  -V CJKmainfont="Noto Sans CJK SC" \
  -V geometry:margin=2cm \
  -V fontsize=12pt \
  2>&1

if [[ $? -eq 0 && -f "$OUTPUT_FILE" ]]; then
  echo -e "${GREEN}✓ 转换成功！${NC}"
  echo "PDF 文件: $OUTPUT_FILE"
  ls -lh "$OUTPUT_FILE"
else
  echo -e "${RED}✗ 转换失败${NC}"
  echo "提示: 确保 xelatex 已安装（yum install -y texlive-xetex）"
  echo "或者使用简化版: bash scripts/convert-simple.sh input.md"
  exit 1
fi
