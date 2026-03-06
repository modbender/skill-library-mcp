#!/bin/bash
# 狗蛋恢复脚本
# 支持从 OneDrive 或本地文件恢复

set -e

ONEDRIVE="OneDrive:/备份/OpenClaw"
BACKUP_DIR="/root/.openclaw/backup"
TEMP_DIR="/root/.openclaw/backup/restore-temp"
LOG_FILE="$BACKUP_DIR/restore.log"

log() {
    echo "[$(date)] $1" | tee -a $LOG_FILE
}

usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --source PATH    本地备份文件夹路径 (可选，不指定则从 OneDrive 恢复)"
    echo "  --core          只恢复核心层 (SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md)"
    echo "  --memory        只恢复记忆层 (memory/)"
    echo "  --all           恢复所有 (默认)"
    echo "  --date DATE     指定日期备份 (格式: YYYYMMDD, 默认最新)"
    echo "  --target DIR    恢复目标目录 (默认: /root/.openclaw/workspace)"
    echo "  --dry-run       测试模式，不实际恢复"
    echo ""
    echo "示例:"
    echo "  # 从 OneDrive 恢复 (默认)"
    echo "  $0 --all --dry-run"
    echo ""
    echo "  # 从本地文件恢复 (新机器无需 rclone)"
    echo "  $0 --source /path/to/backup/files --all"
    echo ""
    echo "  # 从本地文件恢复核心层"
    echo "  $0 --source ./backup-files --core --target /tmp/restore"
}

# 解析参数
MODE="all"
DATE=""
TARGET="/root/.openclaw/workspace"
DRY_RUN=false
SOURCE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE="$2"
            shift 2
            ;;
        --core)
            MODE="core"
            shift
            ;;
        --memory)
            MODE="memory"
            shift
            ;;
        --all)
            MODE="all"
            shift
            ;;
        --date)
            DATE="$2"
            shift 2
            ;;
        --target)
            TARGET="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            usage
            exit 1
            ;;
    esac
done

log "========== 开始恢复 =========="
log "模式: $MODE"
log "目标: $TARGET"
log "日期: ${DATE:-最新}"
log "来源: ${SOURCE:-OneDrive}"
log "测试模式: $DRY_RUN"

# 创建临时目录
mkdir -p $TEMP_DIR

# 从本地文件恢复
restore_from_local() {
    local file=$1
    local dest=$2
    
    if [ -f "$file" ]; then
        log "找到备份文件: $file"
        if [ "$DRY_RUN" = true ]; then
            log "[测试] 会解压到 $dest"
        else
            log "解压到临时目录..."
            tar -xzf "$file" -C $TEMP_DIR/
            log "复制到目标目录..."
            cp -n $TEMP_DIR/*/$dest $TARGET/ 2>/dev/null || true
        fi
    else
        log "文件不存在: $file"
    fi
}

# 从 OneDrive 恢复
restore_from_onedrive() {
    local pattern=$1
    local file
    
    if [ -n "$DATE" ]; then
        file="goudan-$pattern-$DATE.tar.gz"
    else
        file=$(rclone lsf $ONEDRIVE/ 2>/dev/null | grep "goudan-$pattern-" | sort | tail -1)
    fi
    
    if [ -n "$file" ]; then
        log "找到备份: $file"
        if [ "$DRY_RUN" = true ]; then
            log "[测试] 会恢复 $pattern 层"
        else
            log "下载备份..."
            rclone copy "$ONEDRIVE/$file" $TEMP_DIR/
            log "解压..."
            tar -xzf $TEMP_DIR/$file -C $TEMP_DIR/
            log "复制到目标目录..."
        fi
    else
        log "未找到 $pattern 备份"
        return 1
    fi
}

# 核心层恢复
if [ "$MODE" = "core" ] || [ "$MODE" = "all" ]; then
    if [ -n "$SOURCE" ]; then
        # 从本地恢复
        if [ -n "$DATE" ]; then
            restore_from_local "$SOURCE/goudan-core-$DATE.tar.gz" "SOUL.md"
            restore_from_local "$SOURCE/goudan-core-$DATE.tar.gz" "AGENTS.md"
            restore_from_local "$SOURCE/goudan-core-$DATE.tar.gz" "IDENTITY.md"
            restore_from_local "$SOURCE/goudan-core-$DATE.tar.gz" "USER.md"
            restore_from_local "$SOURCE/goudan-core-$DATE.tar.gz" "TOOLS.md"
        else
            CORE_FILE=$(ls -t $SOURCE/goudan-core-*.tar.gz 2>/dev/null | head -1)
            if [ -n "$CORE_FILE" ]; then
                restore_from_local "$CORE_FILE" "SOUL.md"
                restore_from_local "$CORE_FILE" "AGENTS.md"
                restore_from_local "$CORE_FILE" "IDENTITY.md"
                restore_from_local "$CORE_FILE" "USER.md"
                restore_from_local "$CORE_FILE" "TOOLS.md"
            fi
        fi
    else
        # 从 OneDrive 恢复
        restore_from_onedrive "core"
        if [ "$DRY_RUN" = false ]; then
            cp -n $TEMP_DIR/*/SOUL.md $TARGET/ 2>/dev/null || true
            cp -n $TEMP_DIR/*/AGENTS.md $TARGET/ 2>/dev/null || true
            cp -n $TEMP_DIR/*/IDENTITY.md $TARGET/ 2>/dev/null || true
            cp -n $TEMP_DIR/*/USER.md $TARGET/ 2>/dev/null || true
            cp -n $TEMP_DIR/*/TOOLS.md $TARGET/ 2>/dev/null || true
        fi
    fi
    log "✅ 核心层恢复完成"
fi

# 记忆层恢复
if [ "$MODE" = "memory" ] || [ "$MODE" = "all" ]; then
    if [ -n "$SOURCE" ]; then
        # 从本地恢复
        if [ -n "$DATE" ]; then
            restore_from_local "$SOURCE/goudan-memory-$DATE.tar.gz" "memory/"
        else
            MEMORY_FILE=$(ls -t $SOURCE/goudan-memory-*.tar.gz 2>/dev/null | head -1)
            if [ -n "$MEMORY_FILE" ]; then
                restore_from_local "$MEMORY_FILE" "memory/"
            fi
        fi
    else
        # 从 OneDrive 恢复
        restore_from_onedrive "memory"
        if [ "$DRY_RUN" = false ]; then
            cp -rn $TEMP_DIR/*/memory/ $TARGET/ 2>/dev/null || true
        fi
    fi
    log "✅ 记忆层恢复完成"
fi

# 清理
rm -rf $TEMP_DIR

log "========== 恢复完成 =========="
