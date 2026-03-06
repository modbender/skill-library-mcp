#!/bin/bash
# Advanced skill discovery across multiple sources

QUERY="$1"
LIMIT="${2:-10}"

echo "🔍 Searching for skills: $QUERY"
echo ""

# Search ClawHub
echo "=== ClawHub ==="
clawhub search "$QUERY" --limit "$LIMIT" 2>/dev/null || echo "ClawHub search failed"

echo ""

# Search GitHub for OpenClaw skills
echo "=== GitHub (OpenClaw Skills) ==="
gh search repos --language=markdown -q ".skill OR SKILL.md" "openclaw $QUERY" --limit "$LIMIT" 2>/dev/null || echo "GitHub search unavailable"

echo ""

# Search GitHub for generic agent skills
echo "=== GitHub (Agent Skills) ==="
gh search code --language=markdown "SKILL.md" "$QUERY" --limit "$LIMIT" 2>/dev/null || echo "GitHub code search unavailable"

echo ""
echo "✅ Search complete!"
