#!/bin/bash
# Orderly Network Registration Tool
# Registers EOA wallet with Orderly for perp trading
# Uses ed25519 keypair for trading authentication

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALLET_FILE="/Users/garysingh/clawd/.eth-wallet.txt"
ORDERLY_KEYS_FILE="${SCRIPT_DIR}/../.orderly-keys.json"
ORDERLY_API="https://api-evm.orderly.org"
BROKER_ID="hyper_claw"  # Using HyperClaw as broker
CHAIN_ID=8453  # Base mainnet

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🔐 Orderly Network Registration${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo

# Check dependencies
check_deps() {
    local missing=()
    command -v openssl >/dev/null || missing+=("openssl")
    command -v curl >/dev/null || missing+=("curl")
    command -v jq >/dev/null || missing+=("jq")
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}Missing dependencies: ${missing[*]}${NC}"
        exit 1
    fi
}

# Load wallet
load_wallet() {
    if [ ! -f "$WALLET_FILE" ]; then
        echo -e "${RED}Wallet file not found: $WALLET_FILE${NC}"
        exit 1
    fi
    
    # Extract private key from wallet file (handles "Private Key: 0x..." format)
    PRIVATE_KEY=$(grep -i "private" "$WALLET_FILE" | grep -oE '0x[a-fA-F0-9]{64}' | head -1)
    
    if [ -z "$PRIVATE_KEY" ]; then
        echo -e "${RED}Could not extract private key from wallet file${NC}"
        exit 1
    fi
    
    # Get address from private key using cast
    WALLET_ADDRESS=$(/Users/garysingh/.foundry/bin/cast wallet address "$PRIVATE_KEY" 2>/dev/null)
    
    echo -e "${GREEN}Wallet loaded: ${WALLET_ADDRESS}${NC}"
}

# Generate ed25519 keypair for Orderly trading
generate_orderly_keys() {
    echo -e "\n${YELLOW}Generating ed25519 trading keypair...${NC}"
    
    if [ -f "$ORDERLY_KEYS_FILE" ]; then
        echo -e "${YELLOW}Existing keys found at $ORDERLY_KEYS_FILE${NC}"
        ORDERLY_KEY=$(jq -r '.orderly_key' "$ORDERLY_KEYS_FILE")
        echo -e "${GREEN}Using existing key: $ORDERLY_KEY${NC}"
        return
    fi
    
    # Generate ed25519 keypair
    TEMP_KEY="/tmp/orderly_ed25519_$$"
    openssl genpkey -algorithm Ed25519 -out "${TEMP_KEY}.pem" 2>/dev/null
    
    # Extract public key in raw format
    ORDERLY_SECRET=$(openssl pkey -in "${TEMP_KEY}.pem" -outform DER 2>/dev/null | tail -c 32 | xxd -p | tr -d '\n')
    ORDERLY_KEY="ed25519:$(openssl pkey -in "${TEMP_KEY}.pem" -pubout -outform DER 2>/dev/null | tail -c 32 | xxd -p | tr -d '\n')"
    
    # Clean up
    rm -f "${TEMP_KEY}.pem"
    
    # Save keys
    cat > "$ORDERLY_KEYS_FILE" << EOF
{
    "orderly_key": "${ORDERLY_KEY}",
    "orderly_secret": "ed25519:${ORDERLY_SECRET}",
    "wallet_address": "${WALLET_ADDRESS}",
    "chain_id": ${CHAIN_ID},
    "broker_id": "${BROKER_ID}",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    chmod 600 "$ORDERLY_KEYS_FILE"
    echo -e "${GREEN}Keys saved to $ORDERLY_KEYS_FILE${NC}"
    echo -e "${GREEN}Orderly public key: $ORDERLY_KEY${NC}"
}

# Check if already registered
check_registration() {
    echo -e "\n${YELLOW}Checking registration status...${NC}"
    
    # Try to get account info
    local account_id="${WALLET_ADDRESS}:${BROKER_ID}"
    local response=$(curl -s "${ORDERLY_API}/v1/get_account?address=${WALLET_ADDRESS}&broker_id=${BROKER_ID}" 2>/dev/null)
    
    if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
        local existing_account=$(echo "$response" | jq -r '.data.account_id // empty')
        if [ -n "$existing_account" ]; then
            echo -e "${GREEN}Already registered! Account ID: $existing_account${NC}"
            
            # Update keys file with account ID
            if [ -f "$ORDERLY_KEYS_FILE" ]; then
                jq --arg aid "$existing_account" '.account_id = $aid' "$ORDERLY_KEYS_FILE" > "${ORDERLY_KEYS_FILE}.tmp"
                mv "${ORDERLY_KEYS_FILE}.tmp" "$ORDERLY_KEYS_FILE"
            fi
            
            return 0
        fi
    fi
    
    echo -e "${YELLOW}Not registered yet${NC}"
    return 1
}

# Create registration message
create_registration_message() {
    local timestamp=$(($(date +%s) * 1000))
    local nonce="$RANDOM$RANDOM"
    
    # EIP-712 message for registration
    cat << EOF
{
    "brokerId": "${BROKER_ID}",
    "chainId": ${CHAIN_ID},
    "timestamp": ${timestamp},
    "registrationNonce": "${nonce}"
}
EOF
}

# Sign message with EVM wallet
sign_message() {
    local message="$1"
    
    # Orderly uses EIP-712 typed data signing
    # For now, use a simple message hash
    local message_hash=$(echo -n "$message" | openssl dgst -sha256 | cut -d' ' -f2)
    
    # Sign with cast
    /Users/garysingh/.foundry/bin/cast wallet sign --private-key "$PRIVATE_KEY" "0x$message_hash" 2>/dev/null
}

# Register with Orderly
register_account() {
    echo -e "\n${YELLOW}Registering with Orderly Network...${NC}"
    
    local timestamp=$(($(date +%s) * 1000))
    local nonce="$RANDOM$RANDOM$RANDOM"
    
    # The registration message to sign (simplified)
    local reg_message="I'm registering my account on Orderly with nonce: ${nonce}"
    
    # Sign the message
    local signature=$(/Users/garysingh/.foundry/bin/cast wallet sign --private-key "$PRIVATE_KEY" "$reg_message" 2>/dev/null)
    
    if [ -z "$signature" ]; then
        echo -e "${RED}Failed to sign registration message${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Signature: ${signature:0:20}...${NC}"
    
    # Get orderly key from saved file
    ORDERLY_KEY=$(jq -r '.orderly_key' "$ORDERLY_KEYS_FILE")
    
    # Call registration API
    local payload=$(cat << EOF
{
    "message": "${reg_message}",
    "signature": "${signature}",
    "user_address": "${WALLET_ADDRESS}",
    "broker_id": "${BROKER_ID}",
    "chain_id": ${CHAIN_ID},
    "orderly_key": "${ORDERLY_KEY}"
}
EOF
)

    echo -e "${BLUE}Calling registration API...${NC}"
    
    local response=$(curl -s -X POST "${ORDERLY_API}/v1/register_account" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null)
    
    echo -e "${CYAN}Response: $response${NC}"
    
    if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
        local account_id=$(echo "$response" | jq -r '.data.account_id')
        echo -e "${GREEN}✅ Registration successful!${NC}"
        echo -e "${GREEN}Account ID: $account_id${NC}"
        
        # Update keys file with account ID
        jq --arg aid "$account_id" '.account_id = $aid' "$ORDERLY_KEYS_FILE" > "${ORDERLY_KEYS_FILE}.tmp"
        mv "${ORDERLY_KEYS_FILE}.tmp" "$ORDERLY_KEYS_FILE"
        
        return 0
    else
        echo -e "${RED}Registration failed: $(echo "$response" | jq -r '.message // .error // "Unknown error"')${NC}"
        return 1
    fi
}

# Main flow
main() {
    check_deps
    load_wallet
    generate_orderly_keys
    
    if check_registration; then
        echo -e "\n${GREEN}✅ Ready to trade on Orderly Network!${NC}"
        echo -e "${YELLOW}Next step: Deposit USDC collateral${NC}"
    else
        echo -e "\n${YELLOW}Attempting registration...${NC}"
        echo -e "${RED}Note: Orderly registration requires EIP-712 typed data signing${NC}"
        echo -e "${RED}This simplified script may not work - may need full SDK${NC}"
        
        # Try registration anyway
        register_account
    fi
    
    echo
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Keys stored at: $ORDERLY_KEYS_FILE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

# Run
main "$@"
