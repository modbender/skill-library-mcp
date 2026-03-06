---
name: einstein
description: >
  Blockchain analytics and DeFi intelligence via Einstein's x402 micropayment services.
  Use when user wants on-chain market analysis, token research, whale tracking, smart money
  tracking, rug pull scanning, launchpad monitoring (Pump.fun, Zora, Virtuals), portfolio
  analysis, MEV detection, cross-chain arbitrage, or Polymarket data. Supports Base, Ethereum,
  BSC, Arbitrum, Polygon, Optimism, zkSync, Solana. Costs $0.25-$1.15 USDC per query via
  x402 protocol on Base.
metadata:
  author: project-einstein
  version: "1.1.0"
  disable-model-invocation: true
  clawdbot:
    emoji: "🧠"
    homepage: "https://emc2ai.io"
    requires:
      bins: ["node", "curl"]
      env: ["EINSTEIN_X402_PRIVATE_KEY"]
---

# Einstein — Blockchain Analytics via x402

Einstein provides 27 blockchain analytics services accessible via x402 micropayments (USDC on Base). Each query costs $0.25–$1.15 depending on complexity.

## Quick Start

```bash
# 1. Install dependencies (manual step — the setup wizard will NOT run npm for you)
cd packages/project-einstein/openclaw-skill/einstein && npm install

# 2. Set your private key via environment variable (recommended)
export EINSTEIN_X402_PRIVATE_KEY=0x_your_private_key_here

# 3. Or run the interactive setup wizard
node scripts/einstein-setup.mjs

# 4. List all services (free)
node scripts/einstein.mjs services

# 5. Run a query (will prompt for payment confirmation)
node scripts/einstein.mjs top-movers --chain base --limit 10
```

**Requirements:**
- Node.js 18+
- Dependencies installed via `npm install` (not auto-installed)
- A **dedicated** wallet private key with USDC on Base network (do NOT use your main wallet)
- Set `EINSTEIN_X402_PRIVATE_KEY` environment variable (preferred) or run setup with `--save-config`

## Service Categories

| Tier | Price (Raw) | Price (+AI) | Services |
|------|-------------|-------------|----------|
| Basic | $0.25 | $0.40 | Latest tokens, token chart |
| Standard | $0.40 | $0.55 | Top movers, top tokens, OHLCV, Virtuals, wallet holdings, holder concentration |
| Platform | $0.60 | $0.75 | Zora launches/volume, Pump.fun launches/volume/graduation, BSC alpha, liquidity shifts |
| Advanced | $0.85 | $1.00 | Whale intel, smart money, top traders, DEX capital, token sniping, Polymarket events |
| Comprehensive | $1.00 | $1.15 | Investment report, NFT analytics, MEV detection, arbitrage scanner, rug pull scanner, Polymarket compare |

**Raw** = structured data only. **+AI** = includes AI-generated analysis and insights (default).

## Free Services

These commands are free and do not require x402 payment or a wallet key.

### Epstein Files Search

Search 44,886+ DOJ-released Jeffrey Epstein documents (Jan 2026 release) via the DugganUSA public index.

```bash
# Search by name
node scripts/einstein.mjs epstein-search --query "Ghislaine Maxwell" --limit 10

# Search by topic
node scripts/einstein.mjs epstein-search --query "flight logs" --limit 20

# Search by location
node scripts/einstein.mjs epstein-search --query "Little St James"
```

| Flag | Description | Default |
|------|-------------|---------|
| `--query <terms>` | Search query (required) | — |
| `--limit <N>` | Number of results (1-500) | `10` |

## Usage Examples

### Market Analysis

```bash
# Top movers on Base in the last 24 hours
node scripts/einstein.mjs top-movers --chain base --timeperiod 1d --limit 10

# Top tokens by market cap on Ethereum
node scripts/einstein.mjs top-tokens --chain ethereum --limit 20

# Latest deployed tokens with liquidity
node scripts/einstein.mjs latest-tokens --chain base --limit 15
```

### Whale & Smart Money Intelligence

```bash
# Track whale accumulation on Ethereum
node scripts/einstein.mjs whale-intel --chain ethereum --limit 10 --timeperiod 7d

# Smart money leaderboard on Base
node scripts/einstein.mjs smart-money --chain base --limit 20 --timeperiod 7d

# Capital-intensive DEX traders
node scripts/einstein.mjs dex-capital --chain base --limit 10 --timeperiod 3d
```

### Security & Risk Analysis

```bash
# Scan a token for rug pull risk
node scripts/einstein.mjs rug-scan --chain ethereum --token 0x1234...abcd

# Detect MEV/sandwich attacks
node scripts/einstein.mjs mev-detect --chain ethereum --limit 10 --timeperiod 1d

# Identify early snipers on a token
node scripts/einstein.mjs token-snipe --chain base --token 0x1234...abcd --limit 20
```

### Launchpad Monitoring

```bash
# Latest Pump.fun launches on Solana
node scripts/einstein.mjs pump-launches --limit 15 --timeperiod 1d

# Pump.fun tokens about to graduate
node scripts/einstein.mjs pump-grads --limit 10

# Zora launches on Base
node scripts/einstein.mjs zora-launches --limit 10 --timeperiod 3d

# Virtuals Protocol agent tokens
node scripts/einstein.mjs virtuals --limit 10 --timeperiod 7d
```

### Portfolio & Token Analysis

```bash
# Check wallet holdings
node scripts/einstein.mjs wallet --chain ethereum --wallet 0xd8dA...

# Token holder concentration
node scripts/einstein.mjs holders --chain base --token 0x1234... --limit 50

# Token price chart
node scripts/einstein.mjs chart --chain base --token 0x1234... --timeperiod 7d

# OHLCV data for technical analysis
node scripts/einstein.mjs ohlcv --chain base --token 0x1234... --timeperiod 30d
```

### Advanced Reports

```bash
# Multi-chain investment report
node scripts/einstein.mjs investment-report --chains base,ethereum,bsc --limit 10 --timeperiod 7d

# Cross-chain arbitrage opportunities
node scripts/einstein.mjs arbitrage --chain ethereum --limit 10 --timeperiod 1d

# NFT collection analytics
node scripts/einstein.mjs nft-analytics --chain ethereum --limit 10 --timeperiod 7d
```

### Prediction Markets

```bash
# Polymarket events (Polygon)
node scripts/einstein.mjs polymarket --limit 10 --timeperiod 7d

# Compare Polymarket API vs chain data
node scripts/einstein.mjs polymarket-compare --limit 10
```

## How Payment Works

Einstein uses the **x402 protocol** — an HTTP-native micropayment standard. Payment is automatic:

1. Your request hits Einstein's endpoint
2. Server responds with HTTP 402 + payment challenge
3. The skill signs a USDC TransferWithAuthorization (EIP-3009) using your private key
4. Request is re-sent with the payment signature
5. Coinbase CDP facilitator settles the USDC transfer on Base
6. You receive the analytics data

**No accounts, no API keys, no subscriptions.** Just USDC on Base and a private key.

## Options Reference

### `einstein.mjs` (query CLI)

| Flag | Description | Default |
|------|-------------|---------|
| `--chain <chain>` | Blockchain network | `base` |
| `--limit <N>` | Number of results (1-500) | `10` |
| `--timeperiod <period>` | Time window: 1d, 3d, 7d, 30d | `7d` |
| `--token <address>` | Token contract address | — |
| `--wallet <address>` | Wallet address | — |
| `--chains <c1,c2>` | Comma-separated chains | — |
| `--raw` | Data-only response (cheaper) | `false` |
| `--yes` / `-y` | Skip payment confirmation prompt | `false` |

To skip the confirmation prompt globally, set `EINSTEIN_AUTO_CONFIRM=true` or add `"autoConfirm": true` to config.json.

### `einstein-setup.mjs` (setup wizard)

| Flag | Description | Default |
|------|-------------|---------|
| `--key <privateKey>` | Private key (skips interactive prompt) | — |
| `--url <baseUrl>` | Base URL for Einstein API | `https://emc2ai.io` |
| `--chain <chain>` | Default blockchain network | `base` |
| `--save-config` | Write config.json to disk (otherwise prints env var exports) | `false` |

**Supported chains:** base, ethereum, bsc, solana, arbitrum, polygon, optimism, zksync

## Security Best Practices

**Use a dedicated wallet.** Create a separate wallet funded with a small amount of USDC for this skill. Do NOT use your primary wallet or any wallet holding significant funds.

**Prefer environment variables over config.json.** Environment variables (`EINSTEIN_X402_PRIVATE_KEY`) are not persisted to disk and are harder to accidentally commit to git. If you must use config.json (`--save-config`), restrict file permissions:

```bash
chmod 600 config.json
```

**What gets signed.** Each paid query signs an EIP-3009 `TransferWithAuthorization` message that authorizes a USDC transfer of the exact query price (shown before confirmation) from your wallet to the Einstein service address. The signature is single-use (unique nonce) and time-limited. No blanket approvals are granted.

**Payment confirmation.** By default, the CLI prompts before every paid query showing the exact cost. To skip the prompt for scripted/automated use, pass `--yes` / `-y` per-command or set `EINSTEIN_AUTO_CONFIRM=true` globally.

**No auto-installed packages.** The setup wizard does NOT run `npm install` automatically. You must install dependencies yourself so you can audit what is being installed.

**No home directory scanning.** Configuration is loaded only from environment variables and the skill-local `config.json`. No paths outside the skill directory are read.

## Troubleshooting

**"No private key configured"**
Set `EINSTEIN_X402_PRIVATE_KEY` environment variable or run `node scripts/einstein-setup.mjs --save-config`.

**"Payment rejected" / "Insufficient balance"**
Your wallet needs USDC on Base. Bridge via https://bridge.base.org. Use a dedicated wallet with a small balance.

**"Cannot reach emc2ai.io"**
Check internet connection. The service may have temporary downtime.

**"Unknown service"**
Run `node scripts/einstein.mjs services` to see all available commands.

**"Dependencies not installed"**
Run `npm install` in the skill directory: `cd packages/project-einstein/openclaw-skill/einstein && npm install`

## References

- `references/services-catalog.md` — Full service catalog with parameters
- `references/payment-guide.md` — Detailed x402 payment protocol guide
- `references/examples.md` — Extended usage examples by category
