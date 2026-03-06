#!/bin/bash
# Memory Shrink Script
# 执行 context 存档操作

set -e

WORKSPACE="${1:-/root/.openclaw/workspace-code_analyst}"
MEMORY_DIR="$WORKSPACE/memory"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)

echo "=== Memory Shrink ==="
echo "Timestamp: $TIMESTAMP"
echo "Workspace: $WORKSPACE"

# 检查 memory 目录
if [ ! -d "$MEMORY_DIR" ]; then
    echo "No memory directory found, nothing to shrink."
    exit 0
fi

# 统计当前 memory 文件
FILE_COUNT=$(ls -1 "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
echo "Memory files: $FILE_COUNT"

# 创建存档
ARCHIVE_DIR="$MEMORY_DIR/archive"
mkdir -p "$ARCHIVE_DIR"

# 移动旧的 memory 文件到 archive
OLD_FILES=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -mtime +7 2>/dev/null)
if [ -n "$OLD_FILES" ]; then
    for file in $OLD_FILES; do
        basename=$(basename "$file")
        mv "$file" "$ARCHIVE_DIR/${TIMESTAMP}_${basename}"
        echo "Archived: $basename"
    done
    echo "Archive complete."
else
    echo "No files older than 7 days to archive."
fi

echo "=== Done ==="
