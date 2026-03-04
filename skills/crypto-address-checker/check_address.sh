#!/bin/bash
# Check address with auto-sync if needed

set -e

ADDRESS=$1

if [ -z "$ADDRESS" ]; then
    echo "Usage: ./check_address.sh <ethereum_address>"
    echo "Example: ./check_address.sh 0x1234567890abcdef1234567890abcdef12345678"
    exit 1
fi

cd "$(dirname "$0")"
source venv/bin/activate

# Check if address is in database
RESULT=$(python3 crypto_check_db.py "$ADDRESS" 2>&1)

if echo "$RESULT" | grep -q "not in database"; then
    echo "⏳ Address not in database. Syncing from Etherscan now..."
    echo ""
    
    # Sync immediately
    if [ -z "$ETHERSCAN_API_KEY" ]; then
        echo "❌ ETHERSCAN_API_KEY not set!"
        echo "   Export it or run: ./setup.sh"
        exit 1
    fi
    
    python3 sync_worker.py --add-address "$ADDRESS" 2>&1 | grep -v "^$"
    python3 sync_worker.py --max-jobs 1 2>&1 | grep -v "DeprecationWarning"
    echo ""
    echo "✅ Sync complete! Showing results:"
    echo ""
fi

# Show final results
python3 crypto_check_db.py "$ADDRESS"
