---
name: manifold
description: "Search, analyze, and trade on Manifold Markets prediction markets. Use when the user wants to look up prediction market odds, place bets, check their portfolio, or discuss Manifold markets."
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires": { "bins": ["python3"], "env": ["MANIFOLD_API_KEY"] },
        "primaryEnv": "MANIFOLD_API_KEY",
      },
  }
---

# Manifold Markets

Trade on prediction markets via the Manifold API. All commands output JSON.

**Script path:** `{baseDir}/scripts/manifold.py`

Run with: `python3 {baseDir}/scripts/manifold.py <command> [options]`

## Check Balance

```bash
python3 {baseDir}/scripts/manifold.py balance
```

## Search Markets

```bash
# Search by keyword
python3 {baseDir}/scripts/manifold.py search "US election"

# Open binary markets, sorted by popularity
python3 {baseDir}/scripts/manifold.py search "AI" --filter open --sort most-popular --limit 5

# Closing soon
python3 {baseDir}/scripts/manifold.py search "" --filter closing-week --sort close-date
```

Filters: `all`, `open`, `closed`, `resolved`, `closing-day`, `closing-week`, `closing-month`

Sorts: `most-popular`, `newest`, `score`, `daily-score`, `24-hour-vol`, `liquidity`, `close-date`, `prob-descending`, `prob-ascending`

## Get Market Details & Probability

```bash
# By ID
python3 {baseDir}/scripts/manifold.py market <market-id>

# By slug (from URL)
python3 {baseDir}/scripts/manifold.py market some-market-slug

# Just the probability
python3 {baseDir}/scripts/manifold.py prob <market-id>
```

## Place Bets

```bash
# Market order: bet 100 mana on YES
python3 {baseDir}/scripts/manifold.py bet <contract-id> 100 YES

# Limit order at 40% probability
python3 {baseDir}/scripts/manifold.py bet <contract-id> 100 YES --limit-prob 0.40

# Dry run (simulate without executing)
python3 {baseDir}/scripts/manifold.py bet <contract-id> 100 YES --dry-run

# Bet on a specific answer in a multiple-choice market
python3 {baseDir}/scripts/manifold.py bet <contract-id> 50 YES --answer-id <answer-id>

# Limit order that expires in 1 hour
python3 {baseDir}/scripts/manifold.py bet <contract-id> 100 YES --limit-prob 0.35 --expires-ms 3600000
```

## Sell Shares

```bash
# Sell all shares in a market
python3 {baseDir}/scripts/manifold.py sell <contract-id>

# Sell specific outcome
python3 {baseDir}/scripts/manifold.py sell <contract-id> --outcome YES

# Sell partial shares
python3 {baseDir}/scripts/manifold.py sell <contract-id> --outcome NO --shares 50

# Sell in multiple-choice market
python3 {baseDir}/scripts/manifold.py sell <contract-id> --answer-id <answer-id>
```

## Cancel Limit Order

```bash
python3 {baseDir}/scripts/manifold.py cancel <bet-id>
```

## Portfolio & Positions

```bash
# Your portfolio summary
python3 {baseDir}/scripts/manifold.py portfolio

# Your current positions with contract details
python3 {baseDir}/scripts/manifold.py my-positions --limit 10 --order profit

# Positions/leaderboard for a specific market
python3 {baseDir}/scripts/manifold.py positions <contract-id> --top 10

# Your position in a specific market
python3 {baseDir}/scripts/manifold.py positions <contract-id> --user-id <your-user-id>
```

## Bet History

```bash
# Your recent bets
python3 {baseDir}/scripts/manifold.py bets --username <your-username>

# Bets on a specific market
python3 {baseDir}/scripts/manifold.py bets --contract-id <contract-id>

# Open limit orders only
python3 {baseDir}/scripts/manifold.py bets --username <your-username> --kinds open-limit
```

## Your Profile

```bash
python3 {baseDir}/scripts/manifold.py me
```

## Notes

- All monetary amounts are in **mana** (M$). New accounts start with M$1,000.
- Limit orders use probabilities from 0.01 to 0.99 (two decimal places).
- **Always use `--dry-run` first** when the user asks to place a bet, so they can confirm the expected outcome before committing real mana.
- The `search` results include `id` fields — use these as `contract-id` for betting/selling.
- For multiple-choice markets, fetch market details first to see available `answers` and their IDs.
- API rate limit: 500 requests/minute.
