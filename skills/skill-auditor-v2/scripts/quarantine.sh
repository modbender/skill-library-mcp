#!/usr/bin/env bash
# Quarantine & audit a skill before installation.
# Uses Skill Auditor v2.0 with 0-100 numeric scoring.
# Usage: quarantine.sh <source_skill_dir> [production_skills_dir]
#        quarantine.sh --slug <skill-name> [production_skills_dir]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT_SCRIPT="$SCRIPT_DIR/audit_skill.py"
PROD_DIR="${2:-/home/node/.openclaw/workspace/skills}"

if [ $# -lt 1 ]; then
    echo "Usage: quarantine.sh <source_skill_dir> [production_skills_dir]"
    echo "       quarantine.sh --slug <skill-name> [production_skills_dir]"
    exit 2
fi

# Handle --slug mode
if [ "$1" == "--slug" ]; then
    if [ $# -lt 2 ]; then
        echo "Error: --slug requires a skill name"
        exit 2
    fi
    SLUG="$2"
    PROD_DIR="${3:-$PROD_DIR}"
    echo "📦 Fetching and auditing slug: $SLUG"
    echo ""
    echo "🔍 Running security audit..."
    echo ""
    set +e
    python3 "$AUDIT_SCRIPT" --slug "$SLUG" --human
    EXIT_CODE=$?
    set -e
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Skill passed audit (score ≤ 20). Safe to install."
    elif [ $EXIT_CODE -eq 1 ]; then
        echo "⚠️  Skill needs review (score 21-60). Inspect findings above."
    else
        echo "🚫 Skill is dangerous (score > 60). Do NOT install."
    fi
    exit $EXIT_CODE
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

cp -r "$SOURCE" "$QUARANTINE_DIR/$SKILL_NAME"
echo "📋 Files copied to quarantine."

echo ""
echo "🔍 Running security audit..."
echo ""

set +e
python3 "$AUDIT_SCRIPT" "$QUARANTINE_DIR/$SKILL_NAME" --human
EXIT_CODE=$?
set -e

# Save JSON report
python3 "$AUDIT_SCRIPT" "$QUARANTINE_DIR/$SKILL_NAME" --json > "$QUARANTINE_DIR/audit-report.json" 2>/dev/null || true
echo "📄 JSON report saved to: $QUARANTINE_DIR/audit-report.json"

# Extract numeric score from JSON
SCORE=$(python3 -c "import json; r=json.load(open('$QUARANTINE_DIR/audit-report.json')); print(r.get('numeric_score', 999))" 2>/dev/null || echo "999")

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Skill passed audit (score: $SCORE/100)."
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
    echo "⚠️  Skill needs review (score: $SCORE/100)."
    echo "🚫 Auto-install blocked. Review findings above."
    echo ""
    echo "If reviewed and accepted:"
    echo "  cp -r '$QUARANTINE_DIR/$SKILL_NAME' '$PROD_DIR/$SKILL_NAME'"
else
    echo ""
    echo "🔴 Skill is dangerous (score: $SCORE/100)."
    echo "🚫 Installation BLOCKED."
    echo "📄 Full report: $QUARANTINE_DIR/audit-report.json"
fi

exit $EXIT_CODE
