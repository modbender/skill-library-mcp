#!/bin/bash
# memu-clean.sh - 过期记忆清理工具

WORKSPACE_DIR="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"
ARCHIVE_DIR="$MEMORY_DIR/archive"

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

# 显示帮助
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo -e "${BLUE}🧹 memU-lite - 过期清理工具${NC}"
    echo "=========================="
    echo ""
    echo "用法:"
    echo "  ./memu-clean.sh           # 扫描过期记忆"
    echo "  ./memu-clean.sh -a        # 自动归档过期记忆"
    echo "  ./memu-clean.sh -f        # 强制删除过期记忆（谨慎）"
    echo "  ./memu-clean.sh -l        # 查看已归档记忆"
    echo ""
    echo "说明:"
    echo "  清理工具会检查带有'过期日期'的记忆，"
    echo "  将已过期的记忆归档到 archive/ 目录"
    exit 0
fi

MODE="scan"
if [ "$1" = "-a" ]; then
    MODE="archive"
elif [ "$1" = "-f" ]; then
    MODE="delete"
elif [ "$1" = "-l" ]; then
    MODE="list"
fi

TODAY=$(date +%Y-%m-%d)
EXPIRED_COUNT=0
EXPIRED_FILES=""

echo -e "${BLUE}🧹 扫描过期记忆...${NC}"
echo "=================="
echo ""
echo "今天: $TODAY"
echo ""

# 扫描所有记忆文件
find "$MEMORY_DIR/items/" -name "*.md" -type f | while read -r file; do
    # 检查是否有过期日期
    EXPIRY=$(grep "^\- \*\*过期日期\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
    
    if [ -n "$EXPIRY" ]; then
        # 比较日期
        if [[ "$TODAY" > "$EXPIRY" ]] || [ "$TODAY" = "$EXPIRY" ]; then
            TITLE=$(grep "^## " "$file" 2>/dev/null | head -1 | sed 's/## //')
            TYPE=$(grep "^\- \*\*类型\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
            
            echo -e "${YELLOW}⚠️  过期记忆:${NC}"
            echo "  标题: $TITLE"
            echo "  类型: $TYPE"
            echo "  过期: $EXPIRY"
            echo "  文件: $file"
            echo ""
            
            EXPIRED_COUNT=$((EXPIRED_COUNT + 1))
            EXPIRED_FILES="$EXPIRED_FILES\n$file"
        fi
    fi
done

# 处理扫描结果
if [ $EXPIRED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ 没有发现过期记忆${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}发现 $EXPIRED_COUNT 条过期记忆${NC}"
echo ""

case $MODE in
    scan)
        echo "扫描完成。如需归档，请运行:"
        echo "  ./memu-clean.sh -a"
        echo ""
        echo "如需强制删除，请运行:"
        echo "  ./memu-clean.sh -f"
        ;;
    
    archive)
        echo -e "${BLUE}📦 归档过期记忆...${NC}"
        echo ""
        
        # 创建归档目录
        mkdir -p "$ARCHIVE_DIR"
        
        # 归档文件
        echo -e "$EXPIRED_FILES" | while read -r file; do
            [ -z "$file" ] && continue
            
            BASENAME=$(basename "$file")
            TYPE=$(echo "$file" | grep -o "items/[^/]*" | cut -d/ -f2)
            
            # 创建类型子目录
            mkdir -p "$ARCHIVE_DIR/$TYPE"
            
            # 移动文件
            mv "$file" "$ARCHIVE_DIR/$TYPE/"
            
            echo -e "${GREEN}✓ 已归档:${NC} $BASENAME → archive/$TYPE/"
        done
        
        echo ""
        echo -e "${GREEN}✅ 归档完成${NC}"
        echo "归档目录: $ARCHIVE_DIR"
        ;;
    
    delete)
        echo -e "${RED}⚠️  警告：即将永久删除过期记忆${NC}"
        echo ""
        read -p "确认删除? (输入 'delete' 确认): " confirm
        
        if [ "$confirm" != "delete" ]; then
            echo -e "${YELLOW}已取消${NC}"
            exit 0
        fi
        
        echo ""
        echo -e "${RED}🗑️  删除过期记忆...${NC}"
        echo ""
        
        echo -e "$EXPIRED_FILES" | while read -r file; do
            [ -z "$file" ] && continue
            
            BASENAME=$(basename "$file")
            rm "$file"
            
            echo -e "${RED}✓ 已删除:${NC} $BASENAME"
        done
        
        echo ""
        echo -e "${GREEN}✅ 删除完成${NC}"
        ;;
    
    list)
        echo -e "${BLUE}📦 已归档记忆列表${NC}"
        echo ""
        
        if [ ! -d "$ARCHIVE_DIR" ] || [ -z "$(ls -A "$ARCHIVE_DIR" 2>/dev/null)" ]; then
            echo -e "${YELLOW}暂无归档记忆${NC}"
            exit 0
        fi
        
        # 遍历归档目录
        find "$ARCHIVE_DIR" -name "*.md" -type f | while read -r file; do
            TITLE=$(grep "^## " "$file" 2>/dev/null | head -1 | sed 's/## //')
            EXPIRY=$(grep "^\- \*\*过期日期\*\*:" "$file" 2>/dev/null | sed 's/.*: //')
            
            echo "• $TITLE"
            echo "  过期: $EXPIRY"
            echo "  位置: ${file#$MEMORY_DIR/}"
            echo ""
        done
        
        TOTAL=$(find "$ARCHIVE_DIR" -name "*.md" -type f | wc -l)
        echo -e "${GREEN}总计: $TOTAL 条归档记忆${NC}"
        ;;
esac
