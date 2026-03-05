#!/bin/bash

# 清理过期记忆

MEMORY_DIR="${HOME}/memory/daily/hotspots"

echo "=== 记忆清理 $(date) ==="

# 清理评论历史（保留30天）
echo "清理评论历史..."
find "${MEMORY_DIR}/history/comments" -mtime +30 -type f -delete 2>/dev/null
echo "✓ 评论历史清理完成"

# 清理每日日志（保留30天）
echo "清理每日日志..."
find "${MEMORY_DIR}/history/daily" -mtime +30 -type f -delete 2>/dev/null
echo "✓ 每日日志清理完成"

# 清理热点表格（保留7天）
echo "清理热点表格..."
find "${MEMORY_DIR}/tables" -mtime +7 -type f -delete 2>/dev/null
echo "✓ 热点表格清理完成"

echo ""
echo "✓ 记忆清理完成: $(date)"
