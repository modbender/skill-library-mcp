#!/usr/bin/env bash
# Add new pre-flight check interactively

set -euo pipefail

WORKSPACE_DIR="${WORKSPACE_DIR:-$(pwd)}"
CHECKS_FILE="$WORKSPACE_DIR/PRE-FLIGHT-CHECKS.md"
ANSWERS_FILE="$WORKSPACE_DIR/PRE-FLIGHT-ANSWERS.md"

# Check files exist
if [ ! -f "$CHECKS_FILE" ]; then
    echo "❌ PRE-FLIGHT-CHECKS.md not found"
    echo "Run: ./skills/preflight-checks/scripts/init.sh first"
    exit 1
fi

if [ ! -f "$ANSWERS_FILE" ]; then
    echo "❌ PRE-FLIGHT-ANSWERS.md not found"
    echo "Run: ./skills/preflight-checks/scripts/init.sh first"
    exit 1
fi

echo "🔥 Add New Pre-Flight Check"
echo

# Get current check count
CURRENT_COUNT=$(grep -c "^\*\*CHECK-" "$CHECKS_FILE" || echo "0")
NEW_CHECK_NUM=$((CURRENT_COUNT + 1))

echo "Current checks: $CURRENT_COUNT"
echo "New check will be: CHECK-$NEW_CHECK_NUM"
echo

# Gather check details
echo "Category (e.g., Core Behavior, Communication, Anti-Patterns):"
read -r CATEGORY

echo
echo "Scenario (brief description, e.g., 'You solved a problem'):"
read -r SCENARIO

echo
echo "Question (what agent should answer):"
read -r QUESTION

echo
echo "Expected answer (correct behavior):"
read -r EXPECTED

echo
echo "Wrong answer #1 (common mistake):"
read -r WRONG1

echo
echo "Wrong answer #2 (optional, press Enter to skip):"
read -r WRONG2

echo
echo "Wrong answer #3 (optional, press Enter to skip):"
read -r WRONG3

# Build check entry
CHECK_ENTRY="
**CHECK-$NEW_CHECK_NUM: $SCENARIO**
$QUESTION
"

# Build answer entry
ANSWER_ENTRY="
**CHECK-$NEW_CHECK_NUM: $SCENARIO**

**Expected:**
$EXPECTED

**Wrong answers:**
- ❌ $WRONG1"

if [ -n "$WRONG2" ]; then
    ANSWER_ENTRY="$ANSWER_ENTRY
- ❌ $WRONG2"
fi

if [ -n "$WRONG3" ]; then
    ANSWER_ENTRY="$ANSWER_ENTRY
- ❌ $WRONG3"
fi

# Show preview
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PREVIEW - CHECKS file:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$CHECK_ENTRY"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PREVIEW - ANSWERS file:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$ANSWER_ENTRY"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Add this check? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# Add to CHECKS file (before Scoring section)
# Find line number of "## Scoring"
SCORING_LINE=$(grep -n "^## Scoring" "$CHECKS_FILE" | cut -d: -f1)

if [ -z "$SCORING_LINE" ]; then
    # If no Scoring section, append to end
    echo "$CHECK_ENTRY" >> "$CHECKS_FILE"
else
    # Insert before Scoring
    {
        head -n $((SCORING_LINE - 2)) "$CHECKS_FILE"
        echo "$CHECK_ENTRY"
        tail -n +$((SCORING_LINE - 1)) "$CHECKS_FILE"
    } > "$CHECKS_FILE.tmp"
    mv "$CHECKS_FILE.tmp" "$CHECKS_FILE"
fi

# Add to ANSWERS file (before Behavior Summary)
SUMMARY_LINE=$(grep -n "^## Behavior Summary" "$ANSWERS_FILE" | cut -d: -f1)

if [ -z "$SUMMARY_LINE" ]; then
    echo "$ANSWER_ENTRY" >> "$ANSWERS_FILE"
else
    {
        head -n $((SUMMARY_LINE - 2)) "$ANSWERS_FILE"
        echo "$ANSWER_ENTRY"
        tail -n +$((SUMMARY_LINE - 1)) "$ANSWERS_FILE"
    } > "$ANSWERS_FILE.tmp"
    mv "$ANSWERS_FILE.tmp" "$ANSWERS_FILE"
fi

# Update scoring
OLD_SCORE="$CURRENT_COUNT/$CURRENT_COUNT"
NEW_SCORE="$NEW_CHECK_NUM/$NEW_CHECK_NUM"

sed -i "s|$OLD_SCORE correct|$NEW_SCORE correct|g" "$CHECKS_FILE"
sed -i "s|Score: X/$CURRENT_COUNT|Score: X/$NEW_CHECK_NUM|g" "$CHECKS_FILE"

echo "✅ Check added!"
echo "✅ Scoring updated: $OLD_SCORE → $NEW_SCORE"
echo
echo "Files updated:"
echo "- $CHECKS_FILE"
echo "- $ANSWERS_FILE"
echo
echo "Next: Have agent run pre-flight checks to verify"
