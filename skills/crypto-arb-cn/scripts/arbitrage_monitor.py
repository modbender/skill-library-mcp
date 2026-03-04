#!/usr/bin/env python3
"""
Cryptocurrency Arbitrage Monitor for Chinese-accessible Exchanges
Supports: Binance, OKX, Gate.io, Huobi

Usage:
    python arbitrage_monitor.py --once    # Single check
    python arbitrage_monitor.py           # Continuous monitoring
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# ============== Configuration ==============

# Trading pairs to monitor
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]

# Exchanges configuration
EXCHANGES = {
    "binance": {
        "name": "币安",
        "url": "https://api.binance.com/api/v3/ticker/price?symbol={}",
        "fee": 0.001,  # 0.1%
    },
    "okx": {
        "name": "OKX",
        "url": "https://www.okx.com/api/v5/market/ticker?instId={}",
        "fee": 0.0008,  # 0.08%
    },
    "gate": {
        "name": "Gate.io",
        "url": "https://api.gateio.ws/api/v4/spot/tickers?currency_pair={}",
        "fee": 0.002,  # 0.2%
    },
    "huobi": {
        "name": "火币",
        "url": "https://api.huobi.pro/market/detail/merged?symbol={}",
        "fee": 0.002,  # 0.2%
    },
}

# Minimum profit threshold (after fees)
MIN_PROFIT_PERCENT = 0.5

# Telegram notification (optional)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ============== Core Logic ==============

class ArbitrageMonitor:
    def __init__(self):
        self.prices: Dict[str, Dict[str, float]] = {}
        self.opportunities: List[dict] = []

    async def fetch_price(self, session: aiohttp.ClientSession, exchange: str, symbol: str) -> Optional[float]:
        """Fetch price from exchange"""
        config = EXCHANGES[exchange]
        
        try:
            # Format symbol for each exchange
            if exchange == "okx":
                formatted = symbol.replace("USDT", "-USDT")
            elif exchange == "huobi":
                formatted = symbol.replace("USDT", "usdt").lower()
            elif exchange == "gate":
                formatted = symbol.replace("USDT", "_USDT")
            else:
                formatted = symbol

            async with session.get(config["url"].format(formatted), timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

                # Parse response for each exchange
                if exchange == "binance":
                    return float(data.get("price", 0))
                elif exchange == "okx":
                    return float(data.get("data", [{}])[0].get("last", 0))
                elif exchange == "gate":
                    if isinstance(data, list) and len(data) > 0:
                        return float(data[0].get("last", 0))
                    return None
                elif exchange == "huobi":
                    tick = data.get("tick", {})
                    return float(tick.get("close", 0))
        except Exception as e:
            print(f"[ERROR] {exchange} {symbol}: {e}")
            return None

    async def update_prices(self):
        """Update all prices"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in SYMBOLS:
                for exchange in EXCHANGES:
                    tasks.append(self.fetch_price(session, exchange, symbol))

            results = await asyncio.gather(*tasks)

            idx = 0
            for symbol in SYMBOLS:
                self.prices[symbol] = {}
                for exchange in EXCHANGES:
                    price = results[idx]
                    if price and price > 0:
                        self.prices[symbol][exchange] = price
                    idx += 1

    def find_opportunities(self) -> List[dict]:
        """Find arbitrage opportunities"""
        opportunities = []

        for symbol in SYMBOLS:
            prices = self.prices.get(symbol, {})
            if len(prices) < 2:
                continue

            exchanges = list(prices.keys())
            for i, buy_ex in enumerate(exchanges):
                for sell_ex in exchanges[i+1:]:
                    buy_price = prices[buy_ex]
                    sell_price = prices[sell_ex]

                    # Calculate profit (after fees)
                    total_fee = EXCHANGES[buy_ex]["fee"] + EXCHANGES[sell_ex]["fee"]
                    
                    if buy_price < sell_price:
                        profit_percent = ((sell_price - buy_price) / buy_price - total_fee) * 100
                        direction = f"{EXCHANGES[buy_ex]['name']} → {EXCHANGES[sell_ex]['name']}"
                        buy_exchange = buy_ex
                        sell_exchange = sell_ex
                    else:
                        profit_percent = ((buy_price - sell_price) / sell_price - total_fee) * 100
                        direction = f"{EXCHANGES[sell_ex]['name']} → {EXCHANGES[buy_ex]['name']}"
                        buy_exchange = sell_ex
                        sell_exchange = buy_ex

                    if profit_percent >= MIN_PROFIT_PERCENT:
                        opportunities.append({
                            "symbol": symbol,
                            "direction": direction,
                            "buy_exchange": EXCHANGES[buy_exchange]["name"],
                            "sell_exchange": EXCHANGES[sell_exchange]["name"],
                            "buy_price": min(buy_price, sell_price),
                            "sell_price": max(buy_price, sell_price),
                            "profit_percent": round(profit_percent, 3),
                            "timestamp": datetime.now().isoformat(),
                        })

        opportunities.sort(key=lambda x: x["profit_percent"], reverse=True)
        return opportunities

    async def send_telegram(self, opp: dict):
        """Send notification to Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return

        message = f"""💰 发现套利机会！

交易对: {opp['symbol']}
方向: {opp['direction']}
利润: {opp['profit_percent']}%

买入: {opp['buy_price']:.2f} ({opp['buy_exchange']})
卖出: {opp['sell_price']:.2f} ({opp['sell_exchange']})

时间: {datetime.now().strftime('%H:%M:%S')}
"""
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                await session.post(url, json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message,
                })
        except Exception as e:
            print(f"[ERROR] Telegram: {e}")

    def print_prices(self):
        """Print current prices"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 价格更新:")
        for symbol, prices in self.prices.items():
            if prices:
                price_str = " | ".join([f"{EXCHANGES[ex]['name']}:{prices[ex]:.2f}" for ex in prices])
                print(f"  {symbol}: {price_str}")

    def print_opportunities(self, opportunities: List[dict]):
        """Print opportunities"""
        if opportunities:
            print(f"\n💰 发现 {len(opportunities)} 个套利机会:")
            for opp in opportunities[:5]:
                print(f"  {opp['symbol']} | {opp['direction']} | 利润: {opp['profit_percent']}%")
        else:
            print(f"  暂无套利机会（需要 > {MIN_PROFIT_PERCENT}% 利润）")

    async def run_once(self) -> List[dict]:
        """Single check"""
        await self.update_prices()
        self.print_prices()
        opportunities = self.find_opportunities()
        self.print_opportunities(opportunities)
        return opportunities

    async def run(self, interval: int = 30):
        """Continuous monitoring"""
        print(f"🔍 套利监控器启动")
        print(f"   交易对: {', '.join(SYMBOLS)}")
        print(f"   最小利润阈值: {MIN_PROFIT_PERCENT}%")
        print(f"   检查间隔: {interval}秒")
        if TELEGRAM_BOT_TOKEN:
            print(f"   Telegram 通知: ✅ 已启用")
        print("-" * 50)

        while True:
            try:
                opportunities = await self.run_once()
                
                # Send Telegram notifications
                for opp in opportunities[:3]:
                    await self.send_telegram(opp)

                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                print("\n监控停止")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                await asyncio.sleep(10)


def main():
    monitor = ArbitrageMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single check mode
        opportunities = asyncio.run(monitor.run_once())
        if opportunities:
            print("\n" + json.dumps(opportunities, ensure_ascii=False, indent=2))
    else:
        # Continuous monitoring mode
        asyncio.run(monitor.run())


if __name__ == "__main__":
    main()
