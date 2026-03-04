#!/bin/bash
# Intelligent Router - Auto-Refresh Cron Wrapper
# Usage: Add to cron for hourly model discovery

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

echo "[$(date -Iseconds)] Starting model discovery refresh..."

# Run discovery with auto-update
python3 skills/intelligent-router/scripts/discover_models.py --auto-update

# Check if any models went down
DISCOVERY_FILE="skills/intelligent-router/discovered-models.json"

if [ -f "$DISCOVERY_FILE" ]; then
    UNAVAILABLE=$(jq '.unavailable_models' "$DISCOVERY_FILE")

    if [ "$UNAVAILABLE" -gt 0 ]; then
        echo "⚠️  Warning: $UNAVAILABLE model(s) unavailable"

        # Send alert to main session
        if command -v openclaw &> /dev/null; then
            echo "Model discovery alert: $UNAVAILABLE model(s) failed health check" | \
                openclaw sessions send --label main --message "$(cat)"
        fi
    fi
fi

echo "[$(date -Iseconds)] Model discovery refresh complete"
