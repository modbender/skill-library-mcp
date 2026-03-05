#!/bin/bash
# review-skill.sh — Full review pipeline: fetch → scan → isolated review
# Usage: bash review-skill.sh <author>/<skill-name>
# 
# This script orchestrates the 3-stage review:
#   Stage 1: Blocklist scan (automated)
#   Stage 2: Isolated agent review (spawned sub-agent, read-only)
#   Stage 3: Human approval (manual — creates draft in reviews/)

set -e

SKILL_PATH="${1:?Usage: review-skill.sh <author>/<skill-name>}"
SKILL=$(echo "$SKILL_PATH" | cut -d'/' -f2)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔍 SkillScout Review Pipeline"
echo "   Skill: $SKILL_PATH"
echo "   Date: $(date -u +%Y-%m-%d)"
echo ""

# Stage 1: Blocklist scan
echo "━━━ Stage 1: Blocklist Scan ━━━"
bash "$SCRIPT_DIR/scan-blocklists.sh" "$SKILL" || {
    echo "⛔ Review aborted: skill is blocklisted"
    exit 1
}
echo ""

# Stage 2: Fetch source (text only)
echo "━━━ Stage 2: Fetching Skill Source ━━━"
SKILL_SOURCE=$(bash "$SCRIPT_DIR/fetch-skill.sh" "$SKILL_PATH")
echo "   Fetched $(echo "$SKILL_SOURCE" | wc -l) lines of source"
echo ""

# Save source for review
REVIEW_DIR="$PROJECT_DIR/reviews"
mkdir -p "$REVIEW_DIR"

# Write the source + template to a review input file
cat > "/tmp/skillscout-review-input-$SKILL.md" << HEREDOC
# SkillScout Security & Quality Review

You are a security-focused code reviewer. Analyze the following OpenClaw skill source code and complete the review template below.

## CRITICAL CONSTRAINTS:
- You are READ-ONLY. You cannot and must not execute any code.
- Analyze the source text only. Look for security risks, quality issues, and verify claims.
- Be skeptical. Flag anything suspicious.
- Write for a non-technical audience where possible.

## SKILL SOURCE CODE:

$SKILL_SOURCE

## REVIEW TEMPLATE (complete this):

$(cat "$PROJECT_DIR/REVIEW_TEMPLATE.md")
HEREDOC

echo "━━━ Stage 2: Ready for Isolated Agent Review ━━━"
echo "   Review input saved to: /tmp/skillscout-review-input-$SKILL.md"
echo "   $(wc -c < "/tmp/skillscout-review-input-$SKILL.md") bytes"
echo ""
echo "━━━ Stage 3: Submit to isolated review agent ━━━"
echo "   Run from OpenClaw main session:"
echo "   sessions_spawn(task=<contents of /tmp/skillscout-review-input-$SKILL.md>, model='deepseek', label='review-$SKILL')"
echo ""
echo "   After review completes, save output to: $REVIEW_DIR/$SKILL.md"
echo "   Then: human approval required before publishing."
