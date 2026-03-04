#!/bin/bash
# Quick publish script for agent-guardrails

set -e

SKILL_DIR="/Users/openclaw/clawd/skills/agent-guardrails"

echo "📦 Publishing Agent Guardrails v1.1.0 to ClawdHub"
echo ""

# Check if logged in
echo "1. Checking ClawdHub authentication..."
if ! clawdhub whoami > /dev/null 2>&1; then
    echo "   ⚠️  Not logged in"
    echo "   Opening browser for login..."
    clawdhub login
else
    echo "   ✅ Already logged in"
fi

echo ""
echo "2. Publishing skill..."
cd "$SKILL_DIR"

clawdhub publish . \
  --slug agent-guardrails \
  --name "Agent Guardrails" \
  --version 1.1.0 \
  --changelog "Meta-enforcement system: Deployment verification + skill update feedback loop. Prevents 4 common agent failure modes through mechanical enforcement."

echo ""
echo "✅ Published to ClawdHub!"
echo ""
echo "View at: https://clawdhub.com/skills/agent-guardrails"
echo ""
echo "Next steps:"
echo "  1. Share on X/Twitter (see X_THREAD.md)"
echo "  2. Post on LinkedIn"
echo "  3. Share on Reddit"
