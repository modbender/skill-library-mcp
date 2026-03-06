#!/bin/bash
# Uninstall etf-investor skill

set -e

echo "Uninstalling etf-investor skill..."

DATA_DIR="$HOME/.clawdbot/etf_investor"

# Ask for confirmation
read -p "This will delete all your positions and alerts. Are you sure? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Uninstall cancelled."
    exit 0
fi

# Remove data directory
if [ -d "$DATA_DIR" ]; then
    rm -rf "$DATA_DIR"
    echo "Removed data directory: $DATA_DIR"
else
    echo "Data directory not found: $DATA_DIR"
fi

echo "ETF Investor skill uninstalled successfully."
