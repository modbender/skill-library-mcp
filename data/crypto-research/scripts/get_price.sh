#!/bin/bash
# 获取BTC/ETH价格数据

echo "=== BTC价格 ==="
curl -s "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"价格: \${d['lastPrice']}\")
print(f\"24h涨跌: {d['priceChangePercent']}%\")
"

echo ""
echo "=== ETH价格 ==="
curl -s "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"价格: \${d['lastPrice']}\")
print(f\"24h涨跌: {d['priceChangePercent']}%\")
"

echo ""
echo "=== 资金费率 ==="
echo "BTC:"
curl -s "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"资金费率: {float(d['lastFundingRate'])*100:.4f}%\")
"
echo "ETH:"
curl -s "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=ETHUSDT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"资金费率: {float(d['lastFundingRate'])*100:.4f}%\")
"
