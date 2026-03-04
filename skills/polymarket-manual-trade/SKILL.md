---
name: polymarket-manual-trade
displayName: Manual Trade Placement
description: Place manual trades on Polymarket by telling your agent what to bet on. Supports FAK (instant fill at market) and GTC (limit order on the book). Pass a Simmer market ID or a full Polymarket URL — the skill auto-imports and handles price discovery. Both FAK and GTC order types are fully tested and working.
metadata:
  clawdbot:
    emoji: "🎯"
    requires:
      pip: ["simmer-sdk"]
      env: ["SIMMER_API_KEY", "WALLET_PRIVATE_KEY"]
    cron: null
    automaton:
      managed: false
      entrypoint: "manual_trade.py"
version: "1.0.4"
published: true
---

# Manual Trade Placement

Place trades on Polymarket by telling your AI agent what to bet on. Supports instant FAK fills and GTC limit orders. Works with Simmer market IDs or full Polymarket event URLs.

## Usage

Tell your agent:
> "Buy YES $10 on [Polymarket URL or market ID]"
> "Place a GTC limit NO $20 at 0.35 on [market]"

Or run directly:

```bash
# FAK — instant fill at best ask price (default)
python3 manual_trade.py --market <market_id_or_url> --side YES --amount 10

# GTC — limit order, sits on book until filled
python3 manual_trade.py --market <market_id_or_url> --side NO --amount 20 --order GTC --price 0.35

# Full Polymarket URL — auto-imports and trades
python3 manual_trade.py \
  --market https://polymarket.com/event/spacex-starship-flight-test-12/will-the-chopsticks-catch-spacex-starship-flight-test-12-superheavy-booster \
  --side YES --amount 10

# Dry run (preview without placing)
python3 manual_trade.py --market <id> --side YES --amount 10 --dry-run
```

## Order Types

| Type | Behavior | When to use |
|------|----------|-------------|
| **FAK** (default) | Fills immediately at best ask+0.01. Remainder cancelled. | You want in now at market price |
| **GTC** | Limit order sits on CLOB book. Funds locked on placement, fill when market reaches your price | You want a specific price |

## Arguments

| Flag | Description |
|------|-------------|
| `--market` / `-m` | Simmer market ID **or** full Polymarket URL |
| `--side` / `-s` | `YES` or `NO` |
| `--amount` / `-a` | Dollar amount (default $10) |
| `--order` / `-o` | `FAK`, `GTC`, or `FOK` (default FAK) |
| `--price` / `-p` | Limit price (optional — auto-fetches best ask+0.01 if omitted) |
| `--venue` / `-v` | `polymarket` or `sim` (default polymarket) |
| `--dry-run` | Preview without placing |

## How it Works

1. **Market resolution** — if you pass a Polymarket URL, it auto-imports via Simmer's import API and resolves to the correct market
2. **Price discovery** — fetches live CLOB order book, uses `asks[-1]` (best ask) + 0.01 for FAK to guarantee fill
3. **Order placement** — signs and submits via simmer-sdk with your wallet key
4. **Confirmation** — reports shares filled, cost, and trade ID

## Requirements

- `SIMMER_API_KEY` — your Simmer API key
- `WALLET_PRIVATE_KEY` — your Polymarket wallet private key (for on-chain signing)
- `simmer-sdk >= 0.8.32`

---

Built for [Simmer](https://www.simmer.markets/) — the AI trading agent platform for Polymarket and Kalshi.
