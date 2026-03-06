#!/bin/bash
# Calculate monthly DCA amounts based on budget
BUDGET=${1:-500}  # Default €500/month

echo "💰 Monthly DCA Plan"
echo "==================="
echo "Budget: €$BUDGET"
echo ""
echo "Allocation:"
echo "├── VWCE (70%):     €$((BUDGET * 70 / 100))"
echo "├── EIMI/IXUS (10%): €$((BUDGET * 10 / 100))"
echo "├── BTC (10%):      €$((BUDGET * 10 / 100))"
echo "└── Cash buffer (10%): €$((BUDGET * 10 / 100))"
echo ""
echo "Where to execute:"
echo "- ETFs: Interactive Brokers (IBKR)"
echo "- Crypto: Bitstamp or Kraken"
echo "- Cash: High-yield savings (Revolut/Swedbank)"
echo ""
echo "Remember:"
echo "- Check if any position drifted >5% from target"
echo "- Rebalance by directing new money, not selling"
echo "- Update your tracking spreadsheet"
