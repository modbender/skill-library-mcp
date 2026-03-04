#!/bin/bash
# Pre-commit hook for skill security scanning
#
# Installation:
#   cp examples/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# This hook scans any modified skills before allowing a commit.
# CRITICAL findings will block the commit.

SCANNER="skills/claw-skill-guard/scripts/scanner.py"

if [ ! -f "$SCANNER" ]; then
    echo "⚠️  claw-skill-guard not found at $SCANNER"
    echo "   Skipping security scan. Consider installing the skill."
    exit 0
fi

echo "🔍 Scanning modified skills for security issues..."
echo

# Find modified skill directories
MODIFIED_SKILLS=$(git diff --cached --name-only | grep "^skills/" | cut -d/ -f2 | sort -u)

if [ -z "$MODIFIED_SKILLS" ]; then
    # No skills modified, nothing to scan
    exit 0
fi

MAX_RISK=0

for skill in $MODIFIED_SKILLS; do
    if [ -d "skills/$skill" ]; then
        echo "Scanning: skills/$skill"
        python3 "$SCANNER" scan "skills/$skill"
        RESULT=$?
        
        if [ $RESULT -gt $MAX_RISK ]; then
            MAX_RISK=$RESULT
        fi
        echo
    fi
done

if [ $MAX_RISK -eq 2 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ COMMIT BLOCKED: Critical security issues detected"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Review the findings above and fix the issues before committing."
    echo "If you believe these are false positives, you can bypass with:"
    echo "  git commit --no-verify"
    echo
    exit 1
elif [ $MAX_RISK -eq 1 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  WARNING: High-risk patterns detected"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Review the findings above. Commit will proceed, but exercise caution."
    echo
fi

exit 0
