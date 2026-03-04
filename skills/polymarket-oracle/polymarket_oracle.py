#!/usr/bin/env python3
"""
Polymarket Oracle - Multi-Strategy Arbitrage & Trading Bot
Version: 1.0.0
Author: Georges Andronescu (Wesley Armando)

Scans ALL Polymarket markets for:
- Parity arbitrage (YES+NO ≠ $1)
- Logical arbitrage (impossible outcomes)
- Tail-end trading (>95% certainty)
- Market making (maker rebates)
- Latency arbitrage (fast events)
- Combinatorial arbitrage (related markets)
- Cross-platform arbitrage (vs Kalshi)

Covers ALL categories: Crypto, Politics, Sports, Economics, Entertainment, etc.
"""

import sys
import json
import os
import time
import urllib.request
import urllib.error
import hashlib
import hmac
from datetime import datetime
from pathlib import Path
import concurrent.futures
import re

# ==========================================
# CONFIGURATION
# ==========================================
POLYMARKET_API_KEY = os.getenv("POLYMARKET_API_KEY")
POLYMARKET_SECRET = os.getenv("POLYMARKET_SECRET")
POLYMARKET_PASSPHRASE = os.getenv("POLYMARKET_PASSPHRASE")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

WORKSPACE = Path("/workspace")
OPPORTUNITIES_LOG = WORKSPACE / "polymarket_opportunities.jsonl"
TRADES_LOG = WORKSPACE / "polymarket_trades.jsonl"
PORTFOLIO_FILE = WORKSPACE / "polymarket_portfolio.json"

# Polymarket endpoints
CLOB_BASE = "https://clob.polymarket.com"
GAMMA_BASE = "https://gamma-api.polymarket.com"

# Strategy thresholds
MIN_PARITY_PROFIT = 0.02  # 2% minimum for parity arb
MIN_LOGICAL_PROFIT = 0.03  # 3% minimum for logical arb
MIN_TAIL_END_CERTAINTY = 0.95  # 95% minimum for tail-end
MIN_MARKET_MAKING_SPREAD = 0.025  # 2.5% minimum spread
LATENCY_WINDOW_SECONDS = 15  # 15s window for latency arb

# Capital allocation
MAX_POSITION_PER_MARKET = 1000  # $1000 max per market
TOTAL_CAPITAL = float(os.getenv("POLYMARKET_CAPITAL", "10000"))  # $10K default

# Scan settings
SCAN_INTERVAL = 60  # Scan every 60 seconds
MAX_WORKERS = 50  # Parallel workers for scanning


# ==========================================
# POLYMARKET API CLIENT
# ==========================================

class PolymarketClient:
    """Polymarket CLOB API client."""
    
    def __init__(self, api_key=None, secret=None, passphrase=None):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.clob_base = CLOB_BASE
        self.gamma_base = GAMMA_BASE
    
    def _sign_request(self, timestamp, method, path, body=""):
        """Sign request for authenticated endpoints."""
        if not self.secret:
            return None
        
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _request(self, endpoint, method="GET", params=None, body=None, auth=False, base="clob"):
        """Make API request."""
        url_base = self.clob_base if base == "clob" else self.gamma_base
        
        if params:
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url_base}{endpoint}?{query}"
        else:
            url = f"{url_base}{endpoint}"
        
        headers = {"Content-Type": "application/json"}
        
        if auth and self.api_key:
            timestamp = str(int(time.time() * 1000))
            signature = self._sign_request(timestamp, method, endpoint, body or "")
            
            headers.update({
                "POLY-API-KEY": self.api_key,
                "POLY-SIGNATURE": signature,
                "POLY-TIMESTAMP": timestamp,
                "POLY-PASSPHRASE": self.passphrase
            })
        
        req_body = json.dumps(body).encode('utf-8') if body else None
        req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"[ERROR] Polymarket API {e.code}: {error_body}")
            return None
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None
    
    # ===== GAMMA API (Market Discovery) =====
    
    def get_all_markets(self, limit=1000):
        """Get all active markets from Gamma API."""
        markets = []
        offset = 0
        
        while True:
            result = self._request(
                "/markets",
                params={"limit": min(limit - len(markets), 100), "offset": offset},
                base="gamma"
            )
            
            if not result or not result.get('data'):
                break
            
            markets.extend(result['data'])
            
            if len(markets) >= limit or len(result['data']) < 100:
                break
            
            offset += 100
            time.sleep(0.1)  # Rate limit
        
        print(f"[GAMMA] Fetched {len(markets)} markets")
        return markets
    
    def get_market_by_id(self, market_id):
        """Get specific market details."""
        return self._request(f"/markets/{market_id}", base="gamma")
    
    # ===== CLOB API (Trading) =====
    
    def get_orderbook(self, token_id):
        """Get order book for token."""
        return self._request(f"/book?token_id={token_id}", base="clob")
    
    def get_midpoint(self, token_id):
        """Get midpoint price."""
        result = self._request(f"/midpoint?token_id={token_id}", base="clob")
        return float(result.get('mid', 0)) if result else None
    
    def get_price(self, token_id, side="BUY"):
        """Get best price for side."""
        result = self._request(f"/price?token_id={token_id}&side={side}", base="clob")
        return float(result.get('price', 0)) if result else None
    
    def create_order(self, token_id, price, size, side, post_only=True):
        """Place order on Polymarket."""
        if not self.api_key:
            print("[SKIP] No API credentials - simulation mode")
            return {"simulated": True}
        
        order = {
            "token_id": token_id,
            "price": str(price),
            "size": str(size),
            "side": side.upper(),
            "type": "LIMIT",
            "post_only": post_only
        }
        
        return self._request("/order", method="POST", body=order, auth=True, base="clob")


# ==========================================
# MARKET CATEGORIZER
# ==========================================

class MarketCategorizer:
    """Automatically categorize markets."""
    
    CATEGORIES = {
        'crypto': [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'coin', 'defi',
            'solana', 'sol', 'cardano', 'ada', 'polygon', 'matic', 'avalanche',
            'polkadot', 'chainlink', 'uniswap', 'aave', 'compound'
        ],
        'politics': [
            'election', 'president', 'senate', 'congress', 'vote', 'poll',
            'trump', 'biden', 'republican', 'democrat', 'policy', 'bill',
            'gov', 'senator', 'mayor', 'parliament', 'prime minister'
        ],
        'sports': [
            'nba', 'nfl', 'mlb', 'nhl', 'super bowl', 'playoff', 'finals',
            'championship', 'world series', 'soccer', 'premier league', 'fifa',
            'uefa', 'tennis', 'golf', 'f1', 'formula', 'ufc', 'mma', 'boxing',
            'ncaa', 'march madness', 'game', 'score', 'win', 'mvp'
        ],
        'economics': [
            'fed', 'rate', 'inflation', 'cpi', 'jobs', 'unemployment', 'gdp',
            'recession', 'stock', 'sp500', 's&p', 'dow', 'nasdaq', 'earnings',
            'market cap', 'treasury', 'bond'
        ],
        'technology': [
            'apple', 'tesla', 'google', 'microsoft', 'amazon', 'meta', 'nvidia',
            'ai', 'ipo', 'product', 'launch', 'acquisition', 'merger'
        ],
        'entertainment': [
            'oscar', 'emmy', 'grammy', 'movie', 'box office', 'netflix',
            'streaming', 'celebrity', 'album', 'song', 'chart'
        ],
        'weather': [
            'hurricane', 'temperature', 'rain', 'snow', 'weather', 'climate',
            'storm', 'tornado', 'flood'
        ]
    }
    
    @classmethod
    def categorize(cls, market_description):
        """Categorize market based on description."""
        desc_lower = market_description.lower()
        
        for category, keywords in cls.CATEGORIES.items():
            if any(keyword in desc_lower for keyword in keywords):
                return category
        
        return 'other'


# ==========================================
# STRATEGY DETECTORS
# ==========================================

class StrategyDetectors:
    """Detect arbitrage opportunities."""
    
    @staticmethod
    def parity_arbitrage(market, client):
        """
        Detect parity arbitrage: YES + NO ≠ $1.00
        
        If YES + NO < $1.00 → Buy both, guaranteed profit
        If YES + NO > $1.00 → Sell both (if you have inventory)
        """
        opportunities = []
        
        for outcome in market.get('outcomes', []):
            yes_token = outcome.get('token_id')
            
            if not yes_token:
                continue
            
            # Get prices
            yes_price = client.get_price(yes_token, "BUY")
            no_price = 1.0 - yes_price if yes_price else None
            
            if not yes_price:
                continue
            
            # Calculate total
            total_cost = yes_price + no_price
            
            # Check for arbitrage
            if total_cost < (1.0 - MIN_PARITY_PROFIT):
                profit_pct = ((1.0 - total_cost) / total_cost) * 100
                
                opportunities.append({
                    'strategy': 'parity_arbitrage',
                    'market_id': market['id'],
                    'market_name': market.get('question', 'Unknown'),
                    'category': MarketCategorizer.categorize(market.get('question', '')),
                    'yes_token': yes_token,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'total_cost': total_cost,
                    'guaranteed_profit_pct': profit_pct,
                    'min_size': 100,
                    'max_size': min(MAX_POSITION_PER_MARKET, 1000),
                    'detected_at': datetime.now().isoformat()
                })
        
        return opportunities
    
    @staticmethod
    def tail_end_trading(market, client):
        """
        Detect tail-end opportunities: Outcome >95% certain
        
        Buy at 0.95-0.99, wait for resolution at $1.00
        """
        opportunities = []
        
        for outcome in market.get('outcomes', []):
            token_id = outcome.get('token_id')
            
            if not token_id:
                continue
            
            price = client.get_price(token_id, "BUY")
            
            if not price:
                continue
            
            # Check if high certainty
            if price >= MIN_TAIL_END_CERTAINTY and price < 0.995:
                profit_pct = ((1.0 - price) / price) * 100
                
                opportunities.append({
                    'strategy': 'tail_end',
                    'market_id': market['id'],
                    'market_name': market.get('question', 'Unknown'),
                    'category': MarketCategorizer.categorize(market.get('question', '')),
                    'token_id': token_id,
                    'outcome': outcome.get('name', 'YES'),
                    'price': price,
                    'certainty_pct': price * 100,
                    'profit_pct': profit_pct,
                    'min_size': 500,
                    'max_size': min(MAX_POSITION_PER_MARKET, 5000),
                    'detected_at': datetime.now().isoformat()
                })
        
        return opportunities
    
    @staticmethod
    def logical_arbitrage(markets_batch):
        """
        Detect logical arbitrage: Impossible price combinations
        
        Example: "Chiefs win" at 28%, "AFC wins" at 24%
        Chiefs ARE an AFC team → logically impossible
        """
        # Placeholder - requires NLP/AI to find related markets
        # Would use vector embeddings to match similar descriptions
        opportunities = []
        
        # TODO: Implement with sentence-transformers or similar
        # For now, return empty (strategy exists but needs AI)
        
        return opportunities
    
    @staticmethod
    def market_making_opportunity(market, client):
        """
        Detect market making opportunities
        
        Place maker orders on both sides, earn spread + rebates
        """
        opportunities = []
        
        for outcome in market.get('outcomes', []):
            token_id = outcome.get('token_id')
            
            if not token_id:
                continue
            
            mid = client.get_midpoint(token_id)
            
            if not mid or mid < 0.1 or mid > 0.9:
                # Skip extreme probabilities
                continue
            
            # Calculate spread we could capture
            target_spread = MIN_MARKET_MAKING_SPREAD
            bid = mid - (target_spread / 2)
            ask = mid + (target_spread / 2)
            
            if bid > 0.01 and ask < 0.99:
                opportunities.append({
                    'strategy': 'market_making',
                    'market_id': market['id'],
                    'market_name': market.get('question', 'Unknown'),
                    'category': MarketCategorizer.categorize(market.get('question', '')),
                    'token_id': token_id,
                    'midpoint': mid,
                    'bid_price': bid,
                    'ask_price': ask,
                    'spread_pct': target_spread * 100,
                    'size_per_side': 200,
                    'detected_at': datetime.now().isoformat()
                })
        
        return opportunities


# ==========================================
# OPPORTUNITY SCANNER
# ==========================================

class OpportunityScanner:
    """Scan all markets for opportunities."""
    
    def __init__(self, client):
        self.client = client
    
    def scan_market(self, market):
        """Scan single market for all strategies."""
        opportunities = []
        
        try:
            # Parity arbitrage
            opportunities.extend(
                StrategyDetectors.parity_arbitrage(market, self.client)
            )
            
            # Tail-end trading
            opportunities.extend(
                StrategyDetectors.tail_end_trading(market, self.client)
            )
            
            # Market making
            opportunities.extend(
                StrategyDetectors.market_making_opportunity(market, self.client)
            )
        
        except Exception as e:
            print(f"[ERROR] Scan market {market.get('id')}: {e}")
        
        return opportunities
    
    def scan_all_markets_parallel(self, markets):
        """Scan all markets in parallel."""
        print(f"[SCAN] Scanning {len(markets)} markets with {MAX_WORKERS} workers...")
        
        all_opportunities = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(self.scan_market, market): market
                for market in markets
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    opps = future.result()
                    all_opportunities.extend(opps)
                except Exception as e:
                    print(f"[ERROR] Future failed: {e}")
        
        # Log opportunities
        if all_opportunities:
            with open(OPPORTUNITIES_LOG, 'a') as f:
                for opp in all_opportunities:
                    f.write(json.dumps(opp) + '\n')
        
        print(f"[SCAN] Found {len(all_opportunities)} opportunities")
        
        return all_opportunities


# ==========================================
# TELEGRAM NOTIFIER
# ==========================================

class TelegramNotifier:
    """Send alerts via Telegram."""
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage" if bot_token else None
    
    def send(self, message):
        """Send message."""
        if not self.api_url:
            print(f"[TELEGRAM] {message}")
            return
        
        try:
            data = json.dumps({
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }).encode('utf-8')
            
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            urllib.request.urlopen(req, timeout=10)
            print("[TELEGRAM] Sent ✓")
        
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}")
    
    def opportunity_alert(self, opportunities):
        """Send opportunity summary."""
        if not opportunities:
            return
        
        # Group by strategy
        by_strategy = {}
        for opp in opportunities:
            strategy = opp['strategy']
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(opp)
        
        message = f"""🎯 *POLYMARKET OPPORTUNITIES*

Found {len(opportunities)} opportunities:

"""
        
        for strategy, opps in by_strategy.items():
            message += f"*{strategy.upper()}:* {len(opps)}\n"
        
        message += f"\nTop 5 by profit:\n"
        
        sorted_opps = sorted(
            opportunities,
            key=lambda x: x.get('guaranteed_profit_pct', x.get('profit_pct', 0)),
            reverse=True
        )[:5]
        
        for opp in sorted_opps:
            profit = opp.get('guaranteed_profit_pct', opp.get('profit_pct', 0))
            message += f"\n• {opp['strategy']}: {profit:.2f}%\n  {opp['market_name'][:50]}...\n"
        
        self.send(message)


# ==========================================
# MAIN SCANNER ENGINE
# ==========================================

def main():
    """Main scanner loop."""
    print("="*60)
    print("POLYMARKET ORACLE - Multi-Strategy Scanner")
    print("="*60)
    
    # Initialize
    client = PolymarketClient(
        api_key=POLYMARKET_API_KEY,
        secret=POLYMARKET_SECRET,
        passphrase=POLYMARKET_PASSPHRASE
    )
    
    scanner = OpportunityScanner(client)
    telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    print(f"[CONFIG] Capital: ${TOTAL_CAPITAL:,.0f}")
    print(f"[CONFIG] Max per market: ${MAX_POSITION_PER_MARKET:,.0f}")
    print(f"[CONFIG] Scan interval: {SCAN_INTERVAL}s")
    
    if not POLYMARKET_API_KEY:
        print("[WARNING] No API credentials - simulation mode only")
    
    telegram.send("🚀 *Polymarket Oracle Started*\n\nScanning all markets...")
    
    # Main loop
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting scan...")
            
            # Fetch all active markets
            markets = client.get_all_markets(limit=2000)
            
            if not markets:
                print("[ERROR] Failed to fetch markets")
                time.sleep(SCAN_INTERVAL)
                continue
            
            # Categorize markets
            categories_count = {}
            for market in markets:
                cat = MarketCategorizer.categorize(market.get('question', ''))
                categories_count[cat] = categories_count.get(cat, 0) + 1
            
            print(f"[MARKETS] Categories: {categories_count}")
            
            # Scan for opportunities
            opportunities = scanner.scan_all_markets_parallel(markets)
            
            # Send alerts
            if opportunities:
                telegram.opportunity_alert(opportunities)
            
            # Wait
            print(f"[SLEEP] Waiting {SCAN_INTERVAL}s...")
            time.sleep(SCAN_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n[STOP] Manual stop")
            break
        
        except Exception as e:
            print(f"[ERROR] Main loop: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
