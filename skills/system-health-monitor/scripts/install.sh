#!/bin/bash
# Install script for System Health Monitor
# Generates script hashes for integrity checking

set -e

SKILL_DIR="${1:-$HOME/.openclaw/workspace/skills/system-health-monitor}"
SCRIPTS_DIR="$SKILL_DIR/scripts"
HASH_FILE="$SCRIPTS_DIR/.script_hashes"

echo "Installing System Health Monitor..."
echo "Skill directory: $SKILL_DIR"

# Create directories
mkdir -p "$SKILL_DIR/data"
mkdir -p "$SKILL_DIR/logs"

# Generate hashes for all scripts
echo "Generating script integrity hashes..."
{
    echo "# Script SHA256 hashes - generated on $(date -Iseconds)"
    echo "# DO NOT MODIFY THIS FILE MANUALLY"
    echo ""
    
    for script in "$SCRIPTS_DIR"/*.sh; do
        if [[ -f "$script" ]]; then
            hash=$(sha256sum "$script" | awk '{print $1}')
            basename=$(basename "$script")
            echo "$basename:$hash"
            echo "  - $basename: $hash"
        fi
    done
} > "$HASH_FILE"

echo ""
echo "Installation complete!"
echo ""
echo "To use the skill:"
echo "  1. Set environment variable: export OPENCLAW_WORKSPACE=~/.openclaw/workspace"
echo "  2. Run: $SCRIPTS_DIR/health-check.sh status"
echo ""
echo "To verify script integrity:"
echo "  $SCRIPTS_DIR/health-check.sh hash"
