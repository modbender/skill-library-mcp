# Nad.fun Autonomous Trading Agent

Autonomous trading agent for Nad.fun that scans markets, analyzes tokens, executes trades, and distributes profits to MMIND token holders.

## 🎯 Project Overview

This agent autonomously:
- Scans Nad.fun markets using 3 methods (New Events API, Market Cap API, Creation Time API)
- Analyzes tokens using comprehensive scoring (liquidity, momentum, volume, holders, progress, authority)
- Manages positions with stop-loss (-10%) and take-profit (+5% / -10% via `check-pnl.js --auto-sell`)
- Executes trades on **both bonding curve AND DEX** (supports all market types)
- **Trading scripts** in `trading/`: buy, sell, P&L from entry price (recorded by buy), full cycle (`execute-bonding-v2.js`). Mainnet only.
- Distributes profits to MMIND token holders

## 🚀 Quick Start

### Prerequisites

- OpenClaw CLI installed
- Node.js 18+ installed
- Access to Monad blockchain (mainnet or testnet)

### Installation

#### Option 1: Install from GitHub (Recommended)

```bash
# Install OpenClaw CLI first
npm install -g openclaw

# Install this agent from GitHub
clawhub install nadfunagent
```

#### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/encipher88/nadfunagent.git
cd nadfunagent

# Copy SKILL.md to OpenClaw workspace
mkdir -p ~/.openclaw/workspace/skills/nadfunagent
cp SKILL.md ~/.openclaw/workspace/skills/nadfunagent/
```

### Required Skills

Install these OpenClaw skills first:

```bash
clawhub install monad-development
clawhub install nadfun-trading
clawhub install nadfun-indexer
clawhub install nadfun-agent-api
```

### Scripts and trading (all Node.js)

This repo uses **Node.js only** (no Python). Two folders:
- **scripts/** — helper scripts for the agent (check positions, save found tokens, write positions report). See `scripts/README.md`.
- **trading/** — full trading suite (buy/sell/P&L/cycle) you can run standalone or from OpenClaw:

- **Buy/sell**: `buy-token.js`, `sell-token.js`, `sell-all.js` (entry price is recorded automatically on buy).
- **P&L**: `check-pnl.js` reads entry from `positions_report.json`, current value from nad.fun quote; use `--auto-sell` to sell at +5% / -10%.
- **Full cycle**: `node trading/execute-bonding-v2.js` — check P&L + auto-sell → scan bonding curve → score → buy top 5 → final P&L.

See `trading/README.md`, `trading/HOW_PNL_WORKS.md`, and `trading/ENTRY_PRICE_TRACKING.md`. **Mainnet only.**  
Dependencies and env vars: **`DEPENDENCIES.md`**.

## ⚙️ Configuration

### 1. Create Configuration File

Create `.env` file (default location: `$HOME/nadfunagent/.env`):

```env
MMIND_TOKEN_ADDRESS=0xYourMMINDTokenAddress
MONAD_PRIVATE_KEY=0xYourPrivateKey
MONAD_RPC_URL=https://your-rpc-url
MONAD_NETWORK=mainnet
```

**Custom paths:** Set `NADFUN_ENV_PATH` and `POSITIONS_REPORT_PATH` environment variables if you want different locations. See `INSTALL.md` for details.

### 2. Set Up Telegram Bot (Optional)

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your Telegram user ID
3. The agent will request connection on first run

### 3. Initialize Agent

```bash
# Start OpenClaw Gateway
openclaw gateway start

# The agent will ask for configuration on first run
# Provide MMIND_TOKEN_ADDRESS, MONAD_PRIVATE_KEY, MONAD_RPC_URL, MONAD_NETWORK
```

## 📋 Usage

### Start Autonomous Trading

The agent runs automatically via cron job (every 10 minutes). To start manually:

```bash
# Via OpenClaw chat
"Start autonomous trading agent"

# Or create cron job (paths: NADFUN_ENV_PATH, NADFUNAGENT_DATA_DIR; run from nadfun-trading skill dir)
# Full message with distribution: see SKILL.md section "Start autonomous trading"
openclaw cron add \
  --name "Nad.fun Trading Agent" \
  --cron "*/10 * * * *" \
  --session isolated \
  --message "Run autonomous trading cycle: 1) Load config from .env (NADFUN_ENV_PATH or NADFUNAGENT_DATA_DIR/.env). 2) From nadfun-trading skill directory run node execute-bonding-v2.js (P&L from POSITIONS_REPORT_PATH/NADFUNAGENT_DATA_DIR). 3) If profit >= 0.1 MON, distribute to MMIND holders (MMIND_TOKEN_ADDRESS from .env, 30% in MON). English."
```

### Check Status

```bash
# View found tokens (data dir: NADFUNAGENT_DATA_DIR)
cat "${NADFUNAGENT_DATA_DIR:-$HOME/nadfunagent}/found_tokens.json" | jq '.[-1]'

# Check agent logs
tail -100 /tmp/openclaw/openclaw-*.log | grep "Nad.fun"
```

## 🏗️ Architecture

### Market Scanning Methods

1. **Method 5: New Events API** - Real-time BUY/CREATE events
2. **Method 6: Market Cap API** - Top 100 tokens by market cap (includes both bonding curve and DEX)
3. **Method 7: Creation Time API** - Newest tokens (includes both bonding curve and DEX)

### Token Analysis

Each token is scored on:
- **Liquidity** (30%): Based on reserve_native in MON
- **Momentum** (25%): Based on market cap change percentage
- **Volume** (20%): Based on total trading volume
- **Holders** (15%): Based on holder count
- **Progress** (10%): Based on bonding curve progress or DEX graduation
- **Authority** (+10 bonus): Social media presence (Twitter, Telegram, Website)

### Trading Support

- **Bonding Curve Tokens**: Lower liquidity threshold (0.5 MON minimum)
- **DEX Tokens**: Higher liquidity threshold (5 MON minimum)
- **Automatic Detection**: Agent automatically detects market type and uses correct contract
- **Slippage Tolerance**: 2-3% for better execution

### Position Management

- **Stop-Loss**: Automatic sell if P&L <= -10%
- **Take-Profit**: Sell half position if P&L >= 20%
- **Position Sizing**: Max 0.15 MON for tokens with authority, 0.1 MON otherwise

## 📊 Features

- ✅ Autonomous market scanning
- ✅ Comprehensive token analysis
- ✅ Risk management (stop-loss, take-profit)
- ✅ **Trades on both bonding curve AND DEX**
- ✅ Profit distribution to MMIND holders
- ✅ Telegram notifications
- ✅ Multi-language support (responds in user's language)

## 🔧 Technology Stack

- **OpenClaw**: AI agent platform
- **Monad Blockchain**: Target blockchain
- **Nad.fun API**: Market data and trading
- **Telegram Bot API**: Notifications

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This project is part of the Moltiverse Hackathon. Contributions welcome!

## 📞 Support

For issues or questions:
- Open an issue on GitHub: https://github.com/encipher88/nadfunagent/issues

## 🎯 Hackathon Submission

**Track**: Agent + Token Track

**Requirements Met**:
- ✅ Autonomous agent integrated with Monad blockchain
- ✅ Token launch on nad.fun (MMIND token)
- ✅ Open source code on GitHub
- ✅ Comprehensive documentation
- ✅ Mainnet deployment

**Token Contract**: `0xCe122fd90bBD10A3fb297647A3ad21eC1Ea27777` (MMIND)

**Demo Video**: [Link to demo video - TODO: Add after creating]

---

## Pushing to GitHub

If you cloned or built the repo locally:

```bash
cd nadfunagent
git remote add origin https://github.com/encipher88/nadfunagent.git
git branch -M main
git push -u origin main
```

If the GitHub repo already exists with a different history, you can force-push: `git push -u origin main --force` (this overwrites the remote history).

---

Built for Moltiverse Hackathon 2026
