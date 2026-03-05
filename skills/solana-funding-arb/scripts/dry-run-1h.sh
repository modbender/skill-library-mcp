#!/bin/bash
# 1 hour dry run test - checks every 5 minutes

cd ~/clawd/skills/solana-funding-arb/scripts
LOG_FILE="/tmp/funding-arb-dry-$(date +%Y%m%d-%H%M%S).log"

echo "🚀 Funding Arb Dry Run Started" | tee $LOG_FILE
echo "📊 Config: $1000 max position, Ultra Safe (1x)" | tee -a $LOG_FILE
echo "⏱️ Duration: 1 hour (12 checks @ 5 min intervals)" | tee -a $LOG_FILE
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a $LOG_FILE

for i in {1..12}; do
    echo "" | tee -a $LOG_FILE
    echo "📡 Check #$i - $(date +%H:%M:%S)" | tee -a $LOG_FILE
    DRY_RUN=true npx ts-node --transpile-only src/trading/auto-trader.ts 2>&1 | tee -a $LOG_FILE
    
    if [ $i -lt 12 ]; then
        echo "⏳ Next check in 5 minutes..." | tee -a $LOG_FILE
        sleep 300
    fi
done

echo "" | tee -a $LOG_FILE
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a $LOG_FILE
echo "✅ 1 Hour Dry Run Complete!" | tee -a $LOG_FILE
echo "📝 Log: $LOG_FILE" | tee -a $LOG_FILE
