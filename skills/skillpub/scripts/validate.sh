#!/usr/bin/env bash
set -euo pipefail

# validate.sh - Validate a skill before publishing
# Usage: validate.sh <skill-folder>

usage() {
  echo "Usage: $0 <skill-folder>"
  echo ""
  echo "Validates skill structure and required fields."
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
fi

SKILL_DIR="$1"
ERRORS=()
WARNINGS=()

# Check skill directory exists
if [[ ! -d "$SKILL_DIR" ]]; then
  echo "❌ Error: Directory not found: $SKILL_DIR"
  exit 1
fi

SKILL_NAME=$(basename "$SKILL_DIR")

echo "🔍 Validating skill: $SKILL_NAME"
echo ""

# Check SKILL.md exists
if [[ ! -f "$SKILL_DIR/SKILL.md" ]]; then
  ERRORS+=("Missing required file: SKILL.md")
else
  # Check frontmatter
  FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$SKILL_DIR/SKILL.md" | head -20)
  
  if [[ -z "$FRONTMATTER" ]]; then
    ERRORS+=("SKILL.md missing YAML frontmatter (---)")
  else
    # Check for name field
    if ! echo "$FRONTMATTER" | grep -q "^name:"; then
      ERRORS+=("SKILL.md frontmatter missing 'name' field")
    fi
    
    # Check for description field
    if ! echo "$FRONTMATTER" | grep -q "^description:"; then
      ERRORS+=("SKILL.md frontmatter missing 'description' field")
    fi
    
    # Check description is not TODO
    if grep -q "TODO:" "$SKILL_DIR/SKILL.md"; then
      WARNINGS+=("SKILL.md contains TODO placeholders - fill these in before publishing")
    fi
  fi
fi

# Check naming conventions
if ! [[ "$SKILL_NAME" =~ ^[a-z0-9-]+$ ]]; then
  ERRORS+=("Skill folder name must be lowercase letters, digits, and hyphens only. Got: $SKILL_NAME")
fi

if [[ ${#SKILL_NAME} -gt 64 ]]; then
  ERRORS+=("Skill name must be 64 characters or less")
fi

# Check for forbidden files
FORBIDDEN_FILES=("README.md" "CHANGELOG.md" "INSTALLATION_GUIDE.md" "QUICK_REFERENCE.md" "LICENSE" ".git")
for file in "${FORBIDDEN_FILES[@]}"; do
  if [[ -e "$SKILL_DIR/$file" ]]; then
    WARNINGS+=("Unnecessary file detected: $file (skills should only contain essential files)")
  fi
done

# Check scripts are not empty
if [[ -d "$SKILL_DIR/scripts" ]]; then
  SCRIPT_COUNT=$(find "$SKILL_DIR/scripts" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" \) 2>/dev/null | wc -l)
  if [[ $SCRIPT_COUNT -eq 0 ]]; then
    WARNINGS+=("scripts/ directory exists but contains no script files")
  fi
fi

# Print results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo "❌ ERRORS (must fix):"
  for err in "${ERRORS[@]}"; do
    echo "   • $err"
  done
  echo ""
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo "⚠️  WARNINGS (should fix):"
  for warn in "${WARNINGS[@]}"; do
    echo "   • $warn"
  done
  echo ""
fi

if [[ ${#ERRORS[@]} -eq 0 && ${#WARNINGS[@]} -eq 0 ]]; then
  echo "✅ All checks passed!"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Exit with error if there are errors
if [[ ${#ERRORS[@]} -gt 0 ]]; then
  exit 1
fi

exit 0
