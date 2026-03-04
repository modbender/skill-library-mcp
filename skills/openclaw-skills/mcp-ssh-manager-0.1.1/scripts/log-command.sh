#!/bin/bash
# log-command.sh - Log a command to the workdir commands.md

set -e

# Usage
usage() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Examples:"
    echo "  $0 'df -h'"
    echo "  $0 'free -h'"
    echo ""
    exit 1
}

# Check for workdir
WORKDIR="${PWD}"

# Check if we're in a workdir
if [ ! -f "${WORKDIR}/commands.md" ]; then
    echo "Error: Not in a workdir (commands.md not found)"
    echo "Usage: $0 <workdir-path> <command>"
    echo ""
    echo "Alternative: Specify workdir path"
    echo "  $0 /path/to/workdir 'command'"
    exit 1
fi

# Get command from argument or stdin
if [ -n "$1" ]; then
    COMMAND="$1"
else
    COMMAND=$(cat)
fi

# Validate command
if [ -z "$COMMAND" ]; then
    echo "Error: No command provided"
    usage
fi

# Log command with timestamp
echo "## $(date -Iseconds)" >> "${WORKDIR}/commands.md"
echo "\`${COMMAND}\`" >> "${WORKDIR}/commands.md"
echo "" >> "${WORKDIR}/commands.md"

echo "Command logged:"
echo "  ${COMMAND}"
echo ""
echo "Total commands logged: $(grep -c '^\## ' "${WORKDIR}/commands.md")"
