#!/bin/bash
# k-deep-research skill validation
# Run this to verify skill structure integrity

SKILL_DIR="$(dirname "$0")/.."
ERRORS=0

echo "=== k-deep-research Skill Validation ==="
echo ""

# Check SKILL.md exists
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "✅ SKILL.md exists"
else
    echo "❌ SKILL.md MISSING"
    ERRORS=$((ERRORS + 1))
fi

# Check frontmatter
if head -1 "$SKILL_DIR/SKILL.md" | grep -q "^---"; then
    echo "✅ YAML frontmatter present"
else
    echo "❌ YAML frontmatter missing"
    ERRORS=$((ERRORS + 1))
fi

# Check name field
if grep -q "^name:" "$SKILL_DIR/SKILL.md"; then
    echo "✅ name field present"
else
    echo "❌ name field missing"
    ERRORS=$((ERRORS + 1))
fi

# Check description field
if grep -q "^description:" "$SKILL_DIR/SKILL.md"; then
    echo "✅ description field present"
else
    echo "❌ description field missing"
    ERRORS=$((ERRORS + 1))
fi

# Check SKILL.md line count (should be under 500)
LINES=$(wc -l < "$SKILL_DIR/SKILL.md")
if [ "$LINES" -lt 500 ]; then
    echo "✅ SKILL.md body: $LINES lines (under 500 limit)"
else
    echo "⚠️  SKILL.md body: $LINES lines (exceeds 500 recommended)"
fi

# Check reference files
REFS="sourcing-strategies.md research-frameworks.md output-templates.md openclaw-architecture.md openclaw-skill-authoring.md autonomy-patterns.md adversarial-analysis.md"

echo ""
echo "--- Reference Files ---"
for ref in $REFS; do
    if [ -f "$SKILL_DIR/references/$ref" ]; then
        REFLINES=$(wc -l < "$SKILL_DIR/references/$ref")
        echo "✅ references/$ref ($REFLINES lines)"
    else
        echo "❌ references/$ref MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for secrets (env vars, API keys)
echo ""
echo "--- Security Check ---"
if grep -rn "sk-\|api_key=\|password=\|secret=" "$SKILL_DIR/" --include="*.md" 2>/dev/null; then
    echo "⚠️  Possible secrets found in files"
else
    echo "✅ No secrets detected"
fi

# Summary
echo ""
echo "=== Validation Complete ==="
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ All checks passed"
else
    echo "❌ $ERRORS error(s) found"
fi

exit $ERRORS
