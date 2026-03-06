#!/bin/bash
# Bittensor SN85 Vibe Miner - Registration Script
# Registers miners on Subnet 85

set -e

echo "🐍 SN85 Vibe Miner - Subnet Registration"
echo "========================================="
echo

# Check wallet
WALLET_NAME="${WALLET_NAME:-default}"

echo "📋 Checking wallet: $WALLET_NAME"
if ! btcli wallet list 2>/dev/null | grep -q "$WALLET_NAME"; then
    echo "❌ Wallet '$WALLET_NAME' not found"
    echo
    read -p "Create new wallet? (y/N): " -n 1 CREATE_WALLET
    echo
    
    if [[ $CREATE_WALLET =~ ^[Yy]$ ]]; then
        btcli wallet create --wallet.name "$WALLET_NAME"
        echo
        echo "⚠️  IMPORTANT: Save your mnemonic phrase securely!"
        read -p "Press Enter when you've saved it..."
    else
        echo "Aborting. Create wallet first: btcli wallet create"
        exit 1
    fi
fi

# Check balance
echo
echo "💰 Checking wallet balance..."
BALANCE=$(btcli wallet balance --wallet.name "$WALLET_NAME" --subtensor.network finney 2>/dev/null | grep "Free Balance" | awk '{print $3}' | tr -d 'τ' || echo "0")

echo "Balance: $BALANCE τ"

if (( $(echo "$BALANCE < 0.5" | bc -l) )); then
    echo "❌ Insufficient balance. Need at least 0.5 τ"
    echo
    echo "Fund your wallet address, then re-run this script."
    btcli wallet balance --wallet.name "$WALLET_NAME" --subtensor.network finney
    exit 1
fi

echo "✅ Sufficient balance for registration"
echo

# Choose miner types
echo "Which miners to register?"
echo "  1) Upscaler only (~0.13 τ)"
echo "  2) Compressor only (~0.13 τ)"
echo "  3) Both (~0.26 τ)"
echo

read -p "Selection (1-3): " -n 1 MINER_CHOICE
echo
echo

REGISTER_UPSCALER=false
REGISTER_COMPRESSOR=false

case $MINER_CHOICE in
    1) REGISTER_UPSCALER=true ;;
    2) REGISTER_COMPRESSOR=true ;;
    3) REGISTER_UPSCALER=true; REGISTER_COMPRESSOR=true ;;
    *) echo "❌ Invalid selection"; exit 1 ;;
esac

# Create hotkeys if needed
if [ "$REGISTER_UPSCALER" = true ]; then
    echo "📝 Upscaler hotkey setup..."
    if ! btcli wallet list 2>/dev/null | grep -A5 "$WALLET_NAME" | grep -q "mining"; then
        echo "Creating hotkey 'mining'..."
        btcli wallet new_hotkey --wallet.name "$WALLET_NAME" --wallet.hotkey mining
    else
        echo "✅ Hotkey 'mining' already exists"
    fi
    echo
fi

if [ "$REGISTER_COMPRESSOR" = true ]; then
    echo "📝 Compressor hotkey setup..."
    if ! btcli wallet list 2>/dev/null | grep -A5 "$WALLET_NAME" | grep -q "mining2"; then
        echo "Creating hotkey 'mining2'..."
        btcli wallet new_hotkey --wallet.name "$WALLET_NAME" --wallet.hotkey mining2
    else
        echo "✅ Hotkey 'mining2' already exists"
    fi
    echo
fi

# Register on subnet
echo "========================================="
echo "📡 Registering on Subnet 85"
echo "========================================="
echo

if [ "$REGISTER_UPSCALER" = true ]; then
    echo "🔧 Registering upscaler (hotkey: mining)..."
    echo "Cost: ~0.13 τ"
    echo
    read -p "Confirm registration? (y/N): " -n 1 CONFIRM
    echo
    
    if [[ $CONFIRM =~ ^[Yy]$ ]]; then
        btcli subnet register --netuid 85 \
            --wallet.name "$WALLET_NAME" \
            --wallet.hotkey mining \
            --subtensor.network finney
        
        echo
        echo "✅ Upscaler registered!"
        
        # Get UID
        UID=$(btcli subnet list --netuid 85 --subtensor.network finney 2>/dev/null | grep "mining" | awk '{print $1}')
        echo "   UID: $UID"
        echo "   Hotkey: mining"
        echo
        
        # Save to env file
        echo "export UPSCALER_UID=$UID" >> ~/.sn85_miner_env
    else
        echo "Skipped upscaler registration"
    fi
    echo
fi

if [ "$REGISTER_COMPRESSOR" = true ]; then
    echo "🔧 Registering compressor (hotkey: mining2)..."
    echo "Cost: ~0.13 τ"
    echo
    read -p "Confirm registration? (y/N): " -n 1 CONFIRM
    echo
    
    if [[ $CONFIRM =~ ^[Yy]$ ]]; then
        btcli subnet register --netuid 85 \
            --wallet.name "$WALLET_NAME" \
            --wallet.hotkey mining2 \
            --subtensor.network finney
        
        echo
        echo "✅ Compressor registered!"
        
        # Get UID
        UID=$(btcli subnet list --netuid 85 --subtensor.network finney 2>/dev/null | grep "mining2" | awk '{print $1}')
        echo "   UID: $UID"
        echo "   Hotkey: mining2"
        echo
        
        # Save to env file
        echo "export COMPRESSOR_UID=$UID" >> ~/.sn85_miner_env
    else
        echo "Skipped compressor registration"
    fi
    echo
fi

echo "========================================="
echo "✅ Registration complete!"
echo "========================================="
echo
echo "📋 Next Steps:"
echo "   1. Configure storage (if not done): ./scripts/storage_setup.sh"
echo "   2. Update miner config files with UIDs and storage"
echo "   3. Start miners with PM2"
echo "   4. Monitor during immunity period (24h)"
echo
echo "⚠️  CRITICAL: First 7200 blocks (~24h) is immunity period"
echo "   Miners cannot be deregistered, but must perform well"
echo "   to establish good scores after immunity ends."
echo
echo "Environment file: ~/.sn85_miner_env"
echo "Source it: source ~/.sn85_miner_env"
echo
