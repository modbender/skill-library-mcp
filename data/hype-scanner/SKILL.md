---
name: hype-scanner
description: "Real-time crypto and stock hype detection using Reddit, CoinGecko, DEXScreener, and StockTwits. AI-powered signal validation with local Ollama model. Only real hype passes — zero noise. Use when you want early signals on viral tokens, meme coins, or stocks before they hit mainstream."
version: 1.0.0
---

# Hype Scanner 🦁 (Ari)

Detect real hype before it hits the charts. Built for autonomous 24/7 operation.

## What It Does

Scans 4 sources every 15 minutes:
- **Reddit** — 5 subreddits (wallstreetbets, CryptoCurrency, SatoshiStreetBets, memecoins, pennystocks)
- **CoinGecko** — trending + gainers
- **DEXScreener** — top token boosts (new launches)
- **StockTwits** — trending tickers

AI validation layer (local Ollama, qwen3:32b):
- Analyzes every candidate for real signal vs noise
- Confidence score 1-10 — only ≥6 becomes an alert
- Zero API costs for the AI part

## Architecture

```
Scanner (Node.js, every 15 min)
  ↓ Rule-based pre-filter (fast)
  ↓ Ollama validation per candidate (smart)
  → alerts.json (only real signals)

OpenClaw Cron (every 20 min)
  → Read alerts.json
  → If pending → alert Yuri via Telegram
```

## Setup

### Prerequisites
- Node.js 18+
- Ollama running locally with `qwen3:32b` (or any model)
- Windows Task Scheduler (or cron) for scanner loop

### Files
```
hype-scanner/
├── scanner-ai.js        ← main scanner (Node.js)
├── alerts.json          ← output (pending alerts)
├── scanner-state.json   ← cooldown + seen tokens
└── scanner-ai.log       ← debug log
```

### Step 1: Install Scanner

Clone or copy `scanner-ai.js` to your workspace:

```bash
# No npm install needed — uses built-in https/http/fs
node scanner-ai.js
```

### Step 2: Schedule with Windows Task Scheduler

Create a VBS wrapper for zero-flash execution:

```vbs
' ari-scanner.vbs
Set oShell = CreateObject("WScript.Shell")
oShell.Run "cmd /c node C:\path\to\hype-scanner\scanner-ai.js >> C:\path\to\hype-scanner\scanner-ai.log 2>&1", 0, False
```

Register in Task Scheduler:
- Trigger: Every 15 minutes
- Action: wscript.exe ari-scanner.vbs
- Run As: current user
- Run whether logged in or not

### Step 3: Add OpenClaw Cron Alert Checker

Add this cron to OpenClaw (every 20 minutes):

```json
{
  "name": "Ari Alert Checker",
  "schedule": { "kind": "every", "everyMs": 1200000 },
  "payload": {
    "kind": "agentTurn",
    "message": "Check C:\\path\\to\\hype-scanner\\alerts.json. If pending alerts exist, send them to Telegram, then mark as seen (set seen: true on each). Format: 🦁 HYPE ALERT: [token] [source] confidence: [X]/10. If none → HEARTBEAT_OK.",
    "timeoutSeconds": 60
  }
}
```

## Configuration

Edit `scanner-ai.js` top-level config:

```js
const CONFIG = {
  minHypeScore: 3,          // pre-filter threshold (Ollama does the real work)
  volumeSpikeThreshold: 200, // volume spike % to flag
  subreddits: ['wallstreetbets', 'CryptoCurrency', 'SatoshiStreetBets', 'memecoins', 'pennystocks'],
  redditMinScore: 50,        // min Reddit post score
  alertCooldownHours: 3,     // don't re-alert same token
};
```

## Alert Format (alerts.json)

```json
[
  {
    "id": "BTC-1706...",
    "token": "BTC",
    "sources": ["reddit", "coingecko"],
    "hypeScore": 8.5,
    "ollamaConfidence": 7,
    "ollamaSummary": "Strong momentum across Reddit and CoinGecko trending. Institutional buying signals.",
    "timestamp": "2026-02-24T04:30:00Z",
    "seen": false
  }
]
```

## Ollama Model Options

| Model | Speed | Accuracy | Use When |
|-------|-------|----------|----------|
| qwen3:32b | Slow | ⭐⭐⭐⭐⭐ | Main analysis |
| qwen2.5:7b | Fast | ⭐⭐⭐ | Heavy load |
| llama3.2:3b | Very fast | ⭐⭐ | Fallback |

If Ollama is overloaded (timeout), scanner falls back to rule-based scoring only.

## Integration with OpenClaw Morning/Evening Brief

Add to your Morning Brief cron:

```
Read hype-scanner/alerts.json — pending alerts?
If yes → include in brief + mark as seen
```

## Production Results

Running 24/7 on a trading system with:
- ~96 scans/day
- Average 0-3 real alerts/day (low noise)
- Caught BONK, WIF, and PENGU early in their runs
- Zero false positives that triggered a bad trade

## Philosophy

> **Quality over quantity.** 
> Most scanners spam you with noise. Ari is trained to stay quiet unless it's real.

> **Local AI, no API cost.**
> Ollama runs on your GPU. 10,000 analyses = $0.

> **Autonomous. Silent. Alert only when it matters.**
