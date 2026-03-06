#!/usr/bin/env python3
"""
全球情报汇总 - 实时数据获取脚本
用于获取各市场实时数据，支持多源验证
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# ============= 配置 =============
CONFIG = {
    "crypto": {
        "coingecko": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
    },
    "stock": {
        "yahoo_nasdaq": "https://query1.finance.yahoo.com/v8/finance/chart/^IXIC",
        "yahoo_dow": "https://query1.finance.yahoo.com/v8/finance/chart/^DJI"
    }
}

# ============= 数据获取 =============
async def fetch_crypto():
    """获取加密货币实时数据"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CONFIG["crypto"]["coingecko"], timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                return {
                    "source": "CoinGecko API",
                    "timestamp": datetime.now().isoformat(),
                    "btc": {"price": data["bitcoin"]["usd"], "change_24h": data["bitcoin"]["usd_24h_change"]},
                    "eth": {"price": data["ethereum"]["usd"], "change_24h": data["ethereum"]["usd_24h_change"]}
                }
    except Exception as e:
        return {"error": str(e)}

async def fetch_stock_data():
    """获取美股数据"""
    try:
        async with aiohttp.ClientSession() as session:
            # 获取纳斯达克
            async with session.get(CONFIG["stock"]["yahoo_nasdaq"], timeout=aiohttp.ClientTimeout(total=10)) as resp:
                nasdaq_data = await resp.json()
            
            # 获取道琼斯
            async with session.get(CONFIG["stock"]["yahoo_dow"], timeout=aiohttp.ClientTimeout(total=10)) as resp:
                dow_data = await resp.json()
            
            return {
                "source": "Yahoo Finance API",
                "timestamp": datetime.now().isoformat(),
                "nasdaq": nasdaq_data,
                "dow": dow_data
            }
    except Exception as e:
        return {"error": str(e)}

# ============= 主函数 =============
async def main():
    print("🔄 正在获取实时数据...")
    
    crypto_data = await fetch_crypto()
    stock_data = await fetch_stock_data()
    
    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crypto": crypto_data,
        "stock": stock_data
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

if __name__ == "__main__":
    asyncio.run(main())
