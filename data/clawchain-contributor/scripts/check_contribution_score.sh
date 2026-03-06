#!/bin/bash
# Check your ClawChain contribution score
# Usage: ./check_contribution_score.sh <github-username>

set -e

GITHUB_USER="${1:-$USER}"
REPO_URL="https://raw.githubusercontent.com/clawinfra/claw-chain/main/CONTRIBUTORS.md"

echo "🦞 Checking contribution score for: $GITHUB_USER"
echo ""

# Fetch CONTRIBUTORS.md
CONTRIBUTORS=$(curl -sL "$REPO_URL")

if echo "$CONTRIBUTORS" | grep -q "@$GITHUB_USER"; then
    echo "✅ You are a ClawChain contributor!"
    echo ""
    echo "Your entry:"
    echo "$CONTRIBUTORS" | grep -A 5 "@$GITHUB_USER" | head -6
    echo ""
    echo "📊 Full contributor list: https://github.com/clawinfra/claw-chain/blob/main/CONTRIBUTORS.md"
else
    echo "❌ Not found in CONTRIBUTORS.md"
    echo ""
    echo "To become a contributor:"
    echo "1. Open a PR: https://github.com/clawinfra/claw-chain"
    echo "2. Sign the CLA when prompted"
    echo "3. Get your PR merged"
    echo ""
    echo "First contribution earns 5,000+ points!"
fi
