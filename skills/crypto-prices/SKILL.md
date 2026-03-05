# Skill: crypto-prices

## Purpose
Fetch live cryptocurrency and commodity prices using the local `crypto_prices.py` module. This is your **single source of truth** for all price data — never use web search for prices.

## When to Use
- Boss Man asks "what's BTC at?" or "price of gold" or any price query
- You need current prices for market analysis, morning protocol, or any report
- Anytime you're about to quote a price in conversation

## How to Execute

### Single Price Lookup
```bash
cd ~/clawd && python3 -c "
from crypto_prices import fetch_live_price, format_price_text
data = fetch_live_price('COIN_NAME')
if data:
    print(format_price_text(data))
    # Full details available in data dict:
    # data['price'], data['change_24h'], data['change_7d'], data['change_30d']
    # data['market_cap'], data['volume_24h'], data['high_24h'], data['low_24h']
    # data['ath'], data['ath_change_pct'], data['source']
else:
    print('Price unavailable — all providers failed')
"
```

### Multiple Price Lookup (Batch)
```bash
cd ~/clawd && python3 -c "
from crypto_prices import fetch_multiple_prices, format_prices_block
prices = fetch_multiple_prices(['bitcoin', 'ethereum', 'xrp', 'sui', 'gold', 'silver'])
print(format_prices_block(prices))
"
```

### Quick Price (Minimal Output)
```bash
cd ~/clawd && python3 -c "
from crypto_prices import fetch_live_price
d = fetch_live_price('COIN_NAME')
if d: print(f\"{d['symbol']}: \${d['price']:,.6g} ({d['change_24h']:+.2f}%)\")
"
```

## Supported Assets
| Input | Resolves To | Source |
|-------|-------------|--------|
| btc, bitcoin | bitcoin | CoinGecko |
| eth, ethereum | ethereum | DexScreener → CoinGecko |
| xrp, ripple | ripple | DexScreener → CoinGecko |
| sui | sui | CoinGecko |
| sol, solana | solana | CoinGecko |
| gold, xau | gold | Yahoo Finance → CoinGecko |
| silver, xag | silver | Yahoo Finance → CoinGecko |
| doge, ada, dot, avax, link, matic | various | CoinGecko |

## Provider Chain
1. **Cache** (60s TTL) — serves instantly if fresh
2. **Yahoo Finance** — metals only (gold/silver), most reliable for commodities
3. **CoinGecko full** — comprehensive data (price, 24h/7d/30d change, ATH/ATL, market cap)
4. **CoinGecko simple** — lighter endpoint if full is rate-limited
5. **DexScreener** — DEX-based failover for crypto (ETH and XRP try this first)

## Rules
- **NEVER** use Brave Search for prices — it returns stale article snippets, not live data
- **NEVER** guess or hallucinate prices — if all providers fail, say "price unavailable"
- Cache is 60 seconds — calling twice within a minute is free
- Rate limits: CoinGecko ~10 req/min, DexScreener ~60 req/min
- For batch queries, the module handles delays automatically
