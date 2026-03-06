#!/bin/bash
# promote-to-memory-md.sh - 将 CortexGraph 高分记忆导出到 MEMORY.md
# 用法: ./promote-to-memory-md.sh [--dry-run]

set -e

DRY_RUN="${1:-}"
MEMORY_FILE="$HOME/.openclaw/workspace/MEMORY.md"

echo "🧠 晋升高价值记忆 → MEMORY.md"

# 获取高分记忆（score > 1.5，用得多的）
echo "  📊 查询高分记忆..."

RESULT=$(mcporter call cortexgraph.search_memory \
    query="important preference decision strategy" \
    min_score=0.5 \
    top_k=20 \
    --json 2>/dev/null || echo '{"results":[]}')

# 解析结果
echo "$RESULT" | python3 -c "
import json
import sys

data = json.load(sys.stdin)
results = data.get('results', [])

for r in results:
    content = r.get('content', '')
    score = r.get('score', 0)
    tags = ', '.join(r.get('tags', []))
    use_count = r.get('use_count', 0)
    
    print(f'### 📍 Score: {score:.2f} | Uses: {use_count} | Tags: {tags}')
    print(f'{content}')
    print()
"

echo ""
echo "---"
echo "💡 以上是高价值记忆候选"
echo ""
echo "手动操作："
echo "1. 检查内容是否值得加入 MEMORY.md"
echo "2. 编辑 MEMORY.md 添加相关内容"
echo "3. 运行: mcporter call cortexgraph.promote_memory memory_id=UUID"
echo ""
echo "自动晋升（谨慎）："
if [[ "$DRY_RUN" != "--dry-run" ]]; then
    read -p "是否自动晋升高分记忆? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mcporter call cortexgraph.promote_memory auto_detect=true
    fi
else
    echo "  [DRY RUN] 跳过自动晋升"
fi
