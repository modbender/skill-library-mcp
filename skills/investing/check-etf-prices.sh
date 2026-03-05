#!/bin/bash
# Check key ETF and crypto prices
echo "📈 Investment Prices - $(date '+%Y-%m-%d %H:%M')"
echo "============================================"

# VWCE - Vanguard FTSE All-World (main ETF)
VWCE=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/VWCE.DE" 2>/dev/null | jq -r '.chart.result[0].meta.regularMarketPrice // "N/A"')
echo "VWCE (All-World):  €$VWCE"

# Bitcoin
BTC=$(curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur" 2>/dev/null | jq -r '.bitcoin.eur // "N/A"')
echo "Bitcoin (BTC):     €$BTC"

# Ethereum
ETH=$(curl -s "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=eur" 2>/dev/null | jq -r '.ethereum.eur // "N/A"')
echo "Ethereum (ETH):    €$ETH"

echo ""
echo "📊 Quick Analysis:"
if [ "$VWCE" != "N/A" ]; then
  echo "- VWCE at €$VWCE - check 52-week range"
fi
if [ "$BTC" != "N/A" ]; then
  if (( $(echo "$BTC < 50000" | bc -l) )); then
    echo "- BTC under €50k - potential accumulation zone"
  elif (( $(echo "$BTC > 80000" | bc -l) )); then
    echo "- BTC over €80k - consider taking some profits"
  else
    echo "- BTC in normal range - continue DCA"
  fi
fi
