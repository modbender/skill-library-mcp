#!/bin/bash
# Memory Maintenance Agent v2 - Apply Script
# Applies suggestions from memory-maintenance-v2.sh review
# Usage: memory-maintenance-apply.sh [--dry-run|--safe|--all] YYYY-MM-DD

set -e

WORKSPACE="/Users/maxhutchinson/.openclaw/workspace"
OUTPUT_DIR="$WORKSPACE/agents/memory"

# Parse arguments
MODE="dry-run"  # default
DATE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            MODE="dry-run"
            shift
            ;;
        --safe)
            MODE="safe"
            shift
            ;;
            MODE="all"
            shift
            ;;
        -*|--*)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run|--safe|--all] YYYY-MM-DD"
            exit 1
            ;;
        *)
            DATE="$1"
            shift
            ;;
    esac
done

if [ -z "$DATE" ]; then
    echo "Error: Date required (YYYY-MM-DD format)"
    echo "Usage: $0 [--dry-run|--safe|--all] YYYY-MM-DD"
    exit 1
fi

REVIEW_FILE="$OUTPUT_DIR/review-v2-${DATE}.json"

if [ ! -f "$REVIEW_FILE" ]; then
    echo "Error: Review file not found: $REVIEW_FILE"
    echo "Run memory-maintenance-v2.sh first to generate review."
    exit 1
fi

echo "=========================================="
echo "Memory Maintenance Apply: ${DATE}"
echo "Mode: ${MODE}"
echo "=========================================="
echo ""

# Stats
CONTENT_COUNT=$(jq '.content_suggestions | length' "$REVIEW_FILE")
MAINT_COUNT=$(jq '.maintenance_suggestions | length' "$REVIEW_FILE")
SAFE_COUNT=$(jq '[.maintenance_suggestions[] | select(.safe_to_auto == true)] | length' "$REVIEW_FILE")

echo "Review contains:"
echo "  - Content suggestions: $CONTENT_COUNT"
echo "  - Maintenance tasks: $MAINT_COUNT"
echo "  - Safe to auto-apply: $SAFE_COUNT"
echo ""

# ============================================
# DRY RUN MODE
# ============================================

if [ "$MODE" = "dry-run" ]; then
    echo "=== DRY RUN - No changes will be made ==="
    echo ""
    
    echo "Content suggestions that would be applied:"
    jq -r '.content_suggestions[] | "  [\(.priority)] \(.type) to \(.section): \(.proposed_text | .[0:60])..."' "$REVIEW_FILE" 2>/dev/null || echo "  (none)"
    echo ""
    
    echo "Maintenance tasks that would be applied:"
    if [ "$MODE" = "safe" ]; then
        jq -r '.maintenance_suggestions[] | select(.safe_to_auto == true) | "  [\(.type)] \(.target) -> \(.action)"' "$REVIEW_FILE" 2>/dev/null || echo "  (none)"
    else
        jq -r '.maintenance_suggestions[] | "  [\(.type)] \(.target) -> \(.action) (safe: \(.safe_to_auto))"' "$REVIEW_FILE" 2>/dev/null || echo "  (none)"
    fi
    echo ""
    
    echo "To apply changes, run:"
    echo "  $0 --safe $DATE    # Apply only safe changes"
    echo "  $0 --all $DATE     # Apply all changes (requires confirmation)"
    exit 0
fi

# ============================================
# SAFE MODE - Apply only safe maintenance tasks
# ============================================

if [ "$MODE" = "safe" ]; then
    echo "=== SAFE MODE - Applying only safe-to-auto changes ==="
    echo ""
    
    # Content suggestions are NEVER auto-applied (always require human review)
    echo "Content suggestions ($CONTENT_COUNT): SKIPPED (requires manual review)"
    echo ""
    
    # Apply safe maintenance tasks
    echo "Applying safe maintenance tasks..."
    SAFE_TASKS=$(jq -c '.maintenance_suggestions[] | select(.safe_to_auto == true)' "$REVIEW_FILE" 2>/dev/null || echo "")
    
    if [ -z "$SAFE_TASKS" ]; then
        echo "  No safe tasks to apply."
    else
        echo "$SAFE_TASKS" | while IFS= read -r task; do
            TYPE=$(echo "$task" | jq -r '.type')
            TARGET=$(echo "$task" | jq -r '.target')
            ACTION=$(echo "$task" | jq -r '.action')
            
            echo "  Processing: $TYPE $TARGET"
            
            case "$TYPE" in
                archive)
                    # Move to archive directory
                    if [ -f "$WORKSPACE/$TARGET" ]; then
                        BASENAME=$(basename "$TARGET")
                        mkdir -p "$WORKSPACE/memory/archive"
                        mv "$WORKSPACE/$TARGET" "$WORKSPACE/memory/archive/$BASENAME"
                        echo "    ✓ Archived to memory/archive/$BASENAME"
                    else
                        echo "    ✗ File not found: $TARGET"
                    fi
                    ;;
                *)
                    echo "    ⚠ Skipped (only 'archive' is auto-safe)"
                    ;;
            esac
        done
    fi
    
    echo ""
    echo "Safe mode complete."
    echo ""
    echo "Manual review still needed for:"
    echo "  - $CONTENT_COUNT content suggestions (update MEMORY.md)"
    UNSAFE_COUNT=$(jq '[.maintenance_suggestions[] | select(.safe_to_auto != true)] | length' "$REVIEW_FILE")
    echo "  - $UNSAFE_COUNT maintenance tasks (requires --all mode)"
    exit 0
fi

# ============================================
# ALL MODE - Apply everything (with confirmation)
# ============================================

if [ "$MODE" = "all" ]; then
    echo "=== ALL MODE - This will apply ALL suggestions ==="
    echo ""
    
    # Show what's about to happen
    echo "CONTENT SUGGESTIONS TO APPLY:"
    jq -r '.content_suggestions[] | "  [\(.priority)] \(.type) to \(.section)"' "$REVIEW_FILE" 2>/dev/null || echo "  (none)"
    echo ""
    
    echo "MAINTENANCE TASKS TO APPLY:"
    jq -r '.maintenance_suggestions[] | "  [\(.type)] \(.target) -> \(.action)"' "$REVIEW_FILE" 2>/dev/null || echo "  (none)"
    echo ""
    
    echo "⚠️  WARNING: This will modify MEMORY.md and move/delete files!"
    read -p "Type 'APPLY' to confirm: " CONFIRM
    
    if [ "$CONFIRM" != "APPLY" ]; then
        echo "Cancelled."
        exit 0
    fi
    
    echo ""
    echo "Applying all changes..."
    echo ""
    
    # Apply content suggestions to MEMORY.md
    if [ "$CONTENT_COUNT" -gt 0 ]; then
        echo "Applying content suggestions to MEMORY.md..."
        echo "  (This requires Gemini to generate the updated MEMORY.md)"
        echo "  Feature coming in v2.1 - for now, apply manually or tell me:"
        echo "  'Apply memory suggestions from $DATE'"
    fi
    
    # Apply all maintenance tasks
    if [ "$MAINT_COUNT" -gt 0 ]; then
        echo ""
        echo "Applying maintenance tasks..."
        
        jq -c '.maintenance_suggestions[]' "$REVIEW_FILE" | while IFS= read -r task; do
            TYPE=$(echo "$task" | jq -r '.type')
            TARGET=$(echo "$task" | jq -r '.target')
            ACTION=$(echo "$task" | jq -r '.action')
            
            echo "  Processing: $TYPE $TARGET"
            
            case "$TYPE" in
                archive)
                    if [ -f "$WORKSPACE/$TARGET" ]; then
                        BASENAME=$(basename "$TARGET")
                        mkdir -p "$WORKSPACE/memory/archive"
                        mv "$WORKSPACE/$TARGET" "$WORKSPACE/memory/archive/$BASENAME"
                        echo "    ✓ Archived"
                    else
                        echo "    ✗ Not found"
                    fi
                    ;;
                rename)
                    # Parse "old -> new" from action
                    OLD=$(echo "$ACTION" | sed 's/.*-> *//')
                    if [ -f "$WORKSPACE/$TARGET" ]; then
                        mv "$WORKSPACE/$TARGET" "$WORKSPACE/$OLD"
                        echo "    ✓ Renamed to $OLD"
                    fi
                    ;;
                delete)
                    if [ -f "$WORKSPACE/$TARGET" ]; then
                        # Move to trash instead of permanent delete
                        mkdir -p "$WORKSPACE/memory/.trash"
                        BASENAME=$(basename "$TARGET")
                        mv "$WORKSPACE/$TARGET" "$WORKSPACE/memory/.trash/${BASENAME}.$(date +%s)"
                        echo "    ✓ Moved to trash (recoverable)"
                    fi
                    ;;
                consolidate)
                    echo "    ⚠ Consolidation requires manual review"
                    ;;
                *)
                    echo "    ⚠ Unknown type: $TYPE"
                    ;;
            esac
        done
    fi
    
    echo ""
    echo "All mode complete."
    echo ""
    echo "Note: Content suggestions for MEMORY.md were not auto-applied."
    echo "Tell me: 'Apply memory suggestions from $DATE' to apply content updates."
    exit 0
fi
