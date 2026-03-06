#!/usr/bin/env bash
# Check that all expected skill files exist
set -euo pipefail

SKILL_DIR="$1"

if [[ ! -d "$SKILL_DIR" ]]; then
    echo "ERROR: Skill directory not found: $SKILL_DIR"
    exit 1
fi

required_files=(
    "SKILL.md"
    "skill.yml"
    "README.md"
)

optional_files=(
    "tests/test-triggers.json"
    "scripts/README.md"
    "references/README.md"
    "CHANGELOG.md"
)

errors=0

echo "Checking required files..."
for file in "${required_files[@]}"; do
    if [[ ! -f "$SKILL_DIR/$file" ]]; then
        echo "ERROR: Required file missing: $file"
        errors=$((errors + 1))
    else
        echo "✓ $file"
    fi
done

echo ""
echo "Checking optional files..."
for file in "${optional_files[@]}"; do
    if [[ ! -f "$SKILL_DIR/$file" ]]; then
        echo "⚠ Optional file missing: $file"
    else
        echo "✓ $file"
    fi
done

if [[ $errors -gt 0 ]]; then
    echo ""
    echo "ERROR: $errors required files missing"
    exit 1
fi

echo ""
echo "✓ All required files present"
exit 0
