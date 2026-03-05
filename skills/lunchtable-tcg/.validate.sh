#!/bin/bash
# Validation script for LunchTable-TCG OpenClaw Skill

echo "🎴 Validating LunchTable-TCG OpenClaw Skill Structure..."
echo ""

# Track validation status
ERRORS=0

# Check required files
echo "📋 Checking required files..."
REQUIRED_FILES=(
  "SKILL.md"
  ".clawhub.json"
  "package.json"
  "README.md"
  "INSTALLATION.md"
  "CHANGELOG.md"
  "SUBMISSION.md"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file exists"
  else
    echo "  ✗ $file is missing"
    ((ERRORS++))
  fi
done

# Check required directories
echo ""
echo "📁 Checking required directories..."
REQUIRED_DIRS=(
  "examples"
  "scenarios"
)

for dir in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "  ✓ $dir/ exists"
  else
    echo "  ✗ $dir/ is missing"
    ((ERRORS++))
  fi
done

# Check SKILL.md has YAML frontmatter
echo ""
echo "🔍 Checking SKILL.md YAML frontmatter..."
if head -1 SKILL.md | grep -q "^---$"; then
  echo "  ✓ SKILL.md has YAML frontmatter"
else
  echo "  ✗ SKILL.md missing YAML frontmatter"
  ((ERRORS++))
fi

# Check for required YAML fields
echo ""
echo "📝 Checking YAML frontmatter fields..."
YAML_FIELDS=("name:" "description:" "version:" "author:" "license:")
for field in "${YAML_FIELDS[@]}"; do
  if grep -q "$field" SKILL.md; then
    echo "  ✓ $field present"
  else
    echo "  ✗ $field missing"
    ((ERRORS++))
  fi
done

# Check .clawhub.json is valid JSON
echo ""
echo "🔧 Validating .clawhub.json..."
if command -v jq &> /dev/null; then
  if jq empty .clawhub.json 2>/dev/null; then
    echo "  ✓ .clawhub.json is valid JSON"
  else
    echo "  ✗ .clawhub.json has invalid JSON"
    ((ERRORS++))
  fi
else
  echo "  ⚠ jq not installed, skipping JSON validation"
fi

# Check package.json is valid JSON
echo ""
echo "📦 Validating package.json..."
if command -v jq &> /dev/null; then
  if jq empty package.json 2>/dev/null; then
    echo "  ✓ package.json is valid JSON"
  else
    echo "  ✗ package.json has invalid JSON"
    ((ERRORS++))
  fi
else
  echo "  ⚠ jq not installed, skipping JSON validation"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
  echo "✅ Validation passed! Skill is ready for ClawHub submission."
  echo ""
  echo "Next steps:"
  echo "  1. Test locally: openclaw skill add ."
  echo "  2. Commit to Git: git add . && git commit -m 'feat: add ClawHub skill'"
  echo "  3. Submit to ClawHub: clawhub submit ."
  exit 0
else
  echo "❌ Validation failed with $ERRORS error(s)."
  echo ""
  echo "Please fix the errors above before submitting to ClawHub."
  exit 1
fi
