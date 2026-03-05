#!/bin/bash
# Bittensor SN85 Vibe Miner - Monitoring Script
# Checks miner status, ranks, and incentives

set -e

INSTALL_DIR="${INSTALL_DIR:-$HOME/vidaio-subnet}"
WALLET_NAME="${WALLET_NAME:-default}"
UPSCALER_UID="${UPSCALER_UID}"
COMPRESSOR_UID="${COMPRESSOR_UID}"

echo "🐍 SN85 Vibe Miner - Status Check"
echo "=================================="
echo

# Check PM2 processes
echo "📊 PM2 Process Status:"
pm2 list | grep -E "video-miner|video-upscaler|video-compressor|video-deleter" || echo "   No miners running"
echo

# Check metagraph if UIDs provided
if [ -n "$UPSCALER_UID" ] || [ -n "$COMPRESSOR_UID" ]; then
    echo "📊 Metagraph Status:"
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    python3 << EOF
from bittensor import metagraph
import numpy as np
import torch
import sys

try:
    meta85 = metagraph(netuid=85, network="finney")
    
    incentives = meta85.I.cpu().numpy() if isinstance(meta85.I, torch.Tensor) else np.array(meta85.I)
    uids = meta85.uids.cpu().numpy() if isinstance(meta85.uids, torch.Tensor) else np.array(meta85.uids)
    
    sorted_indices = np.argsort(incentives)[::-1]
    sorted_uids = uids[sorted_indices]
    
    # Check upscaler
    upscaler_uid = ${UPSCALER_UID:-None}
    if upscaler_uid is not None and upscaler_uid in uids:
        uid_idx = np.where(uids == upscaler_uid)[0][0]
        rank = np.where(sorted_uids == upscaler_uid)[0][0] + 1
        inc = incentives[uid_idx]
        daily_usd = (inc * 7200 / 360) * 205  # Approx earnings
        
        print(f"UID {upscaler_uid} (Upscaler):")
        print(f"  Rank: #{rank}/256")
        print(f"  Incentive: {inc:.6f}")
        print(f"  Est. earnings: ~\${daily_usd:.2f}/day")
        
        if inc < 0.002:
            print(f"  ⚠️  WARNING: Low incentive, deregistration risk!")
        elif rank <= 20:
            print(f"  🔥 TOP 20 miner!")
        print()
    
    # Check compressor
    compressor_uid = ${COMPRESSOR_UID:-None}
    if compressor_uid is not None and compressor_uid in uids:
        uid_idx = np.where(uids == compressor_uid)[0][0]
        rank = np.where(sorted_uids == compressor_uid)[0][0] + 1
        inc = incentives[uid_idx]
        daily_usd = (inc * 7200 / 360) * 205
        
        print(f"UID {compressor_uid} (Compressor):")
        print(f"  Rank: #{rank}/256")
        print(f"  Incentive: {inc:.6f}")
        print(f"  Est. earnings: ~\${daily_usd:.2f}/day")
        
        if inc < 0.002:
            print(f"  ⚠️  WARNING: Low incentive, deregistration risk!")
        print()
        
except Exception as e:
    print(f"❌ Error checking metagraph: {e}")
    sys.exit(1)
EOF
    
    echo
fi

# Check for recent tasks (upscaler)
if pm2 list | grep -q "video-miner "; then
    echo "📝 Recent Upscaler Tasks:"
    tail -100 /root/.pm2/logs/video-miner-error.log 2>/dev/null | \
        grep "Receiving.*Request" | \
        tail -3 || echo "   No recent tasks found"
    echo
fi

# Check for VMAF calculation (compressor)
if pm2 list | grep -q "video-compressor"; then
    echo "🎯 VMAF Calculation Check:"
    if tail -500 /root/.pm2/logs/video-compressor-out.log 2>/dev/null | grep -q "Calculating final video VMAF"; then
        echo "   ✅ VMAF calculation is ACTIVE"
        tail -500 /root/.pm2/logs/video-compressor-out.log 2>/dev/null | \
            grep -E "Calculating final video VMAF|Final VMAF:" | tail -2
    elif tail -500 /root/.pm2/logs/video-compressor-out.log 2>/dev/null | grep -q "Skipping full video VMAF"; then
        echo "   ❌ WARNING: VMAF calculation DISABLED (apply patch!)"
    else
        echo "   ⏳ No recent compression tasks"
    fi
    echo
fi

# Check for crash loops
echo "🔍 Crash Loop Detection:"
RESTARTS=$(pm2 list | grep video-compressor | awk '{print $8}' | tr -d '│')
if [ -n "$RESTARTS" ] && [ "$RESTARTS" -gt 10 ]; then
    echo "   ⚠️  WARNING: video-compressor has restarted ${RESTARTS} times!"
    echo "   Check logs: pm2 logs video-compressor"
else
    echo "   ✅ No crash loops detected"
fi
echo

# Wallet balance
echo "💰 Wallet Balance:"
btcli wallet balance --wallet.name "$WALLET_NAME" --subtensor.network finney 2>/dev/null || \
    echo "   (Unable to check balance)"
echo

echo "=================================="
echo "Monitoring complete. Run again to refresh."
echo
