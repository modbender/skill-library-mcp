# Fía Signals — OpenClaw Skill

Real-time crypto market intelligence for AI agents, powered by Fía Signals' live trading system. One command gives any OpenClaw agent instant access to professional-grade market data: regime detection, Fear & Greed index, funding rates, liquidations, OHLCV, on-chain Bitcoin metrics, and more — all via pay-per-call x402 micropayments.

---

## Prerequisites

Both are standard on macOS and Linux. No installation needed.

| Dependency | Check |
|------------|-------|
| `curl` | `curl --version` |
| `python3` | `python3 --version` |

---

## Quick Start

```bash
# Free — no payment required
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh preview

# Core intelligence (paid — 0.001 USDC each)
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh regime
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh fear-greed
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh funding
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh prices BTC,ETH,SOL
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh signals BTCUSDT
```

---

## Command Reference

### Free

| Command | Description |
|---------|-------------|
| `preview` | Live regime snapshot + Fear & Greed + full endpoint list |
| `discover` | Complete endpoint directory from `/.well-known/x402.json` |
| `help` | Full usage guide |

**Example output — `preview`:**
```
=== Fía Signals — Free Preview ===
┌─── Fía Signals — Live Preview ──────────────────────────────────┐
│  Regime:       RANGING     RSI: 49.61  ADX: 16.66
│  Fear & Greed: 11 — Extreme Fear
│  Paid endpoints available: 16
│  Discovery:    https://x402.fiasignals.com/.well-known/x402.json
└──────────────────────────────────────────────────────────────────┘
```

---

### Core Market Intelligence

| Command | Args | Price | Description |
|---------|------|-------|-------------|
| `regime` | — | $0.001 | Market regime (TRENDING UP/DOWN/RANGING), RSI, ADX, confidence, recommendation |
| `fear-greed` | — | $0.001 | Fear & Greed index (0–100), 7-day history, contrarian signal |
| `funding` | — | $0.001 | Top 10 perpetual futures funding rates with annualised % |
| `prices` | `BTC,ETH,SOL` | $0.001 | Real-time spot prices for up to 20 symbols |
| `signals` | `SYMBOL` | $0.005 | RSI-14, MACD histogram, Bollinger %B, composite signal |

**Example output — `regime`:**
```
=== Fía Signals — Market Regime ===
Market Regime:  RANGING
Confidence:     0.72
RSI-14:         49.61
ADX:            16.66
Recommendation: Wait for breakout confirmation
```

**Example output — `fear-greed`:**
```
=== Fía Signals — Fear & Greed ===
Fear & Greed:  11 — Extreme Fear
7-day trend:   Declining
Signal:        Contrarian Buy — extreme fear often precedes recovery
```

**Example output — `funding`:**
```
=== Fía Signals — Funding Rates ===
Symbol         Rate       Annual
------------------------------------
🔴 BTCUSDT      0.0100%   109.5% pa
⚪ ETHUSDT      0.0050%    54.8% pa
🟢 SOLUSDT     -0.0010%   -10.9% pa
```

**Example output — `signals BTCUSDT`:**
```
=== Fía Signals — Technical Signals: BTCUSDT ===
Symbol:            BTCUSDT @ $84,320.00
RSI-14:            49.61 (Neutral)
MACD histogram:    -210.4 (Bearish)
Bollinger %B:      0.42 (Mid-range)
Composite signal:  NEUTRAL
```

---

### Market Structure

| Command | Args | Price | Description |
|---------|------|-------|-------------|
| `dominance` | — | $0.001 | BTC/ETH market dominance % |
| `liquidations` | — | $0.001 | Recent liquidation events — long/short volumes |
| `altseason` | — | $0.001 | Altseason index, BTC dominance, ETH/BTC ratio |
| `basis` | `SYMBOL` | $0.001 | Spot vs futures basis (premium/discount) |
| `open-interest` | `SYMBOL` | $0.001 | Open interest + 24h change + signal |
| `mark-price` | `SYMBOL` | $0.001 | Mark price, index price, next funding rate |

---

### Price Data

| Command | Args | Price | Description |
|---------|------|-------|-------------|
| `ohlcv` | `SYM [TF] [N]` | $0.002 | OHLCV candles — e.g. `ohlcv BTCUSDT 4h 50` |
| `gainers` | — | $0.001 | Top 10 24h gainers with % change |
| `losers` | — | $0.001 | Top 10 24h losers with % change |
| `recent-trades` | `SYMBOL` | $0.001 | Recent trades with large block detection |
| `orderbook` | `SYMBOL` | $0.001 | Order book depth + bid/ask imbalance score |

---

### On-Chain & Macro

| Command | Args | Price | Description |
|---------|------|-------|-------------|
| `macro` | — | $0.005 | Cross-asset macro signal bundle |
| `btc-metrics` | — | $0.001 | Bitcoin on-chain: hashrate, difficulty, mempool, supply |
| `gas` | — | $0.001 | Ethereum gas prices (slow/standard/fast Gwei) |
| `defi-tvl` | — | $0.001 | Top 10 DeFi protocols by TVL |
| `stablecoin-flows` | — | $0.001 | USDT/USDC volume as buying pressure indicator |

---

### Analytics

| Command | Args | Price | Description |
|---------|------|-------|-------------|
| `correlation` | `BTC,ETH,SOL,...` | $0.005 | 30-day cross-asset correlation matrix |
| `funding-history` | `SYMBOL [N]` | $0.001 | Historical funding rates — e.g. `funding-history BTCUSDT 24` |
| `oi-history` | `SYMBOL [TF] [N]` | $0.001 | Open interest history |

---

## Live API

All data is served from the Fía Signals x402 gateway:

- **Base URL:** `https://x402.fiasignals.com`
- **Discovery:** `https://x402.fiasignals.com/.well-known/x402.json`
- **Preview (free):** `https://x402.fiasignals.com/preview`

### Payment

Paid endpoints use the [x402 micropayment protocol](https://github.com/coinbase/x402) on Base network.

| Detail | Value |
|--------|-------|
| Currency | USDC |
| Network | Base (eip155:84532) |
| Wallet | `0x3c0D84055994c3062819Ce8730869D0aDeA4c3Bf` |
| Price range | $0.001 – $0.005 USDC per call |

### About Fía Signals

Fía Signals is an autonomous AI trading system running 24/7 on live crypto markets with real capital. The same intelligence that drives the trades is available per-call to any agent — no subscriptions, no rate limits, pay only for what you use.

Contact: `fia-trading@agentmail.to`

---

## Submitting to ClaWHub

Follow these steps to list this skill on [ClaWHub](https://clawhub.com):

### Step 1 — Package the skill

Make sure all files are present:

```
fia-signals-skill/
├── SKILL.md          ← OpenClaw trigger config
├── package.json      ← Skill metadata
├── README.md         ← This file
└── scripts/
    └── fia_signals.sh
```

Run a final smoke test:
```bash
chmod +x scripts/fia_signals.sh
./scripts/fia_signals.sh preview
./scripts/fia_signals.sh help
```

### Step 2 — Create a zip or push to GitHub

```bash
# Option A: zip
cd ~/.openclaw/workspace/skills
zip -r fia-signals-v1.1.0.zip fia-signals-skill/

# Option B: push to GitHub
cd fia-signals-skill
git init && git add . && git commit -m "Initial release v1.1.0"
git remote add origin https://github.com/yourorg/fia-signals-skill.git
git push -u origin main
```

### Step 3 — Submit on ClaWHub

1. Go to **https://clawhub.com**
2. Click **"Submit a skill"**
3. Fill in:
   - **Name:** `fia-signals`
   - **Version:** `1.1.0`
   - **Description:** Real-time crypto market intelligence — regime, RSI, Fear & Greed, funding rates, liquidations, OHLCV, on-chain data
   - **Category:** Finance / Market Data
   - **Tags:** `crypto`, `trading`, `bitcoin`, `signals`, `market-regime`, `fear-greed`, `funding-rates`, `x402`
   - **Repository / upload:** link to your GitHub repo or upload the zip
   - **Entrypoint:** `scripts/fia_signals.sh`
4. Click **Submit for review**

### Step 4 — Review

Skills are typically reviewed within 24–48 hours. You'll receive confirmation at the email or contact address on file.

---

*Built by Fía Signals · https://x402.fiasignals.com · fia-trading@agentmail.to*
