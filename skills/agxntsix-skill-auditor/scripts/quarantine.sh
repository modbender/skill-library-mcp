#!/usr/bin/env bash
# Quarantine & audit a skill before installation.
# Usage: quarantine.sh <source_skill_dir> [production_skills_dir]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT_SCRIPT="$SCRIPT_DIR/audit_skill.py"
PROD_DIR="${2:-/home/node/.openclaw/workspace/skills}"

if [ $# -lt 1 ]; then
    echo "Usage: quarantine.sh <source_skill_dir> [production_skills_dir]"
    exit 2
fi

SOURCE="$(realpath "$1")"
SKILL_NAME="$(basename "$SOURCE")"

if [ ! -d "$SOURCE" ]; then
    echo "❌ Source directory does not exist: $SOURCE"
    exit 2
fi

# Create quarantine directory
QUARANTINE_DIR=$(mktemp -d "/tmp/skill-quarantine-${SKILL_NAME}-XXXXXX")
echo "📦 Quarantining '$SKILL_NAME' to: $QUARANTINE_DIR"

# Copy files to quarantine (never touch production)
cp -r "$SOURCE" "$QUARANTINE_DIR/$SKILL_NAME"
echo "📋 Files copied to quarantine."

# Run audit
echo ""
echo "🔍 Running security audit..."
echo ""

set +e
python3 "$AUDIT_SCRIPT" "$QUARANTINE_DIR/$SKILL_NAME" --human
EXIT_CODE=$?
set -e

# Also save JSON report
python3 "$AUDIT_SCRIPT" "$QUARANTINE_DIR/$SKILL_NAME" --json > "$QUARANTINE_DIR/audit-report.json" 2>/dev/null || true
echo "📄 JSON report saved to: $QUARANTINE_DIR/audit-report.json"

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Skill passed audit (CLEAN/LOW)."
    echo ""
    read -p "Install '$SKILL_NAME' to $PROD_DIR/$SKILL_NAME? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "$PROD_DIR/$SKILL_NAME" ]; then
            echo "⚠️  Skill already exists at $PROD_DIR/$SKILL_NAME"
            read -p "Overwrite? [y/N] " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "❌ Installation cancelled."
                exit 0
            fi
            rm -rf "$PROD_DIR/$SKILL_NAME"
        fi
        cp -r "$QUARANTINE_DIR/$SKILL_NAME" "$PROD_DIR/$SKILL_NAME"
        echo "✅ Installed to $PROD_DIR/$SKILL_NAME"
    else
        echo "❌ Installation cancelled."
    fi
elif [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "⚠️  Skill has MEDIUM risk findings."
    echo "🚫 Automatic installation BLOCKED. Review findings above."
    echo "📄 Full report: $QUARANTINE_DIR/audit-report.json"
    echo ""
    echo "If you've reviewed and accept the risks:"
    echo "  cp -r '$QUARANTINE_DIR/$SKILL_NAME' '$PROD_DIR/$SKILL_NAME'"
else
    echo ""
    echo "🔴 Skill has HIGH/CRITICAL risk findings."
    echo "🚫 Installation BLOCKED. This skill may be malicious."
    echo "📄 Full report: $QUARANTINE_DIR/audit-report.json"
    echo ""
    echo "Quarantined files preserved for analysis at:"
    echo "  $QUARANTINE_DIR/"
fi

exit $EXIT_CODE
