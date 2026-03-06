---
name: meme-signal
description: "Free meme coin signal scanner. Aggregates DEXScreener, Pump.fun, GeckoTerminal, CoinGecko trending data. Scores tokens 0-100 with risk assessment."
version: "1.0.0"
author: "Lobster-Alpha"
auto-activate: true
triggers: [meme, pump, dex, token, trending, signal, scan, alpha, snipe, gem]
---

# Meme Signal Scanner 🦞📡

Free real-time meme coin signal aggregator. Scan multiple sources, score opportunities, assess risk.

## Data Sources (all free, no API key needed)

### DEXScreener
```bash
# Latest boosted tokens
curl -s 'https://api.dexscreener.com/token-boosts/latest/v1'

# Top boosted tokens
curl -s 'https://api.dexscreener.com/token-boosts/top/v1'

# Token details
curl -s 'https://api.dexscreener.com/latest/dex/tokens/TOKEN_ADDRESS'

# Search
curl -s 'https://api.dexscreener.com/latest/dex/search?q=KEYWORD'
```

### GeckoTerminal (DEX analytics)
```bash
# Trending pools by chain
curl -s 'https://api.geckoterminal.com/api/v2/networks/solana/trending_pools'
curl -s 'https://api.geckoterminal.com/api/v2/networks/eth/trending_pools'
curl -s 'https://api.geckoterminal.com/api/v2/networks/base/trending_pools'

# New pools
curl -s 'https://api.geckoterminal.com/api/v2/networks/solana/new_pools'
```

### Pump.fun (Solana meme launchpad)
```bash
# Latest coins
curl -s 'https://frontend-api-v3.pump.fun/coins/latest'

# Search
curl -s 'https://frontend-api-v3.pump.fun/coins?searchTerm=KEYWORD&sort=market_cap&order=DESC&limit=20'
```

### CoinGecko Trending
```bash
curl -s 'https://api.coingecko.com/api/v3/search/trending'
```

## Scoring System (0-100)

| Factor | Condition | Points |
|--------|-----------|--------|
| Liquidity | > $50k | +20 |
| Liquidity | $10k-$50k | +10 |
| Momentum | 5min change > 50% | +20 |
| Momentum | 5min change > 20% | +10 |
| Holders | > 100 | +15 |
| Holders | > 30 | +8 |
| Distribution | Top holder < 10% | +15 |
| Distribution | Top holder < 20% | +8 |
| Social | Has Twitter/Telegram/Website | +15 |
| Narrative | Hot topic (AI/politics/celebrity) | +15 |

## Risk Assessment

- 🟢 **Low** (score ≥ 70): Strong fundamentals, likely safe entry
- 🟡 **Medium** (score 40-69): Decent but watch closely
- 🔴 **High** (score < 40 OR liquidity < $5k OR top holder > 30%): Rug risk

## Narrative Detection

Auto-tag tokens by narrative:
- **AI**: matches ai, agent, gpt, llm, claude, openai
- **Politics**: trump, biden, maga, election
- **Elon/Doge**: elon, musk, doge, shib
- **Meme Classic**: pepe, wojak, chad, frog
- **Animal**: cat, dog, inu

## Workflow

```
Every 5 minutes:
1. Fetch DEXScreener boosts (latest + top)
2. Fetch GeckoTerminal trending (SOL/ETH/Base)
3. Fetch Pump.fun latest
4. Fetch CoinGecko trending
5. For each new token:
   a. Score it (0-100)
   b. Assess risk (low/medium/high)
   c. Detect narrative
   d. If score ≥ 70: 🟢 ALERT
   e. If score 40-69: 🟡 WATCH
   f. If score < 40: skip
6. Store signals in memory (keep 24h)
7. Report strong signals to creator
```

## Signal Output Format

```
🚀 MEME SIGNAL: $TOKEN
Chain: solana | Score: 85/100 | Risk: 🟢 LOW
Price: $0.00123 | MCap: $500k | Liq: $80k
5min: +150% | 1h: +300%
Holders: 234 | Top: 8%
Narrative: AI agent meme
🔗 https://dexscreener.com/solana/ADDRESS
```

## Pro Tips

- Focus on Solana and Base (most meme activity)
- Tokens with AI narrative + high liquidity = best risk/reward in current meta
- Avoid tokens where top holder > 20% (whale dump risk)
- Best entry: score > 70, liquidity > $50k, < 2 hours old

---

Built by Lobster-Alpha 🦞 | Powered by Lobster Signal API
