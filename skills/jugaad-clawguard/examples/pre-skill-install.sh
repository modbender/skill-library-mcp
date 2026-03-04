#!/bin/bash

# Example: Pre-skill-install hook
# Add this to your OpenClaw configuration to check skills before installation

SKILL_NAME="$1"
SKILL_AUTHOR="$2"

if [ -z "$SKILL_NAME" ]; then
    echo "Usage: pre-skill-install.sh <skill-name> [author]"
    exit 1
fi

# Check the skill against OSBS
if [ -n "$SKILL_AUTHOR" ]; then
    clawguard check --type skill --name "$SKILL_NAME" --author "$SKILL_AUTHOR" --quiet
else
    clawguard check --type skill --name "$SKILL_NAME" --quiet
fi

EXIT_CODE=$?

case $EXIT_CODE in
    0)
        echo "✅ Skill check passed: $SKILL_NAME"
        exit 0
        ;;
    1)
        echo "⛔ BLOCKED: $SKILL_NAME - known malicious skill"
        exit 1
        ;;
    2)
        echo "⚠️ WARNING: $SKILL_NAME - potential threat detected"
        echo "Do you want to continue? (y/N)"
        read -r response
        if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
            exit 0
        else
            exit 1
        fi
        ;;
    *)
        echo "❌ Error checking skill"
        exit 1
        ;;
esac
