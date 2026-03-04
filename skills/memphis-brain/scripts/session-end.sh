#!/bin/bash
# Session End Script for Memphis Brain
# Run at the end of each agent session

set -e

echo "🔥 Memphis Session End"
echo "======================"
echo ""

# 1. Prompt for summary
read -p "📝 Session summary (what did you accomplish?): " SUMMARY
if [ -z "$SUMMARY" ]; then
    SUMMARY="Session completed"
fi

# 2. Prompt for learnings
read -p "💡 What did you learn? (optional): " LEARNINGS

# 3. Journal session end
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo ""
echo "📝 Journaling session end..."
memphis journal "Session ended at $TIMESTAMP. Accomplished: $SUMMARY" --tags session,summary

if [ -n "$LEARNINGS" ]; then
    memphis journal "Learned: $LEARNINGS" --tags learning,session
fi
echo ""

# 4. Embed new context
echo "🔢 Embedding new context..."
memphis embed --chain journal
echo ""

# 5. Save reflection
echo "🤔 Saving daily reflection..."
memphis reflect --daily --save
echo ""

# 6. Share-sync (if configured)
if [ -f ~/.memphis/config.yaml ] && grep -q "pinata:" ~/.memphis/config.yaml; then
    echo "🌐 Syncing shared blocks..."
    read -p "Push to IPFS? (y/N): " PUSH
    if [ "$PUSH" = "y" ] || [ "$PUSH" = "Y" ]; then
        memphis share-sync --push || echo "Push failed"
    else
        memphis share-sync --pull || echo "Pull failed"
    fi
    echo ""
fi

# 7. Show stats
echo "📊 Session stats:"
BLOCKS=$(ls ~/.memphis/chains/journal/*.json 2>/dev/null | wc -l)
echo "  Journal blocks: $BLOCKS"
echo ""

echo "✅ Session closed"
echo "💾 Memory persisted"
