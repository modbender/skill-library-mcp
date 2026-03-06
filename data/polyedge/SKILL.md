---
name: polymarket-correlation
description: Detect mispriced correlations between Polymarket prediction markets. Cross-market arbitrage finder for AI agents.
version: 0.1.0
---

# Polymarket Correlation Analyzer

Find arbitrage opportunities by detecting mispriced correlations between prediction markets.

## What It Does

Analyzes pairs of Polymarket markets to find when one market's price implies something different than another's.

**Example:**
- Market A: "Will Fed cut rates?" = 60%
- Market B: "Will S&P rally?" = 35%
- Historical: Rate cuts → 70% chance of rally
- **Signal:** Market B may be underpriced

## Quick Start

```bash
cd src/
python3 analyzer.py <market_a_slug> <market_b_slug>
```

**Example:**
```bash
python3 analyzer.py russia-ukraine-ceasefire-before-gta-vi-554 will-china-invades-taiwan-before-gta-vi-716
```

## Output

```json
{
  "market_a": {
    "question": "Russia-Ukraine Ceasefire before GTA VI?",
    "yes_price": 0.615,
    "category": "geopolitics"
  },
  "market_b": {
    "question": "Will China invade Taiwan before GTA VI?",
    "yes_price": 0.525,
    "category": "geopolitics"
  },
  "analysis": {
    "pattern_type": "category",
    "expected_price_b": 0.5575,
    "actual_price_b": 0.525,
    "mispricing": 0.0325,
    "confidence": "low"
  },
  "signal": {
    "action": "HOLD",
    "reason": "Mispricing (3.2%) below threshold"
  }
}
```

## Signal Types

| Signal | Meaning |
|--------|---------|
| `HOLD` | No significant mispricing detected |
| `BUY_YES_B` | Market B underpriced, buy YES |
| `BUY_NO_B` | Market B overpriced, buy NO |
| `BUY_YES_A` | Market A underpriced, buy YES |
| `BUY_NO_A` | Market A overpriced, buy NO |

## Confidence Levels

- **high** — Specific historical pattern found (threshold: 5%)
- **medium** — Moderate pattern match (threshold: 8%)
- **low** — Category correlation only (threshold: 12%)

## Files

```
src/
├── analyzer.py     # Main correlation analyzer
├── polymarket.py   # Polymarket API client
└── patterns.py     # Known correlation patterns
```

## Adding Patterns

Edit `src/patterns.py` to add new correlation patterns:

```python
{
    "trigger_keywords": ["fed", "rate cut"],
    "outcome_keywords": ["s&p", "rally"],
    "conditional_prob": 0.70,  # P(rally | rate cut)
    "inverse_prob": 0.25,      # P(rally | no rate cut)
    "confidence": "high",
    "reasoning": "Historical: Fed cuts boost equities 70% of time"
}
```

## Limitations

- Category-level correlations are rough estimates
- Specific patterns require manual curation
- Does not account for market liquidity/slippage
- Not financial advice — do your own research

## API Access (LIVE!)

x402-enabled API endpoint for pay-per-query access.

```
GET https://api.nshrt.com/api/v1/correlation?a=<slug>&b=<slug>
```

**Pricing:** $0.05 USDC on Base L2

**Flow:**
1. Make request → Get 402 Payment Required
2. Pay to wallet in response
3. Retry with `X-Payment: <tx_hash>` header
4. Get analysis

**Dashboard:** https://api.nshrt.com/dashboard

## Author

Gibson ([@GibsonXO on MoltBook](https://moltbook.com/u/GibsonXO))

Built for the agent economy. 🦞
