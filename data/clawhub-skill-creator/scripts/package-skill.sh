#!/bin/bash
#
# Package skill for clawhub distribution
# Usage: ./package-skill.sh [skill-path] [output-dir]
#

set -e

SKILL_PATH="${1:-.}"
OUTPUT_DIR="${2:-./dist}"

# Validate skill exists
if [[ ! -d "$SKILL_PATH" ]]; then
    echo "Error: Skill directory not found: $SKILL_PATH"
    exit 1
fi

# Get skill name from directory
SKILL_NAME=$(basename "$SKILL_PATH")

echo "Packaging skill: $SKILL_NAME"
echo "Source: $SKILL_PATH"
echo "Output: $OUTPUT_DIR"

# Validate structure
echo ""
echo "Validating structure..."

if [[ ! -f "$SKILL_PATH/SKILL.md" ]]; then
    echo "❌ SKILL.md not found"
    exit 1
fi
echo "✅ SKILL.md exists"

if [[ ! -f "$SKILL_PATH/_meta.json" ]]; then
    echo "❌ _meta.json not found"
    exit 1
fi
echo "✅ _meta.json exists"

if [[ ! -f "$SKILL_PATH/LICENSE.txt" ]]; then
    echo "❌ LICENSE.txt not found"
    exit 1
fi
echo "✅ LICENSE.txt exists"

# Validate JSON
if ! jq . "$SKILL_PATH/_meta.json" > /dev/null 2>&1; then
    echo "❌ _meta.json is invalid JSON"
    exit 1
fi
echo "✅ _meta.json is valid JSON"

# Check name matches
FRONTMATTER_NAME=$(grep "^name:" "$SKILL_PATH/SKILL.md" | head -1 | sed 's/name:[[:space:]]*//')
META_NAME=$(jq -r '.name' "$SKILL_PATH/_meta.json")

if [[ "$FRONTMATTER_NAME" != "$META_NAME" ]]; then
    echo "❌ Name mismatch: SKILL.md='$FRONTMATTER_NAME', _meta.json='$META_NAME'"
    exit 1
fi
echo "✅ Names match: $META_NAME"

# Check line count
LINE_COUNT=$(wc -l < "$SKILL_PATH/SKILL.md")
if [[ $LINE_COUNT -gt 300 ]]; then
    echo "⚠️  WARNING: SKILL.md has $LINE_COUNT lines (recommended: <300)"
else
    echo "✅ SKILL.md line count: $LINE_COUNT"
fi

# Check for extraneous files
if [[ -f "$SKILL_PATH/README.md" ]]; then
    echo "⚠️  WARNING: README.md found (consider removing)"
fi

if [[ -f "$SKILL_PATH/CHANGELOG.md" ]]; then
    echo "⚠️  WARNING: CHANGELOG.md found (consider removing)"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create package (zip with .skill extension)
PACKAGE_FILE="$OUTPUT_DIR/$SKILL_NAME.skill"

echo ""
echo "Creating package: $PACKAGE_FILE"

# Exclude .git and other unnecessary files
cd "$SKILL_PATH" && zip -r "$OLDPWD/$PACKAGE_FILE" . \
    -x "*.git*" \
    -x "*.DS_Store" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*.egg-info*" \
    -x "node_modules/*"

echo ""
echo "✅ Package created: $PACKAGE_FILE"
echo ""
echo "To publish:"
echo "  clawhub publish $SKILL_PATH --version X.Y.Z"
echo ""
echo "Or install locally:"
echo "  clawhub install $PACKAGE_FILE"