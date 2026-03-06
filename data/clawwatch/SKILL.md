---
name: clawwatch
description: >
  Crypto and stock price watchlist tracker. Use when the user asks about their watchlist,
  wants to add/remove assets to track, check prices, set price alerts, or get a market overview.
  Supports BTC, ETH, and all major crypto via CoinPaprika + stocks via Yahoo Finance.
  Also provides the Crypto Fear & Greed Index.
tools: Bash, Read
---

# ClawWatch — Watchlist Skill

## Quick Reference

| User says... | You run... |
|---|---|
| "Füg Bitcoin zur Watchlist hinzu" | `clawwatch add BTC` |
| "Add NVIDIA and Tesla" | `clawwatch add NVDA TSLA --tag portfolio` |
| "Wie steht meine Watchlist?" | `clawwatch check --json` → parse & summarize |
| "Zeig mir nur die Kryptos" | `clawwatch list --type crypto --json` |
| "Alert wenn BTC über 100k geht" | `clawwatch alert add BTC above 100000` |
| "Alert if ETH drops 5% in a day" | `clawwatch alert add ETH change 5` |
| "Wie ist die Marktstimmung?" | `clawwatch feargreed` |
| "Entferne TSLA" | `clawwatch remove TSLA` |
| "Check my alerts" | `clawwatch alert check --json` |
| "Export als CSV" | `clawwatch export --format csv` |

## How to Use

1. Run commands via Bash tool: `bash clawwatch <command>`
2. Use `--json` flag to get machine-readable output you can parse
3. Summarize results in natural language for the user
4. For deep analysis, pass the JSON data to market-analyst agent

## Important Rules

- **Always use `--json` flag** when you need to parse the output programmatically
- **Don't run `clawwatch check` too frequently** — respect API rate limits (max every 60 seconds)
- **Auto-detection:** Just pass symbols like `BTC`, `ETH`, `NVDA`, `SAP.DE` — the tool auto-detects crypto vs stock
- **Alert exit codes:** `clawwatch alert check` returns exit code 0 (no alerts) or 1 (triggered)

## Combining with market-analyst

When the user asks for analysis (not just prices), chain:
1. `clawwatch check --json` → get current prices
2. Pass relevant data to market-analyst for interpretation
3. Deliver combined response

## Reading Cached Data

Instead of running CLI commands, you can read cached data directly:
- `~/.clawwatch/latest.json` — Last fetched prices
- `~/.clawwatch/watchlist.json` — Full watchlist state

## Installation

```bash
pip install clawwatch
# No API keys needed for crypto! Works out of the box.
# Optional: set CoinCap key for higher rate limits
clawwatch config --coincap-key YOUR_KEY  # optional
```
