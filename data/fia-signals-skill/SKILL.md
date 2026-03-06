---
name: fia-signals
description: >
  AI crypto market intelligence from Fía Signals. 65+ endpoints covering price predictions,
  technical analysis (RSI MACD EMA Bollinger), market sentiment, smart money tracking,
  DeFi yield rates, gas prices (14 chains), Solana trending tokens, MEV detection,
  wallet risk scoring, on-chain data, crypto signals, trading signals, regime detection,
  funding rates, VIRTUAL token analysis, smart contract auditing. Free tier — no API key.
  Use when asked about: crypto market data, price prediction, technical analysis, gas prices,
  Solana trending tokens, DeFi yields, MEV bots, smart contract audit, wallet risk,
  research topics, BTC due diligence, smart money tracking, whale activity, market sentiment,
  trading signals, regime detection, on-chain analytics, funding rates, crypto analysis.
---

# Fía Signals — Crypto Market Intelligence

Real-time crypto data for AI agents. 56 endpoints. Free tier works instantly — no keys, no signup.

## API Base URL

`https://api.fiasignals.com`

## Free Endpoints (no auth, no payment)

| Endpoint | Description |
|----------|-------------|
| `/v1/gas/prices` | Multi-chain gas prices (Ethereum, Base, Arbitrum, Polygon, Optimism) |
| `/v1/gas/prices/{chain}` | Gas prices for a specific chain |
| `/v1/gas/history/{chain}` | Gas price history |
| `/v1/solana/trending` | Top 20 trending Solana tokens with price, liquidity, volume |
| `/v1/solana/staking` | Solana staking rates and validator info |
| `/v1/solana/top-wallets` | Most active Solana wallets |
| `/v1/mev/bots` | Known MEV bot addresses and activity |
| `/v1/dd/quick/{symbol}` | Quick due diligence report for any crypto asset |
| `/v1/research/topics` | Current crypto research topics and papers |
| `/v1/yield/rates` | Best DeFi yield rates across protocols |
| `/v1/health` | API health check |

## Premium Endpoints (x402 USDC payment)

| Endpoint | Price | Description |
|----------|-------|-------------|
| `/v1/solana/new-launches` | $0.005 | Newly launched Solana tokens |
| `/v1/solana/new-pools` | $0.005 | New liquidity pools |
| `/v1/solana/smart-money` | $0.01 | Smart money wallet tracking |
| `/v1/solana/whales` | $0.01 | Whale movement alerts |
| `/v1/solana/yields` | $0.005 | Solana-specific yield opportunities |
| `/v1/mev/scan` | $0.01 | Full MEV risk scan for a transaction |
| `/v1/audit/quick/{address}` | $0.05 | Quick smart contract risk assessment |
| `/v1/audit/report` | $0.50 | Full smart contract audit report |
| `/v1/wallet/risk` | $0.02 | Wallet risk scoring |
| `/v1/wallet/profile/{address}` | $0.02 | Complete wallet profile and PnL |

## Usage

```bash
# Free — works immediately
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh gas
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh trending
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh yields
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh dd BTC
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh mev-bots
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh research
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh staking

# Premium — requires x402 USDC payment
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh whales
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh smart-money
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh new-launches
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh audit 0xContractAddress
```

## Data Source

Live data from Fía Signals API: https://api.fiasignals.com
Discovery doc: https://x402.fiasignals.com/.well-known/x402.json
Contact: fia-trading@agentmail.to
