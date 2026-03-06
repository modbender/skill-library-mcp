#!/bin/bash
# memu-add.sh - 交互式创建记忆

WORKSPACE_DIR="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查记忆系统是否存在
if [ ! -d "$MEMORY_DIR" ]; then
    echo -e "${RED}❌ 错误：记忆系统未初始化${NC}"
    echo "请先运行安装脚本："
    echo "  cd ~/.openclaw/workspace/skills-pub/memu-lite"
    echo "  ./install.sh"
    exit 1
fi

# 显示菜单
echo -e "${BLUE}🧠 memU-lite - 添加新记忆${NC}"
echo "=========================="
echo ""

# 选择记忆类型
echo "选择记忆类型:"
echo "  1) preference  - 用户偏好、习惯"
echo "  2) knowledge   - 领域知识、事实"
echo "  3) relationship- 人际关系、上下文"
echo "  4) task        - 待办事项、项目"
echo "  5) skill       - 技能、方法、流程"
echo ""
read -p "请输入类型编号 (1-5): " type_num

case $type_num in
    1) TYPE="preference"; TYPE_PREFIX="P" ;;
    2) TYPE="knowledge"; TYPE_PREFIX="K" ;;
    3) TYPE="relationship"; TYPE_PREFIX="R" ;;
    4) TYPE="task"; TYPE_PREFIX="T" ;;
    5) TYPE="skill"; TYPE_PREFIX="S" ;;
    *) echo -e "${RED}❌ 无效选择${NC}"; exit 1 ;;
esac

echo ""
echo -e "已选择: ${GREEN}$TYPE${NC}"
echo ""

# 输入记忆标题
read -p "记忆标题: " TITLE
if [ -z "$TITLE" ]; then
    echo -e "${RED}❌ 标题不能为空${NC}"
    exit 1
fi

# 输入内容
read -p "内容摘要 (直接回车进入详细编辑): " CONTENT_SUMMARY

echo ""
echo "详细内容 (输入空行结束):"
echo "------------------------"
CONTENT=""
while IFS= read -r line; do
    [ -z "$line" ] && break
    CONTENT="$CONTENT$line\n"
done

# 输入来源
read -p "来源 (如: 对话/文档/链接): " SOURCE
SOURCE=${SOURCE:-"对话"}

# 输入标签
read -p "标签 (用空格分隔，如: #偏好 #AI): " TAGS

# 输入关联
read -p "关联记忆 ID (可选，如: K-20260302-001): " RELATIONS

# 如果是 task，询问过期日期
EXPIRY=""
if [ "$TYPE" = "task" ]; then
    echo ""
    read -p "过期日期 (YYYY-MM-DD，可选): " EXPIRY
fi

# 生成 ID
DATE=$(date +%Y%m%d)
COUNT=$(ls "$MEMORY_DIR/items/$TYPE"/ 2>/dev/null | grep "^$TYPE_PREFIX-$DATE" | wc -l)
COUNT=$((COUNT + 1))
ID="${TYPE_PREFIX}-${DATE}-$(printf "%03d" $COUNT)"

# 生成文件名
SLUG=$(echo "$TITLE" | tr ' ' '-' | tr -cd '[:alnum:]-' | tr '[:upper:]' '[:lower:]')
FILENAME="$MEMORY_DIR/items/$TYPE/${ID}-${SLUG}.md"

# 创建记忆文件
echo -e "\n${BLUE}📝 创建记忆文件...${NC}"

cat > "$FILENAME" << EOF
## $ID $TITLE

- **类型**: $TYPE
- **来源**: $SOURCE
- **日期**: $(date +%Y-%m-%d)
- **置信度**: high
- **标签**: $TAGS
EOF

if [ -n "$EXPIRY" ]; then
    echo "- **过期日期**: $EXPIRY" >> "$FILENAME"
fi

cat >> "$FILENAME" << EOF

- **内容**: 
  ${CONTENT_SUMMARY:-$CONTENT}

EOF

if [ -n "$RELATIONS" ]; then
    echo "- **关联**: [[$RELATIONS]]" >> "$FILENAME"
fi

echo "" >> "$FILENAME"

# 更新 MEMORY.md 索引
echo -e "${BLUE}🔄 更新 MEMORY.md 索引...${NC}"

# 在索引表格中添加新行
# 找到表格的最后一行，在后面添加
TABLE_LINE="| $ID | $TYPE | $TITLE | $(date +%Y-%m-%d) | $TAGS |"

# 使用 sed 在表格最后添加一行（在 "| - | - | - | - | - |" 之后）
sed -i "/^| - | - | - | - | - |$/a\\$TABLE_LINE" "$MEMORY_DIR/MEMORY.md"

# 更新时间线
MONTH=$(date +%Y-%m)
if grep -q "^### $MONTH" "$MEMORY_DIR/MEMORY.md"; then
    # 在现有月份下添加
    sed -i "/^### $MONTH/a\\- **$(date +%m-%d)**: 添加 $TYPE - $TITLE" "$MEMORY_DIR/MEMORY.md"
else
    # 创建新的月份
    sed -i "/^### 2026-03$/a\\
### $MONTH
_本月暂无重要记忆_" "$MEMORY_DIR/MEMORY.md"
fi

echo -e "${GREEN}✅ 记忆创建成功!${NC}"
echo ""
echo "文件: $FILENAME"
echo "ID: $ID"
echo ""
echo "提示:"
echo "  - 编辑文件: $FILENAME"
echo "  - 查看索引: $MEMORY_DIR/MEMORY.md"
echo "  - 搜索记忆: ./memu-search.sh $TAGS"
