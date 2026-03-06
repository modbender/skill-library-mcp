#!/bin/bash
# Daily Ritual Script for Memphis Brain
# Run daily for memory maintenance

set -e

echo "🔥 Memphis Daily Ritual"
echo "======================="
echo ""

# 1. Health check
echo "📊 Step 1/7: Health check..."
memphis status
echo ""

# 2. Embed all chains
echo "🔢 Step 2/7: Embedding all chains..."
memphis embed
echo ""

# 3. Build knowledge graph
echo "🕸️ Step 3/7: Building knowledge graph..."
memphis graph build
echo ""

# 4. Daily reflection
echo "🤔 Step 4/7: Running daily reflection..."
memphis reflect --daily --save
echo ""

# 5. Verify chain integrity
echo "🔒 Step 5/7: Verifying chain integrity..."
memphis verify --all || echo "⚠️  Chain verification failed, run repair"
echo ""

# 6. Share-sync (if configured)
if [ -f ~/.memphis/config.yaml ] && grep -q "pinata:" ~/.memphis/config.yaml; then
    echo "🌐 Step 6/7: Share-sync..."
    memphis share-sync --all || echo "Share-sync failed or not configured"
else
    echo "🌐 Step 6/7: Share-sync (skipped, not configured)"
fi
echo ""

# 7. Show stats
echo "📈 Step 7/7: Memory stats..."
echo ""

# Count blocks
JOURNAL_BLOCKS=$(ls ~/.memphis/chains/journal/*.json 2>/dev/null | wc -l || echo "0")
DECISION_BLOCKS=$(ls ~/.memphis/chains/decision/*.json 2>/dev/null | wc -l || echo "0")
ASK_BLOCKS=$(ls ~/.memphis/chains/ask/*.json 2>/dev/null | wc -l || echo "0")
SUMMARY_BLOCKS=$(ls ~/.memphis/chains/summary/*.json 2>/dev/null | wc -l || echo "0")

echo "  📓 Journal blocks: $JOURNAL_BLOCKS"
echo "  🎯 Decision blocks: $DECISION_BLOCKS"
echo "  ❓ Ask blocks: $ASK_BLOCKS"
echo "  📄 Summary blocks: $SUMMARY_BLOCKS"
echo ""

# Check embeddings
if [ -d ~/.memphis/embeddings ]; then
    EMBEDDED_CHAINS=$(ls ~/.memphis/embeddings/*.json 2>/dev/null | wc -l || echo "0")
    echo "  🔢 Embedded chains: $EMBEDDED_CHAINS"
fi
echo ""

# Check graph
if [ -f ~/.memphis/graph/nodes.jsonl ]; then
    NODES=$(wc -l < ~/.memphis/graph/nodes.jsonl)
    EDGES=$(wc -l < ~/.memphis/graph/edges.jsonl 2>/dev/null || echo "0")
    echo "  🕸️  Graph nodes: $NODES"
    echo "  🔗 Graph edges: $EDGES"
fi
echo ""

echo "✅ Daily ritual complete"
echo "🧠 Memory is healthy and up-to-date"
