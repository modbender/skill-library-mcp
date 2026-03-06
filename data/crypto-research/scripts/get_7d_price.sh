#!/bin/bash
# 获取7天价格数据

SYMBOL=$1
if [ -z "$SYMBOL" ]; then
    SYMBOL="BTCUSDT"
fi

echo "=== $SYMBOL 7天数据 ==="
curl -s "https://api.binance.com/api/v3/klines?symbol=$SYMBOL&interval=1d&limit=8" | python3 -c "
import sys, json
data = json.load(sys.stdin)
prices = [float(k[4]) for k in data]
if len(prices) >= 7:
    today = prices[0]
    d1 = prices[1]
    d7 = prices[6]
    print(f'今日: \${today:.2f}')
    print(f'昨日: \${d1:.2f}')
    print(f'7日前: \${d7:.2f}')
    print(f'7d涨跌: {((today-d7)/d7*100):.2f}%')
"
