#!/bin/bash

# Example: Pre-exec command hook
# Use this to check commands before execution

COMMAND="$1"

if [ -z "$COMMAND" ]; then
    echo "Usage: pre-exec-hook.sh '<command>'"
    exit 1
fi

# Check the command against OSBS
clawguard check --type command --input "$COMMAND" --quiet

EXIT_CODE=$?

case $EXIT_CODE in
    0)
        # Safe - execute the command
        exit 0
        ;;
    1)
        echo "⛔ BLOCKED: Command contains known threat indicators"
        echo "Command: $COMMAND"
        exit 1
        ;;
    2)
        echo "⚠️ WARNING: Command may be dangerous"
        echo "Command: $COMMAND"
        exit 2
        ;;
    *)
        echo "❌ Error checking command"
        exit 1
        ;;
esac
