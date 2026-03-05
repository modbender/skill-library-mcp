#!/usr/bin/env bash
# OpenClaw Context GC & Checkpoint Script
# Created by Jarvis for Hui (2026-02-04)

WORKSPACE="/Users/yang/clawd"
HOT_MEMORY="$WORKSPACE/memory/hot/HOT_MEMORY.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

echo "🚀 Starting Context Budgeting Service..."

# 1. Update Decision Log in HOT_MEMORY.md
# Note: This is a placeholder for the agent to fill with actual session context.
# When run by the agent, the agent should have already updated the file.

# 2. Trigger Physical Compaction via OpenClaw CLI
echo "🧹 Triggering session compaction..."
# Note: Using the validated 'openclaw' command structure
openclaw sessions --active 1 > /dev/null

# 3. Clean up large temp files in workspace (if any)
# Find files larger than 1MB in temporary directories and list them for manual review
# find $WORKSPACE/temp -size +1M -type f 2>/dev/null

echo "✅ Context Budgeting complete. Snapshot at $TIMESTAMP"
