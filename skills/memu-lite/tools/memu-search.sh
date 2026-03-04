#!/bin/bash
# memu-search.sh - 记忆搜索工具

WORKSPACE_DIR="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 检查参数
if [ $# -eq 0 ]; then
    echo -e "${BLUE}🔍 memU-lite - 记忆搜索${NC}"
    echo "========================"
    echo ""
    echo "用法:"
    echo "  ./memu-search.sh <关键词>"
    echo "  ./memu-search.sh -t <标签>     # 按标签搜索"
    echo "  ./memu-search.sh -i <ID>       # 按 ID 搜索"
    echo "  ./memu-search.sh -l             # 列出所有记忆"
    echo ""
    echo "示例:"
    echo "  ./memu-search.sh 偏好"
    echo "  ./memu-search.sh -t '#AI'"
    echo "  ./memu-search.sh -i P-20260302-001"
    exit 0
fi

# 检查记忆系统是否存在
if [ ! -d "$MEMORY_DIR" ]; then
    echo -e "${RED}❌ 错误：记忆系统未初始化${NC}"
    exit 1
fi

MODE="content"
QUERY="$1"

# 解析选项
while getopts "t:i:lh" opt; do
    case $opt in
        t) MODE="tag"; QUERY="$OPTARG" ;;
        i) MODE="id"; QUERY="$OPTARG" ;;
        l) MODE="list" ;;
        h)
            echo "用法: ./memu-search.sh [选项] <查询>"
            echo "  -t <标签>   按标签搜索"
            echo "  -i <ID>     按 ID 搜索"
            echo "  -l          列出所有记忆"
            echo "  -h          显示帮助"
            exit 0
            ;;
        *) exit 1 ;;
    esac
done

echo -e "${BLUE}🔍 搜索记忆...${NC}"
echo "=================="
echo ""

case $MODE in
    content)
        echo -e "关键词: ${CYAN}$QUERY${NC}"
        echo ""
        
        # 在 items 目录下搜索
        RESULTS=$(grep -rni "$QUERY" "$MEMORY_DIR/items/" --include="*.md" 2>/dev/null)
        
        if [ -z "$RESULTS" ]; then
            echo -e "${YELLOW}⚠️  未找到匹配的记忆${NC}"
            exit 0
        fi
        
        # 显示结果
        echo "$RESULTS" | while read -r line; do
            FILE=$(echo "$line" | cut -d: -f1)
            LINENO=$(echo "$line" | cut -d: -f2)
            CONTENT=$(echo "$line" | cut -d: -f3-)
            
            # 提取文件名和标题
            BASENAME=$(basename "$FILE")
            TITLE=$(grep "^## " "$FILE" 2>/dev/null | head -1 | sed 's/## //')
            
            echo -e "${GREEN}📄 $TITLE${NC}"
            echo -e "   ${CYAN}$CONTENT${NC}"
            echo -e "   ${YELLOW}行 $LINENO: $FILE${NC}"
            echo ""
        done
        
        COUNT=$(echo "$RESULTS" | wc -l)
        echo -e "${GREEN}✅ 找到 $COUNT 条匹配结果${NC}"
        ;;
    
    tag)
        echo -e "标签: ${CYAN}$QUERY${NC}"
        echo ""
        
        # 搜索包含该标签的文件
        RESULTS=$(grep -rl "\*\*标签\*\*:.*$QUERY" "$MEMORY_DIR/items/" --include="*.md" 2>/dev/null)
        
        if [ -z "$RESULTS" ]; then
            echo -e "${YELLOW}⚠️  未找到带有标签 $QUERY 的记忆${NC}"
            exit 0
        fi
        
        # 显示结果
        echo "$RESULTS" | while read -r file; do
            TITLE=$(grep "^## " "$file" 2>/dev/null | head -1 | sed 's/## //')
            TYPE=$(grep "^\- \*\*类型\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
            DATE=$(grep "^\- \*\*日期\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
            TAGS=$(grep "^\- \*\*标签\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
            
            echo -e "${GREEN}📄 $TITLE${NC}"
            echo -e "   类型: $TYPE | 日期: $DATE"
            echo -e "   标签: ${CYAN}$TAGS${NC}"
            echo ""
        done
        
        COUNT=$(echo "$RESULTS" | wc -l)
        echo -e "${GREEN}✅ 找到 $COUNT 条记忆${NC}"
        ;;
    
    id)
        echo -e "ID: ${CYAN}$QUERY${NC}"
        echo ""
        
        # 查找文件
        FILE=$(find "$MEMORY_DIR/items/" -name "*$QUERY*" -type f 2>/dev/null | head -1)
        
        if [ -z "$FILE" ]; then
            echo -e "${YELLOW}⚠️  未找到 ID 为 $QUERY 的记忆${NC}"
            exit 0
        fi
        
        # 显示完整内容
        echo -e "${GREEN}📄 完整记忆内容:${NC}"
        echo ""
        cat "$FILE"
        echo ""
        echo -e "${YELLOW}文件: $FILE${NC}"
        ;;
    
    list)
        echo "所有记忆列表:"
        echo ""
        
        # 遍历所有类型
        for type_dir in "$MEMORY_DIR/items/"*/; do
            if [ -d "$type_dir" ]; then
                TYPE=$(basename "$type_dir")
                COUNT=$(ls -1 "$type_dir"/*.md 2>/dev/null | wc -l)
                
                if [ $COUNT -gt 0 ]; then
                    echo -e "${CYAN}[$TYPE]${NC} ($COUNT 条)"
                    
                    for file in "$type_dir"/*.md; do
                        if [ -f "$file" ]; then
                            TITLE=$(grep "^## " "$file" 2>/dev/null | head -1 | sed 's/## //')
                            echo "  • $TITLE"
                        fi
                    done
                    echo ""
                fi
            fi
        done
        
        TOTAL=$(find "$MEMORY_DIR/items/" -name "*.md" 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ 总计: $TOTAL 条记忆${NC}"
        ;;
esac
