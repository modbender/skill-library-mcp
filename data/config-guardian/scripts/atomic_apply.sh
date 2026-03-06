#!/usr/bin/env bash
# atomic_apply.sh - Atomic config apply with auto-rollback
# Usage: atomic_apply.sh <config_path> <new_value>
# Example: atomic_apply.sh "model" "minimax-portal/MiniMax-M2.5"

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONFIG_PATH="${1:?Error: Config path is required. Usage: atomic_apply.sh <config_path> <new_value>}"
NEW_VALUE="${2:?Error: New value is required. Usage: atomic_apply.sh <config_path> <new_value>}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/.openclaw/config-guardian-backups}"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

# Trap for cleanup on exit (error or crash)
ROLLBACK_NEEDED=false
BACKUP_PATH=""

cleanup() {
    if [ "$ROLLBACK_NEEDED" = true ] && [ -n "$BACKUP_PATH" ] && [ -f "$BACKUP_PATH" ]; then
        echo -e "${YELLOW}Rolling back due to failure...${NC}"
        cp "$BACKUP_PATH" "$CONFIG_FILE"
        echo -e "${RED}Rollback complete. Config restored from backup.${NC}"
    fi
}

trap cleanup EXIT

# Step 1: Create backup
echo -e "${YELLOW}[1/4] Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="$BACKUP_DIR/openclaw-$STAMP.json"
cp "$CONFIG_FILE" "$BACKUP_PATH"
echo -e "Backup created: ${GREEN}$BACKUP_PATH${NC}"
ROLLBACK_NEEDED=true

# Step 2: Apply the change
echo -e "${YELLOW}[2/4] Applying change: ${CONFIG_PATH} = ${NEW_VALUE}${NC}"
if ! openclaw config set "$CONFIG_PATH" "$NEW_VALUE"; then
    echo -e "${RED}Failed to apply config change.${NC}"
    exit 1
fi
echo -e "Change applied successfully."

# Step 3: Validate with openclaw doctor
echo -e "${YELLOW}[3/4] Validating config...${NC}"
if ! openclaw doctor --non-interactive; then
    echo -e "${RED}Validation failed! Restoring backup...${NC}"
    exit 1
fi
echo -e "Validation passed."

# Step 4: Success - disable rollback
echo -e "${GREEN}[4/4] ✓ Atomic apply successful!${NC}"
echo -e "Config path: ${CONFIG_PATH}"
echo -e "New value: ${NEW_VALUE}"
echo -e "Backup preserved at: ${BACKUP_PATH}"
ROLLBACK_NEEDED=false

exit 0
