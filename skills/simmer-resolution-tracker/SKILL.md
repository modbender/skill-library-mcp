---
name: simmer-resolution-tracker
displayName: Simmer Resolution Tracker and Auto-Redeemer
description: Monitors your Simmer positions for resolutions, logs wins/losses to your trade journal, and automatically redeems winning positions on-chain. Built for Simmer agents trading on Polymarket. Sends Discord webhook alerts on every resolution. Runs every 5 minutes via cron.
metadata:
  clawdbot:
    emoji: "🔍"
    requires:
      pip: ["simmer-sdk"]
      env:
        - SIMMER_API_KEY
        - WALLET_PRIVATE_KEY
        - DISCORD_WEBHOOK
    cron: "*/5 * * * *"
    automaton:
      managed: true
      entrypoint: "resolution_tracker.py"
version: "1.0.0"
published: true
---

# Simmer Resolution Tracker and Auto-Redeemer

Monitors your Simmer positions every 5 minutes. When a market resolves, it:
- Logs the win/loss and PnL to your trade journal
- Posts a Discord alert (💰 win / ❌ loss)
- Automatically redeems winning positions on-chain (Polymarket only)
- Tracks cooldown state per strategy for loss streak detection

Built for [Simmer](https://www.simmer.markets/) — the AI trading agent platform for Polymarket and Kalshi.

## Setup

Set these environment variables:

```bash
SIMMER_API_KEY=your_api_key          # From simmer.markets/account
WALLET_PRIVATE_KEY=your_private_key  # Polymarket wallet (for on-chain redemptions)
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...  # Optional: for alerts
```

## Usage

Run manually:
```bash
python3 resolution_tracker.py
```

Or let your agent run it on a cron schedule (every 5 minutes recommended).

## What It Does

1. **Fetches resolved positions** from Simmer API (`?status=resolved`)
2. **Matches to trade journal** — finds the original trade entry, updates it with outcome + PnL
3. **Calculates PnL** — `shares - cost` for wins, `-cost` for losses (binary market math)
4. **Posts Discord alert** — win 💰 or loss ❌ with strategy name and P&L
5. **Auto-redeems** — calls Simmer SDK `redeem()` for winning Polymarket positions, verifies tx hash
6. **Tracks cooldowns** — records win/loss per strategy for consecutive-loss detection

## File Structure

The tracker reads/writes these files in your `data/` directory:

| File | Purpose |
|------|---------|
| `trade_journal.jsonl` | Your trade log — updated with resolved/outcome/pnl |
| `resolved_trades.jsonl` | Append-only log of all resolutions |
| `resolved_markets.json` | IDs already reported (dedup) |
| `redeemed_markets.json` | IDs already redeemed on-chain |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SIMMER_API_KEY` | ✅ | Your Simmer API key |
| `WALLET_PRIVATE_KEY` | ✅ | Polymarket wallet private key for redemptions |
| `DISCORD_WEBHOOK` | Optional | Discord webhook URL for alerts |
| `POLY_MODE` | Optional | Set to `sim` for simulation mode (skips on-chain redemptions) |
| `DATA_DIR` | Optional | Override data directory (default: `./data/live`) |
