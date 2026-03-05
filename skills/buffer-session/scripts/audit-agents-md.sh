#!/bin/bash
# Audit AGENTS.md structure and instruction quality
set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
AGENTS="$WORKSPACE/AGENTS.md"

if [ ! -f "$AGENTS" ]; then
  echo "ERROR: AGENTS.md not found at $AGENTS"
  exit 1
fi

echo "=== AGENTS.MD STRUCTURE AUDIT ==="
echo ""

# Check if skill triggers are first section
first_h2=$(grep -n "^## " "$AGENTS" | head -1)
echo "First section: $first_h2"
if echo "$first_h2" | grep -qi "skill\|trigger"; then
  echo "  ✅ Skill triggers are the first section"
else
  echo "  🔴 Skill triggers are NOT first. Move them to position 1."
fi

echo ""

# Check for pre-response checkpoint
if grep -qi "before every response\|before responding\|pre-response\|checkpoint" "$AGENTS"; then
  echo "  ✅ Pre-response checkpoint found"
else
  echo "  🔴 No pre-response checkpoint. Add: 'Before Every Response: 1. Match skill triggers. 2. Check if a skill handles this.'"
fi

# Check for negative triggers
if grep -qi "don't reinvent\|don't bypass\|never manually\|use .* instead\|don't do.*manually" "$AGENTS"; then
  echo "  ✅ Negative triggers found"
else
  echo "  🔴 No negative triggers. Add a 'Don't Reinvent Skills' section."
fi

echo ""
echo "=== INSTRUCTION QUALITY ==="

# Flag weak patterns
echo "Scanning for weak instruction patterns..."
weak=0
while IFS= read -r line; do
  # Skip empty lines, headers, comments
  [[ -z "$line" || "$line" =~ ^#  || "$line" =~ ^\<!-- ]] && continue

  for pattern in "You have access" "you might want" "consider " "try to " "if appropriate" "you could" "you may want" "feel free" "it.s recommended" "you should consider"; do
    if echo "$line" | grep -qi "$pattern"; then
      echo "  ⚠️  Weak: \"$(echo "$line" | head -c 100)\""
      echo "     Pattern: '$pattern' → Rewrite as imperative directive"
      weak=$((weak + 1))
    fi
  done
done < "$AGENTS"

if [ "$weak" -eq 0 ]; then
  echo "  ✅ No weak instruction patterns found"
else
  echo ""
  echo "  Found $weak weak patterns. Rewrite each as: 'Do X when Y' or 'Never do X'"
fi

echo ""
echo "=== SECTION ORGANIZATION ==="
echo "Sections found:"
grep "^## " "$AGENTS" | while read -r line; do
  echo "  $line"
done

echo ""
echo "Check: Are sections organized by TRIGGER (when they fire) or by TOPIC (what they're about)?"
echo "  Trigger-based: 'During conversation', 'Before building', 'At wrap'"
echo "  Topic-based: 'Memory', 'Tools', 'Safety', 'Context'"
