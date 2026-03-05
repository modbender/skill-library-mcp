#!/bin/bash
#
# Daily Briefing - Full Pipeline
# Generates and sends the briefing. Designed for cron execution.
#
# Usage: ./generate-and-send.sh
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="${SKILL_DIR}/config/config.yaml"

# Default recipient
RECIPIENT="paulkingham@mac.com"

# Read recipient from config if available
if [[ -f "$CONFIG_FILE" ]]; then
    config_recipient=$(grep -E "^\s*recipient:" "$CONFIG_FILE" | head -1 | cut -d: -f2- | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sed 's/^"//' | sed 's/"$//' | sed "s/^'//" | sed "s/'$//")
    if [[ -n "$config_recipient" ]]; then
        RECIPIENT="$config_recipient"
    fi
fi

# Status files
STATUS_FILE="${SKILL_DIR}/.last-status"
RUN_FILE="${SKILL_DIR}/.last-run"

# Run the briefing pipeline
echo "[$(date -Iseconds)] Starting daily briefing..." >> "$RUN_FILE"

# Generate and send
if "${SCRIPT_DIR}/send-briefing.sh" "$RECIPIENT" >> "$RUN_FILE" 2>&1; then
    echo "success $(date +%s)" > "$STATUS_FILE"
    echo "[$(date -Iseconds)] Briefing completed successfully" >> "$RUN_FILE"
    exit 0
else
    echo "error $(date +%s)" > "$STATUS_FILE"
    echo "[$(date -Iseconds)] Briefing failed" >> "$RUN_FILE"
    exit 1
fi
