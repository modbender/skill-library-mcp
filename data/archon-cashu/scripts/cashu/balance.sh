#!/bin/bash
# Archon Cashu Wallet — Check balance
# Usage: balance.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

echo "💰 Cashu Balance"
echo "Mint: $CASHU_MINT_URL"
$CASHU_BIN balance 2>&1
