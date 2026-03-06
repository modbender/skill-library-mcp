---
name: okx-competition
description: "5 AI trading agents compete live on OKX Demo (real prices). Evolutionary tournament — losers get replaced daily. Exchange-level stop-losses protect capital. Full autonomous trading system: strategy backtesting, agent evolution, cron automation. Use for: algorithmic trading research, paper trading, building toward live trading. Supports OKX Demo and Live modes."
version: 1.0.0
---

# OKX Competition Manager 🏆

5 AI agents. 1 winner per day. Losers get replaced by better strategies.

Runs 24/7. You watch the leaderboard.

## How It Works

```
5 agents trade OKX Demo (real-time prices, zero risk)
  ↓ Every 5 minutes: fetch prices → calculate signals → place orders
  ↓ Exchange-level SL on every trade (survives bot crashes)
  ↓ Every 24 hours (07:00): evolve
    → Rank 1-2: survive (proven)
    → Rank 3: keep strategy, swap underperforming assets
    → Rank 4-5: replaced by best_strategies from researcher
```

## Features

### 5 Competing Agents
Each agent has a unique strategy:
- **S&D Hunter** — Supply & Demand zones, trend-following
- **S&D Sniper** — Supply & Demand with tight SL
- **RSI Reverter** — RSI mean reversion with EMA filter
- **RSI Sniper** — Fast RSI confirmation (EMA20>50 bounce)
- **RSI Trend** — RSI trend-following with EMA50>200

### Evolutionary Tournament
```
Daily 07:00 → evolve_agents.js:
  🥇 #1 → survive unchanged
  🥈 #2 → survive unchanged
  🥉 #3 → keep strategy, replace losing assets with backtest winners
  4️⃣ #4 → full replacement from best_strategies/
  5️⃣ #5 → full replacement from best_strategies/
```

### Exchange-Level Stop-Loss
Every order includes OKX native SL:
```js
slTriggerPx: entryPrice * (1 - stopLossPct)
slOrdPx: -1  // market SL
```
Bot can die. Positions stay protected.

### 3-Layer Position Safety
1. Skip trade if asset CT_VALS unknown (no sizing bugs)
2. Max 50% equity per agent per trade
3. $500 hard cap per single trade

## Setup

### Prerequisites
- OKX account (Demo or Live)
- OKX API key with trading permissions
- Node.js 18+
- OpenClaw (for cron automation)

### Step 1: OKX API Keys

**Demo Trading (recommended start):**
1. OKX → Trade → Demo Trading → Advanced Mode
2. API Management → Create API Key
3. Permissions: Read + Trade

**Live Trading:**
Same flow, but in live account.

### Step 2: Configure Secrets

Create `.secrets/okx.env`:
```
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
OKX_DEMO=true   # set to false for live
```

### Step 3: Core Files

```
bybit-trading/                    # historical name, OKX system
├── competition_manager_okx.js    ← main competition loop
├── helpers_okx.js                ← OKX API wrapper + indicators
├── evolve_agents.js              ← daily evolution (generates pending_evolution.json)
├── apply_evolution.js            ← apply evolution after Yossi approval
├── agents_config.json            ← current 5 agents + strategies
├── leaderboard_okx.json          ← live leaderboard (read by dashboard)
├── competition_log_okx.txt       ← verbose trade log
├── competition.lock              ← PID lockfile (prevents duplicates)
└── strategies/
    ├── supply_demand.js
    ├── rsi_mean_reversion.js
    ├── rsi_fast_confirm.js
    └── rsi_trend_filter.js
```

### Step 4: CT_VALS Configuration

**Critical — wrong CT_VALS = wrong position size = losses**

In `helpers_okx.js`, configure contract values for each asset:
```js
const CT_VALS = {
  'BTC-USDT-SWAP': 0.01,
  'ETH-USDT-SWAP': 0.1,
  'SOL-USDT-SWAP': 1,
  'XRP-USDT-SWAP': 100,
  'ADA-USDT-SWAP': 100,
  'DOGE-USDT-SWAP': 1000,
  'TRX-USDT-SWAP': 1000,
  'LTC-USDT-SWAP': 1,
  'LINK-USDT-SWAP': 1,
  'BNBUSDT': 0.1,
};
```

Find the correct value: OKX API `/api/v5/public/instruments?instType=SWAP&instId=ASSET-USDT-SWAP`

### Step 5: Start the Competition

```bash
node competition_manager_okx.js
```

The competition will:
- Load agents from `agents_config.json`
- Run a 5-minute loop
- Create `competition.lock` with PID
- Write results to `leaderboard_okx.json`

### Step 6: Automate with Task Scheduler (Windows)

Create `guardian.vbs` for zero-flash auto-restart:
```vbs
' guardian.vbs — starts competition if not running
Set oShell = CreateObject("WScript.Shell")
Set oFS = CreateObject("Scripting.FileSystemObject")

lockFile = "C:\Users\User\.openclaw\workspace\bybit-trading\competition.lock"

If oFS.FileExists(lockFile) Then
  pid = Trim(oFS.OpenTextFile(lockFile,1).ReadLine())
  ' Check if PID is alive (WMI)
  strCmd = "powershell -Command ""(Get-Process -Id " & pid & " -ErrorAction SilentlyContinue) -ne $null"""
  result = oShell.Run(strCmd, 0, True)
  If result = 0 Then WScript.Quit  ' Still running
End If

' Start competition
oShell.Run "cmd /c node C:\Users\User\.openclaw\workspace\bybit-trading\competition_manager_okx.js >> competition.log 2>&1", 0, False
```

Register in Task Scheduler: every 2 minutes, run as user, run whether logged in or not.

## Agents Config (agents_config.json)

```json
{
  "agents": [
    {
      "id": 1,
      "name": "S&D Hunter #1",
      "strategy": "supply_demand",
      "assets": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"],
      "timeframe": "5m",
      "capital": 300,
      "risk_per_trade_pct": 2
    }
  ]
}
```

**Iron Rules:**
- `timeframe` = always `"5m"` (never change)
- `risk_per_trade_pct` = 2% maximum
- Every new asset → verify CT_VALS first

## Evolution System

### Generate Recommendations (automatic, daily 07:00)
```bash
node evolve_agents.js
```
Creates `pending_evolution.json` — does NOT modify agents_config.json.

### Review & Apply
Review `pending_evolution.json`, then:
```bash
node apply_evolution.js
```

Never auto-apply without human review — this is by design.

## Strategy Researcher Integration

Pair with the `strategy-researcher` skill for continuous strategy discovery:

```
strategy-researcher/
├── run_nightly.js    ← 22:00-06:00 backtesting
├── run_daytime.js    ← 07:00-21:30 backtesting
└── best_strategies/  ← JSON results → fed into evolve_agents.js
```

The researcher backtests hundreds of strategy/asset/parameter combinations overnight. Best performers go into the evolution pool.

## Live Dashboard

Serve `leaderboard_okx.json` to a web dashboard for real-time monitoring:

```js
// Simple Express server for dashboard
app.get('/api/leaderboard', (req, res) => {
  res.json(JSON.parse(fs.readFileSync('bybit-trading/leaderboard_okx.json')));
});
```

## Going Live

When ready to trade real money:

1. 7 consecutive profitable days on Demo
2. P&L > 15% total
3. 30+ trades executed
4. Max drawdown < 10%
5. Zero CT_VALS sizing bugs

Then:
- Remove `OKX_DEMO=true` from `.secrets/okx.env`
- Replace Demo API keys with Live keys
- Start with $100-150

## KISS Principle

> Simple > Complex. Every extra indicator costs.

The best strategies here are dead simple:
- **RSI Fast Confirm**: EMA20>50 + RSI bounce from one candle. That's it.
  - DOGE: PF=4.90, LTC: PF=2.90
- **Supply/Demand**: Price touches S/D zone + reversal candle.
  - BTC 15m: PF=2.90, DD=0.69%

Don't add layers. Test first.

## Production Stats

Running 24/7 since 22.02.2026 on OKX Demo:
- Timeframe: 5m candles
- 19 tradeable assets
- Evolution: daily at 07:00
- Best single-day gain: +8.25% (RSI Reverter)
- System uptime: 99%+ (VBS guardian + Task Scheduler)
