#!/bin/bash
# memu-tags.sh - 标签索引生成工具

WORKSPACE_DIR="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"
INDEXES_DIR="$MEMORY_DIR/indexes"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 检查记忆系统是否存在
if [ ! -d "$MEMORY_DIR" ]; then
    echo -e "${RED}❌ 错误：记忆系统未初始化${NC}"
    exit 1
fi

echo -e "${BLUE}🏷️  memU-lite - 标签索引生成${NC}"
echo "=========================="
echo ""

# 创建索引目录
mkdir -p "$INDEXES_DIR"

# 生成标签统计
echo -e "${BLUE}📊 扫描记忆文件...${NC}"

# 临时文件
TEMP_TAGS=$(mktemp)

# 提取所有标签
find "$MEMORY_DIR/items/" -name "*.md" -type f | while read -r file; do
    TAGS=$(grep "^\- \*\*标签\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
    if [ -n "$TAGS" ]; then
        # 将标签拆分为行
        for tag in $TAGS; do
            echo "$tag" >> "$TEMP_TAGS"
        done
    fi
done

# 统计标签频率
echo -e "${BLUE}📈 生成标签统计...${NC}"
echo ""

if [ ! -s "$TEMP_TAGS" ]; then
    echo -e "${YELLOW}⚠️  暂无标签数据${NC}"
    rm "$TEMP_TAGS"
    exit 0
fi

# 排序并统计
echo "标签统计:"
echo "---------"
sort "$TEMP_TAGS" | uniq -c | sort -rn | while read -r count tag; do
    printf "  ${CYAN}%-20s${NC} %4s 次\n" "$tag" "$count"
done

echo ""

# 生成索引文件
echo -e "${BLUE}📝 生成标签索引...${NC}"

INDEX_FILE="$INDEXES_DIR/tags.md"

cat > "$INDEX_FILE" << EOF
# 标签索引

> 自动生成于 $(date "+%Y-%m-%d %H:%M:%S")

## 标签统计

| 标签 | 数量 | 相关记忆 |
|------|------|----------|
EOF

# 生成表格内容
sort "$TEMP_TAGS" | uniq -c | sort -rn | while read -r count tag; do
    # 查找包含该标签的记忆
    MEMORIES=$(grep -rl "\*\*标签\*\*:.*$tag" "$MEMORY_DIR/items/" --include="*.md" 2>/dev/null | head -5)
    
    MEM_LIST=""
    for mem in $MEMORIES; do
        TITLE=$(grep "^## " "$mem" 2>/dev/null | head -1 | sed 's/## //')
        MEM_LIST="$MEM_LIST$TITLE; "
    done
    
    # 截断太长的列表
    if [ ${#MEM_LIST} -gt 50 ]; then
        MEM_LIST="${MEM_LIST:0:47}..."
    fi
    
    echo "| $tag | $count | $MEM_LIST |" >> "$INDEX_FILE"
done

cat >> "$INDEX_FILE" << EOF

## 快速检索

使用搜索工具按标签查找:
\`\`\`bash
./tools/memu-search.sh -t "#标签名"
\`\`\`

## 标签云

EOF

# 生成标签云（按频率排序）
echo "" >> "$INDEX_FILE"
sort "$TEMP_TAGS" | uniq -c | sort -rn | head -20 | while read -r count tag; do
    # 根据频率决定显示大小
    if [ $count -ge 10 ]; then
        echo -n "**$tag** " >> "$INDEX_FILE"
    elif [ $count -ge 5 ]; then
        echo -n "*$tag* " >> "$INDEX_FILE"
    else
        echo -n "$tag " >> "$INDEX_FILE"
    fi
done
echo "" >> "$INDEX_FILE"

# 清理临时文件
rm "$TEMP_TAGS"

echo -e "${GREEN}✅ 标签索引已更新!${NC}"
echo "文件: $INDEX_FILE"
echo ""

# 显示统计
TOTAL_TAGS=$(grep "^| #" "$INDEX_FILE" 2>/dev/null | wc -l)
echo "统计:"
echo "  标签总数: $TOTAL_TAGS"
echo "  索引文件: $INDEX_FILE"
