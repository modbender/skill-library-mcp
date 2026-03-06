#!/bin/bash
# Skill Auditor - ClawHub Pre-Install Inspector
# Downloads, audits, and trust-scores a skill before installation
# Usage: bash inspect.sh <skill-slug> [--json]
#
# Workflow:
#   1. Download skill to temp dir via clawhub inspect
#   2. Run security audit
#   3. Calculate trust score
#   4. Show results and recommendation (never auto-installs)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLUG="${1:?Usage: inspect.sh <skill-slug> [--json]}"
JSON_MODE=false

shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --json) JSON_MODE=true; shift ;;
        *) shift ;;
    esac
done

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

if ! $JSON_MODE; then
    echo "========================================="
    echo "  ClawHub Pre-Install Inspector"
    echo "  Skill: $SLUG"
    echo "========================================="
    echo ""
fi

# Step 1: Download
if ! $JSON_MODE; then echo "Downloading $SLUG..."; fi

if ! command -v clawhub &>/dev/null; then
    echo "Error: clawhub CLI not found. Install with: npm install -g clawhub"
    exit 3
fi

# Try clawhub inspect to download
clawhub inspect "$SLUG" --dir "$TEMP_DIR" 2>/dev/null
INSPECT_CODE=$?

if [ $INSPECT_CODE -ne 0 ]; then
    # Fallback: try clawhub download or similar
    if ! $JSON_MODE; then echo "clawhub inspect failed. Trying alternative download..."; fi
    clawhub download "$SLUG" --dir "$TEMP_DIR" 2>/dev/null || {
        echo "Error: Could not download skill '$SLUG'"
        exit 3
    }
fi

# Find the skill directory (might be nested)
SKILL_PATH="$TEMP_DIR/$SLUG"
if [ ! -d "$SKILL_PATH" ]; then
    # Try finding any directory with SKILL.md
    SKILL_PATH=$(find "$TEMP_DIR" -name "SKILL.md" -maxdepth 3 -exec dirname {} \; | head -1)
fi

if [ -z "$SKILL_PATH" ] || [ ! -d "$SKILL_PATH" ]; then
    echo "Error: Could not find skill directory after download"
    exit 3
fi

if ! $JSON_MODE; then
    echo "Downloaded to: $SKILL_PATH"
    echo ""
fi

# Step 2: Security Audit
if ! $JSON_MODE; then
    echo "--- Security Audit ---"
    bash "$SCRIPT_DIR/audit.sh" "$SKILL_PATH"
    AUDIT_CODE=$?
    echo ""
else
    AUDIT_JSON=$(bash "$SCRIPT_DIR/audit.sh" "$SKILL_PATH" --json 2>/dev/null)
    AUDIT_CODE=$?
fi

# Step 3: Trust Score
if ! $JSON_MODE; then
    echo "--- Trust Score ---"
    python3 "$SCRIPT_DIR/trust_score.py" "$SKILL_PATH"
    echo ""
else
    TRUST_JSON=$(python3 "$SCRIPT_DIR/trust_score.py" "$SKILL_PATH" --json 2>/dev/null)
fi

# Step 4: JSON output
if $JSON_MODE; then
    TRUST_SCORE=$(echo "$TRUST_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('trust_score',0))" 2>/dev/null || echo 0)
    echo "{\"slug\":\"$SLUG\",\"audit\":$AUDIT_JSON,\"trust\":$TRUST_JSON,\"install_recommended\":$([ "$TRUST_SCORE" -ge 75 ] && echo true || echo false)}"
    exit $AUDIT_CODE
fi

# Step 5: Recommendation
TRUST_SCORE=$(python3 "$SCRIPT_DIR/trust_score.py" "$SKILL_PATH" --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('trust_score',0))" 2>/dev/null || echo 0)

echo "========================================="
echo "  RECOMMENDATION"
echo "========================================="

if [ "$AUDIT_CODE" -eq 2 ]; then
    echo -e "\033[0;31m  DO NOT INSTALL - Critical security issues found\033[0m"
    echo "  Trust Score: $TRUST_SCORE/100"
    exit 2
elif [ "$TRUST_SCORE" -ge 75 ]; then
    echo -e "\033[0;32m  SAFE TO INSTALL - Trust score $TRUST_SCORE/100\033[0m"
    echo "  Install with: clawhub install $SLUG"
    exit 0
elif [ "$TRUST_SCORE" -ge 60 ]; then
    echo -e "\033[1;33m  REVIEW BEFORE INSTALLING - Trust score $TRUST_SCORE/100\033[0m"
    echo "  Some quality/transparency gaps. Review the audit output above."
    echo "  Install with: clawhub install $SLUG"
    exit 1
else
    echo -e "\033[0;31m  NOT RECOMMENDED - Trust score $TRUST_SCORE/100\033[0m"
    echo "  Low trust score. Review carefully or find an alternative."
    exit 1
fi
