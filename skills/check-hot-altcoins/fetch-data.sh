#!/bin/bash
# 加密货币早报生成脚本
# 使用CoinGecko API获取数据

COIN_IDS="solana,binancecoin,ripple,cardano,dogecoin,chainlink,avalanche-2,polygon,polkadot,stellar,fetch-ai,render-token,ocean-protocol,uniswap,aave,near,aptos,pepe,optimism,ondo,kite-ai,world-liberty-financial"

echo "正在获取加密货币数据..."

# 获取数据
DATA=$(curl -s "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=$COIN_IDS&order=market_cap_desc&sparkline=false&price_change_percentage=24h")

echo "$DATA" > /tmp/coins.json

# 检查数据是否获取成功
if [ -s /tmp/coins.json ]; then
    echo "数据获取成功"
else
    echo "数据获取失败"
    exit 1
fi
