#!/bin/bash
# memu-backup.sh - 记忆备份工具

WORKSPACE_DIR="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"
BACKUP_DIR="$WORKSPACE_DIR/backups/memory"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查记忆系统是否存在
if [ ! -d "$MEMORY_DIR" ]; then
    echo -e "${RED}❌ 错误：记忆系统未初始化${NC}"
    exit 1
fi

# 显示帮助
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo -e "${BLUE}💾 memU-lite - 备份工具${NC}"
    echo "======================="
    echo ""
    echo "用法:"
    echo "  ./memu-backup.sh           # 创建备份"
    echo "  ./memu-backup.sh -l        # 列出所有备份"
    echo "  ./memu-backup.sh -r <备份文件>  # 恢复备份"
    echo "  ./memu-backup.sh -c <天数>    # 清理旧备份"
    echo ""
    echo "示例:"
    echo "  ./memu-backup.sh                    # 立即备份"
    echo "  ./memu-backup.sh -l                 # 查看备份列表"
    echo "  ./memu-backup.sh -r memory-20260302-143022.tar.gz  # 恢复"
    echo "  ./memu-backup.sh -c 7               # 清理 7 天前的备份"
    exit 0
fi

# 创建备份
if [ $# -eq 0 ] || [ "$1" = "-b" ]; then
    echo -e "${BLUE}💾 创建记忆备份...${NC}"
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    # 生成备份文件名
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BACKUP_FILE="memory-$TIMESTAMP.tar.gz"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"
    
    # 创建备份
    cd "$WORKSPACE_DIR"
    tar -czf "$BACKUP_PATH" -C "$WORKSPACE_DIR" memory/
    
    if [ $? -eq 0 ]; then
        SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
        echo -e "${GREEN}✅ 备份成功!${NC}"
        echo "文件: $BACKUP_PATH"
        echo "大小: $SIZE"
        echo "时间: $(date)"
    else
        echo -e "${RED}❌ 备份失败${NC}"
        exit 1
    fi
    
    # 显示备份统计
    TOTAL=$(ls -1 "$BACKUP_DIR"/memory-*.tar.gz 2>/dev/null | wc -l)
    echo ""
    echo -e "${BLUE}📊 备份统计: 共 $TOTAL 个备份${NC}"
    
    # 显示最近5个备份
    if [ $TOTAL -gt 0 ]; then
        echo ""
        echo "最近 5 个备份:"
        ls -1t "$BACKUP_DIR"/memory-*.tar.gz 2>/dev/null | head -5 | while read -r f; do
            SIZE=$(du -h "$f" | cut -f1)
            DATE=$(stat -c %y "$f" 2>/dev/null | cut -d' ' -f1)
            echo "  • $(basename "$f") ($SIZE) - $DATE"
        done
    fi
fi

# 列出备份
if [ "$1" = "-l" ]; then
    echo -e "${BLUE}📋 备份列表${NC}"
    echo "==========="
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠️  暂无备份${NC}"
        exit 0
    fi
    
    echo "备份文件                          大小      日期"
    echo "--------------------------------  --------  ----------"
    
    ls -1t "$BACKUP_DIR"/memory-*.tar.gz 2>/dev/null | while read -r f; do
        SIZE=$(du -h "$f" | cut -f1)
        DATE=$(stat -c %y "$f" 2>/dev/null | cut -d' ' -f1)
        printf "%-32s  %-8s  %s\n" "$(basename "$f")" "$SIZE" "$DATE"
    done
    
    TOTAL=$(ls -1 "$BACKUP_DIR"/memory-*.tar.gz 2>/dev/null | wc -l)
    echo ""
    echo -e "${GREEN}总计: $TOTAL 个备份${NC}"
    
    # 计算总大小
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    echo "占用空间: $TOTAL_SIZE"
fi

# 恢复备份
if [ "$1" = "-r" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}❌ 错误：请指定备份文件${NC}"
        echo "用法: ./memu-backup.sh -r <备份文件>"
        exit 1
    fi
    
    BACKUP_FILE="$2"
    
    # 如果提供的是文件名，补全路径
    if [ ! -f "$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$2"
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}❌ 错误：备份文件不存在${NC}"
        echo "文件: $BACKUP_FILE"
        exit 1
    fi
    
    echo -e "${YELLOW}⚠️  警告：恢复备份将覆盖当前记忆系统${NC}"
    echo "备份文件: $BACKUP_FILE"
    echo ""
    read -p "是否继续? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}已取消${NC}"
        exit 0
    fi
    
    # 先创建当前状态的备份
    echo ""
    echo -e "${BLUE}💾 正在备份当前状态...${NC}"
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    AUTO_BACKUP="memory-auto-before-restore-$TIMESTAMP.tar.gz"
    cd "$WORKSPACE_DIR"
    tar -czf "$BACKUP_DIR/$AUTO_BACKUP" -C "$WORKSPACE_DIR" memory/
    echo -e "${GREEN}✅ 当前状态已备份: $AUTO_BACKUP${NC}"
    
    # 恢复备份
    echo ""
    echo -e "${BLUE}🔄 正在恢复备份...${NC}"
    cd "$WORKSPACE_DIR"
    rm -rf memory/
    tar -xzf "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 恢复成功!${NC}"
    else
        echo -e "${RED}❌ 恢复失败${NC}"
        exit 1
    fi
fi

# 清理旧备份
if [ "$1" = "-c" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}❌ 错误：请指定天数${NC}"
        echo "用法: ./memu-backup.sh -c <天数>"
        echo "示例: ./memu-backup.sh -c 7  # 清理 7 天前的备份"
        exit 1
    fi
    
    DAYS=$2
    echo -e "${BLUE}🧹 清理 ${DAYS} 天前的备份...${NC}"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}⚠️  备份目录不存在${NC}"
        exit 0
    fi
    
    # 查找并删除旧备份
    DELETED=0
    find "$BACKUP_DIR" -name "memory-*.tar.gz" -type f -mtime +$DAYS | while read -r f; do
        echo "删除: $(basename "$f")"
        rm "$f"
        DELETED=$((DELETED + 1))
    done
    
    echo ""
    echo -e "${GREEN}✅ 清理完成${NC}"
    
    # 显示剩余备份
    REMAINING=$(ls -1 "$BACKUP_DIR"/memory-*.tar.gz 2>/dev/null | wc -l)
    echo "剩余备份: $REMAINING 个"
fi
