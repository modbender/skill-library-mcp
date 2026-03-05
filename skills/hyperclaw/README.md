# HyperClaw

An [AgentSkills](https://agentskills.io)-compatible skill for trading perpetual futures on [Hyperliquid](https://hyperliquid.xyz). Works with Claude Code, OpenClaw, and any agent that supports the AgentSkills standard.

**[View on ClawHub](https://clawhub.ai/zoan37/hyperclaw)**

Supports 229+ native crypto perps, HIP-3 builder-deployed perps (equities like TSLA, commodities like GOLD), market intelligence, and a caching proxy to prevent rate limiting.

## Quick Start

```bash
# 1. Clone into your skills directory
git clone https://github.com/zoan37/hyperclaw.git

# 2. Run setup (creates venv, installs deps)
bash hyperclaw/scripts/setup.sh

# 3. Configure credentials
cp hyperclaw/.env.example hyperclaw/.env
# Edit .env with your Hyperliquid API key

# 4. Start the caching proxy (recommended)
hyperclaw/scripts/.venv/bin/python hyperclaw/scripts/server.py &

# 5. Test
hyperclaw/scripts/.venv/bin/python hyperclaw/scripts/hyperliquid_tools.py price BTC
```

## For AI Agents

See [SKILL.md](SKILL.md) for the full command reference and usage instructions that agents read.

## Commands

- **Account:** `status`, `positions`, `orders`, `check`, `portfolio`, `user-funding`, `swap`
- **Market Data:** `price`, `funding`, `book`, `candles`, `funding-history`, `trades`, `raw`
- **Analysis:** `analyze`, `scan`, `hip3`, `dexes`, `history`
- **Trading:** `leverage`, `buy`, `sell`, `limit-buy`, `limit-sell`, `stop-loss`, `take-profit`, `close`, `cancel`, `cancel-all`, `modify-order`
- **Intelligence (requires Grok API):** `sentiment`, `unlocks`, `devcheck`, `ask`, `search`
- **Prediction Markets:** `polymarket`

## Account Setup

**Unified mode is recommended** for API wallet trading. In standard mode, funds are split between spot and perp clearinghouses, and API wallets cannot transfer between them. Unified mode pools all funds so cross-margin perps can access your full balance. Enable it at [app.hyperliquid.xyz](https://app.hyperliquid.xyz) → Portfolio → Account Mode.

For HIP-3 dexes that use non-USDC collateral (USDH, USDe, USDT0), use the `swap` command to convert USDC before trading.

## Features

- **229+ perps** — all native Hyperliquid perpetual futures
- **HIP-3 multi-dex** — equities (TSLA, META, NVDA), commodities (GOLD, SILVER), forex, and more across 7+ builder dexes
- **HIP-3 collateral swaps** — `swap` command for USDC ↔ USDH/USDe/USDT0 on dexes that require non-USDC collateral
- **Caching proxy** — reduces API weight usage, prevents rate limiting for agents making many calls
- **Account modes** — auto-detects unified, portfolio margin, and standard accounts
- **Order types** — market, limit, stop-loss, take-profit, modify
- **Position health** — `check` command shows book ratio, funding, liquidation proximity warnings
- **Market intelligence** — Grok-powered sentiment analysis, token unlock tracking, developer exodus signals
- **Prediction markets** — Polymarket odds for macro context

## License

MIT
