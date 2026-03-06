#!/bin/bash
# Memory Maintenance Skill - Status Check

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/agents/memory"

echo "🧹 Memory Maintenance Status"
echo "============================="
echo ""

# Count files
echo "📊 Current State:"
echo "  Memory dir files:      $(find "$WORKSPACE/memory" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "  Archive files:         $(find "$WORKSPACE/memory/archive" -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "  Review files:          $(find "$MEMORY_DIR" -maxdepth 1 -name 'review-v2-*.json' 2>/dev/null | wc -l | tr -d ' ')"
echo "  Archived reviews:      $(find "$MEMORY_DIR/archive" -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "  Trash:                 $(find "$MEMORY_DIR/.trash" -type f 2>/dev/null | wc -l | tr -d ' ')"
echo ""

# Last review
LATEST_REVIEW=$(ls -1 "$MEMORY_DIR"/review-v2-*.json 2>/dev/null | tail -1)
if [ -n "$LATEST_REVIEW" ]; then
    REVIEW_DATE=$(basename "$LATEST_REVIEW" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
    echo "📅 Last Review: $REVIEW_DATE"
    
    if [ -f "$LATEST_REVIEW" ]; then
        CONTENT=$(jq '.content_suggestions | length' "$LATEST_REVIEW" 2>/dev/null || echo "0")
        MAINT=$(jq '.maintenance_suggestions | length' "$LATEST_REVIEW" 2>/dev/null || echo "0")
        SAFE=$(jq '[.maintenance_suggestions[] | select(.safe_to_auto == true)] | length' "$LATEST_REVIEW" 2>/dev/null || echo "0")
        
        echo "  Content suggestions:   $CONTENT"
        echo "  Maintenance tasks:     $MAINT"
        echo "  Safe to auto-apply:    $SAFE"
    fi
else
    echo "📅 Last Review: Never"
fi
echo ""

# Stats
if [ -f "$MEMORY_DIR/stats.json" ]; then
    echo "📈 Lifetime Stats:"
    jq -r '. | "  Total archived: \(.totalArchived // 0)\n  Total deleted: \(.totalDeleted // 0)"' "$MEMORY_DIR/stats.json" 2>/dev/null || echo "  (no stats yet)"
    echo ""
fi

# Cron status
echo "⏰ Schedule:"
if openclaw cron list 2>/dev/null | grep -q "memory-maintenance"; then
    echo "  ✅ Cron job active (runs daily at 23:00)"
else
    echo "  ⚠️  Cron job not found"
    echo "     Run: openclaw skill memory-maintenance install"
fi
echo ""

# Next actions
LATEST_REVIEW=$(ls -1 "$MEMORY_DIR"/review-v2-*.md 2>/dev/null | tail -1)
if [ -n "$LATEST_REVIEW" ]; then
    REVIEW_DATE=$(basename "$LATEST_REVIEW" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
    echo "🎯 Next Actions:"
    echo "  1. Review: $LATEST_REVIEW"
    echo "  2. Apply:  openclaw skill memory-maintenance apply --safe $REVIEW_DATE"
    echo "  3. Or:     Tell me 'Apply memory suggestions from $REVIEW_DATE'"
fi
