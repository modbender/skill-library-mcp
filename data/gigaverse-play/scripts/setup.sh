#!/bin/bash
# Gigaverse Skill Setup
# Configures wallet and play mode

set -e

SECRETS_DIR="${HOME}/.secrets"
CONFIG_DIR="${HOME}/.config/gigaverse"
CONFIG_FILE="${CONFIG_DIR}/config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🎮 Gigaverse Skill Setup 🎮        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Create config directory
mkdir -p "$CONFIG_DIR"
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

# Check for existing config
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Existing config found at: $CONFIG_FILE${NC}"
    echo ""
    read -p "Overwrite? (y/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# === WALLET SETUP ===
echo ""
echo -e "${CYAN}=== Wallet Setup ===${NC}"
echo ""

KEY_FILE="${SECRETS_DIR}/gigaverse-private-key.txt"

if [ -f "$KEY_FILE" ]; then
    ADDR_FILE="${SECRETS_DIR}/gigaverse-address.txt"
    EXISTING_ADDR=$(cat "$ADDR_FILE" 2>/dev/null || echo "unknown")
    echo -e "Existing wallet found: ${GREEN}$EXISTING_ADDR${NC}"
    read -p "Use existing wallet? (Y/n): " USE_EXISTING
    
    if [[ "$USE_EXISTING" =~ ^[Nn]$ ]]; then
        echo ""
        echo "1) Generate new wallet"
        echo "2) Import private key"
        read -p "Choice (1/2): " WALLET_CHOICE
        
        if [ "$WALLET_CHOICE" = "1" ]; then
            "$SCRIPT_DIR/setup-wallet.sh" generate
        else
            read -p "Enter private key (0x...): " IMPORT_KEY
            "$SCRIPT_DIR/setup-wallet.sh" import "$IMPORT_KEY"
        fi
    fi
    WALLET_ADDRESS=$(cat "$ADDR_FILE")
else
    echo "No wallet found."
    echo ""
    echo "1) Generate new wallet"
    echo "2) Import private key"
    read -p "Choice (1/2): " WALLET_CHOICE
    
    if [ "$WALLET_CHOICE" = "1" ]; then
        "$SCRIPT_DIR/setup-wallet.sh" generate
    else
        read -p "Enter private key (0x...): " IMPORT_KEY
        "$SCRIPT_DIR/setup-wallet.sh" import "$IMPORT_KEY"
    fi
    WALLET_ADDRESS=$(cat "${SECRETS_DIR}/gigaverse-address.txt")
fi

# === MODE SELECTION ===
echo ""
echo -e "${CYAN}=== Play Mode ===${NC}"
echo ""
echo "How should the agent play Gigaverse?"
echo ""
echo -e "  ${GREEN}1) Autonomous${NC} — Agent makes all decisions"
echo "     • Generates username automatically"
echo "     • Selects faction randomly (or by preference)"
echo "     • Plays dungeons independently"
echo "     • Best for: background operation, fully automated"
echo ""
echo -e "  ${YELLOW}2) Interactive${NC} — Agent asks you at each decision"
echo "     • Asks for username preference"
echo "     • Lets you choose faction"
echo "     • Confirms before dungeon runs"
echo "     • Best for: guided play, human participation"
echo ""
read -p "Choice (1/2) [1]: " MODE_CHOICE

if [ "$MODE_CHOICE" = "2" ]; then
    MODE="interactive"
else
    MODE="autonomous"
fi

echo ""
echo -e "Selected: ${GREEN}$MODE${NC}"

# === PREFERENCES ===
echo ""
echo -e "${CYAN}=== Preferences ===${NC}"
echo ""

# Faction preference
DEFAULT_FACTION="null"
if [ "$MODE" = "autonomous" ]; then
    echo "Default faction for autonomous mode:"
    echo "  0) Random selection"
    echo "  1-N) Specific faction ID (check /factions/summary for options)"
    read -p "Choice [0]: " FACTION_CHOICE
    
    if [ -n "$FACTION_CHOICE" ] && [ "$FACTION_CHOICE" != "0" ]; then
        DEFAULT_FACTION="$FACTION_CHOICE"
    fi
fi

# Energy notifications
read -p "Notify when energy is full? (Y/n): " NOTIFY_ENERGY
if [[ "$NOTIFY_ENERGY" =~ ^[Nn]$ ]]; then
    NOTIFY_FULL="false"
else
    NOTIFY_FULL="true"
fi

# === WRITE CONFIG ===
echo ""
echo -e "${CYAN}=== Saving Configuration ===${NC}"

cat > "$CONFIG_FILE" << EOF
{
  "mode": "$MODE",
  "wallet_address": "$WALLET_ADDRESS",
  "preferences": {
    "default_faction": $DEFAULT_FACTION,
    "username_style": "random",
    "notify_on_full_energy": $NOTIFY_FULL
  },
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo ""
echo -e "${GREEN}✅ Configuration saved to: $CONFIG_FILE${NC}"
echo ""
cat "$CONFIG_FILE"
echo ""

# === SUMMARY ===
echo -e "${CYAN}=== Setup Complete ===${NC}"
echo ""
echo "  Wallet: $WALLET_ADDRESS"
echo "  Mode: $MODE"
echo "  Config: $CONFIG_FILE"
echo ""

if [ "$MODE" = "autonomous" ]; then
    echo -e "${YELLOW}⚠️  Autonomous mode requires a funded wallet to mint Noob.${NC}"
    echo "   Send ETH to your wallet address to get started."
else
    echo "   The agent will ask you at each decision point."
fi

echo ""
echo -e "${GREEN}Ready to enter the Gigaverse! ⚔️${NC}"
