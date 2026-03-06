#!/bin/bash
# Bittensor SN85 Vibe Miner - Storage Configuration
# Sets up BackBlaze B2 or Hippius for video storage

set -e

echo "🐍 SN85 Vibe Miner - Storage Setup"
echo "===================================="
echo
echo "Miners need object storage to share processed videos with validators."
echo
echo "Choose storage backend:"
echo "  1) BackBlaze B2 (centralized, reliable, $6/TB/month)"
echo "  2) Hippius (decentralized, Bittensor SN75, pay-per-use)"
echo

read -p "Selection (1 or 2): " -n 1 STORAGE_CHOICE
echo
echo

if [ "$STORAGE_CHOICE" == "1" ]; then
    echo "📦 BackBlaze B2 Setup"
    echo "====================="
    echo
    echo "1. Go to: https://www.backblaze.com/b2/sign-up.html"
    echo "2. Create account and bucket"
    echo "3. Generate Application Key (read/write access)"
    echo
    read -p "Press Enter when ready to input credentials..."
    echo
    
    read -p "Bucket Name: " B2_BUCKET
    read -p "Application Key ID: " B2_KEY_ID
    read -sp "Application Key: " B2_KEY
    echo
    read -p "Endpoint (e.g., s3.us-west-004.backblazeb2.com): " B2_ENDPOINT
    echo
    
    # Save to config file
    CONFIG_FILE="$HOME/.sn85_storage_config"
    cat > "$CONFIG_FILE" << EOF
# SN85 Vibe Miner Storage Configuration
# Backend: BackBlaze B2

export STORAGE_BACKEND="backblaze"
export B2_BUCKET_NAME="$B2_BUCKET"
export B2_APPLICATION_KEY_ID="$B2_KEY_ID"
export B2_APPLICATION_KEY="$B2_KEY"
export B2_ENDPOINT="$B2_ENDPOINT"
EOF
    
    chmod 600 "$CONFIG_FILE"
    
    echo "✅ BackBlaze B2 credentials saved to $CONFIG_FILE"
    echo
    echo "⚠️  IMPORTANT: Update miner config files with:"
    echo "   Bucket: $B2_BUCKET"
    echo "   Endpoint: $B2_ENDPOINT"
    echo
    
elif [ "$STORAGE_CHOICE" == "2" ]; then
    echo "📦 Hippius Setup (Bittensor SN75)"
    echo "=================================="
    echo
    echo "Hippius is decentralized storage on Bittensor Subnet 75."
    echo
    echo "Setup options:"
    echo "  1) Use S3-compatible API (recommended for miners)"
    echo "  2) Use IPFS gateway"
    echo
    read -p "Selection (1 or 2): " -n 1 HIPPIUS_MODE
    echo
    echo
    
    if [ "$HIPPIUS_MODE" == "1" ]; then
        echo "📋 Hippius S3 API Setup"
        echo
        echo "1. Get API credentials from Hippius provider"
        echo "2. Create bucket via Hippius dashboard"
        echo
        read -p "Press Enter when ready..."
        echo
        
        read -p "Bucket Name: " HIPPIUS_BUCKET
        read -p "Access Key ID: " HIPPIUS_KEY_ID
        read -sp "Secret Access Key: " HIPPIUS_SECRET
        echo
        read -p "S3 Endpoint: " HIPPIUS_ENDPOINT
        echo
        
        CONFIG_FILE="$HOME/.sn85_storage_config"
        cat > "$CONFIG_FILE" << EOF
# SN85 Vibe Miner Storage Configuration
# Backend: Hippius (S3-compatible)

export STORAGE_BACKEND="hippius-s3"
export HIPPIUS_BUCKET_NAME="$HIPPIUS_BUCKET"
export HIPPIUS_ACCESS_KEY_ID="$HIPPIUS_KEY_ID"
export HIPPIUS_SECRET_ACCESS_KEY="$HIPPIUS_SECRET"
export HIPPIUS_ENDPOINT="$HIPPIUS_ENDPOINT"
EOF
        
        chmod 600 "$CONFIG_FILE"
        
        echo "✅ Hippius S3 credentials saved to $CONFIG_FILE"
        
    else
        echo "📋 Hippius IPFS Setup"
        echo
        echo "IPFS mode requires running Hippius node or using gateway."
        echo "This is more complex and may have latency issues for mining."
        echo
        echo "Recommended: Use S3 mode instead (option 1)"
        echo
        read -p "Continue with IPFS anyway? (y/N): " -n 1 CONFIRM
        echo
        
        if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
            echo "Aborting. Run script again and choose S3 mode."
            exit 0
        fi
        
        read -p "IPFS Gateway URL: " IPFS_GATEWAY
        read -p "Hippius Wallet Address: " HIPPIUS_WALLET
        
        CONFIG_FILE="$HOME/.sn85_storage_config"
        cat > "$CONFIG_FILE" << EOF
# SN85 Vibe Miner Storage Configuration
# Backend: Hippius (IPFS)

export STORAGE_BACKEND="hippius-ipfs"
export IPFS_GATEWAY="$IPFS_GATEWAY"
export HIPPIUS_WALLET="$HIPPIUS_WALLET"
EOF
        
        chmod 600 "$CONFIG_FILE"
        
        echo "✅ Hippius IPFS config saved to $CONFIG_FILE"
    fi
    
else
    echo "❌ Invalid selection"
    exit 1
fi

echo
echo "===================================="
echo "✅ Storage configuration complete!"
echo "===================================="
echo
echo "Next steps:"
echo "  1. Source the config: source $CONFIG_FILE"
echo "  2. Update miner config files with storage credentials"
echo "  3. Test upload before registering miners"
echo
echo "Config file location: $CONFIG_FILE"
echo "Keep this file secure (contains credentials)"
echo
