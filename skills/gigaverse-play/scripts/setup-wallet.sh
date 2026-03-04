#!/bin/bash
# Gigaverse Wallet Setup Script
# Usage: ./setup-wallet.sh generate | ./setup-wallet.sh import "0x..."

set -e

SECRETS_DIR="${HOME}/.secrets"
KEY_FILE="${SECRETS_DIR}/gigaverse-private-key.txt"
ADDR_FILE="${SECRETS_DIR}/gigaverse-address.txt"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

print_warning() {
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  CRITICAL SECURITY WARNING ⚠️                           ║${NC}"
    echo -e "${RED}╠════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${RED}║  Your private key controls ALL funds in this wallet.       ║${NC}"
    echo -e "${RED}║                                                            ║${NC}"
    echo -e "${RED}║  • NEVER share it with anyone                              ║${NC}"
    echo -e "${RED}║  • NEVER commit it to git                                  ║${NC}"
    echo -e "${RED}║  • NEVER paste it in chat or logs                          ║${NC}"
    echo -e "${RED}║  • BACK IT UP in a secure password manager                 ║${NC}"
    echo -e "${RED}║                                                            ║${NC}"
    echo -e "${RED}║  If compromised, ALL assets are permanently lost.          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Ensure secrets directory exists with proper permissions
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

# Check if wallet already exists
if [ -f "$KEY_FILE" ]; then
    echo -e "${YELLOW}⚠️  Wallet already exists at: $KEY_FILE${NC}"
    echo "   To create a new wallet, first backup and remove the existing key."
    echo ""
    if [ -f "$ADDR_FILE" ]; then
        echo "   Current Address: $(cat "$ADDR_FILE")"
    fi
    exit 1
fi

case "$1" in
    generate)
        echo "🔐 Generating new wallet..."
        
        # Generate random 32 bytes and convert to hex
        PRIVATE_KEY="0x$(openssl rand -hex 32)"
        
        # Derive address using cast (foundry) if available, otherwise use node
        if command -v cast &> /dev/null; then
            ADDRESS=$(cast wallet address "$PRIVATE_KEY" 2>/dev/null)
        else
            # Fallback: use node with viem
            ADDRESS=$(node -e "
                const { privateKeyToAccount } = require('viem/accounts');
                const account = privateKeyToAccount('$PRIVATE_KEY');
                console.log(account.address);
            " 2>/dev/null || echo "")
        fi
        
        if [ -z "$ADDRESS" ]; then
            echo "❌ Failed to derive address. Install foundry (cast) or ensure viem is available."
            exit 1
        fi
        
        # Save private key
        echo "$PRIVATE_KEY" > "$KEY_FILE"
        chmod 600 "$KEY_FILE"
        
        # Save address
        echo "$ADDRESS" > "$ADDR_FILE"
        chmod 644 "$ADDR_FILE"
        
        print_warning
        
        echo -e "${GREEN}✅ Wallet created successfully!${NC}"
        echo ""
        echo "   EOA Address: $ADDRESS"
        echo "   (smart wallet will be deployed on first transaction)"
        echo ""
        echo "   Private key saved to: $KEY_FILE"
        echo ""
        echo -e "${YELLOW}📝 BACKUP YOUR KEY NOW before continuing.${NC}"
        ;;
        
    import)
        if [ -z "$2" ]; then
            echo "❌ Usage: $0 import \"0x...\""
            echo "   Provide the private key as the second argument."
            exit 1
        fi
        
        PRIVATE_KEY="$2"
        
        # Validate key format
        if [[ ! "$PRIVATE_KEY" =~ ^0x[a-fA-F0-9]{64}$ ]]; then
            echo "❌ Invalid private key format."
            echo "   Expected: 0x followed by 64 hex characters"
            exit 1
        fi
        
        echo "🔐 Importing wallet..."
        
        # Derive address
        if command -v cast &> /dev/null; then
            ADDRESS=$(cast wallet address "$PRIVATE_KEY" 2>/dev/null)
        else
            ADDRESS=$(node -e "
                const { privateKeyToAccount } = require('viem/accounts');
                const account = privateKeyToAccount('$PRIVATE_KEY');
                console.log(account.address);
            " 2>/dev/null || echo "")
        fi
        
        if [ -z "$ADDRESS" ]; then
            echo "❌ Failed to derive address from key."
            exit 1
        fi
        
        # Save private key
        echo "$PRIVATE_KEY" > "$KEY_FILE"
        chmod 600 "$KEY_FILE"
        
        # Save address
        echo "$ADDRESS" > "$ADDR_FILE"
        chmod 644 "$ADDR_FILE"
        
        print_warning
        
        echo -e "${GREEN}✅ Wallet imported successfully!${NC}"
        echo ""
        echo "   EOA Address: $ADDRESS"
        echo "   Private key saved to: $KEY_FILE"
        ;;
        
    *)
        echo "Gigaverse Wallet Setup"
        echo ""
        echo "Usage:"
        echo "  $0 generate           Generate a new wallet"
        echo "  $0 import \"0x...\"     Import existing private key"
        echo ""
        echo "Files created:"
        echo "  ~/.secrets/gigaverse-private-key.txt  Your private key"
        echo "  ~/.secrets/gigaverse-address.txt      Your EOA address"
        ;;
esac
