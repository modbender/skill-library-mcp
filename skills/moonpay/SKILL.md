---
name: moonpay
version: 0.6.23
description: "Your agent needs money. MoonPay is the crypto onramp for AI agents — wallets, swaps, bridges, transfers, DCA, limit orders, deposits, market data, and fiat on/off ramps via CLI or MCP."
tags: [crypto, trading, wallets, defi, solana, ethereum, mcp, fiat]
metadata:
  openclaw:
    emoji: "🌕"
    homepage: https://agents.moonpay.com
    requires:
      bins: [mp]
    install:
      - kind: node
        package: "@moonpay/cli"
        bins: [mp]
---

# MoonPay CLI

Your agent needs money. Give your agents crypto.

MoonPay is the crypto onramp for AI agents — non-custodial wallets, swaps, bridges, transfers, DCA, limit orders, deposits, market data, and fiat on/off ramps. One CLI for everything.

**Base URL:** `https://agents.moonpay.com`

## What is MoonPay CLI?

MoonPay CLI gives AI agents and humans full access to crypto:

- **Non-custodial** — Local wallets with OS keychain encryption. Keys never leave the machine.
- **Multi-chain** — Solana, Ethereum, Base, Polygon, Arbitrum, Optimism, BNB, Avalanche, TRON, Bitcoin
- **Multi-surface** — MoonPay CLI (`mp`), local MCP server (`mp mcp`), web chat
- **Trading** — Swap, bridge, transfer, DCA, limit orders, stop losses
- **Market intelligence** — Trending tokens, token analysis, price data, price alerts
- **Deposits** — Multi-chain deposit links with automatic stablecoin conversion
- **Fiat on/off-ramp** — Buy crypto with fiat (USD), virtual accounts with KYC
- **Deposits** — Multi-chain deposit links with automatic stablecoin conversion

## Quick Start

### Option A: CLI (Recommended)

```bash
# Install
npm install -g @moonpay/cli

# Login (opens browser for captcha verification)
mp login --email you@example.com
# Open the URL, solve captcha, get code from email
mp verify --email you@example.com --code 123456

# Create a wallet
mp wallet create --name main

# List tools
mp tools

# Search for a token
mp token search --query "SOL" --chain solana --limit 5

# Check balances
mp token balance list --wallet main --chain solana
```

### Option B: MCP Server (Local)

Run `mp mcp` to start a local MCP server over stdio. This exposes all CLI + remote tools to any MCP-compatible client (Claude Desktop, Cursor, Claude Code).

```json
{
  "mcpServers": {
    "moonpay": {
      "command": "mp",
      "args": ["mcp"]
    }
  }
}
```

### Option C: REST API

```bash
curl -X POST https://agents.moonpay.com/api/tools/token_search \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SOL", "chain": "solana", "limit": 5}'
```

## Authentication

**CLI:** Run `mp login --email you@example.com` to open a browser page with hCaptcha. After solving the captcha, a verification code is sent to your email. Run `mp verify --email you@example.com --code 123456`. Credentials are stored encrypted at `~/.config/moonpay/credentials.json` and auto-refresh. Run `mp logout` to clear stored credentials.

**REST API:** Use a Bearer token in the `Authorization` header. Obtain tokens via the login/verify flow or OAuth 2.0 with PKCE.

**Rate limits:** 5 requests/min (anonymous), 60 requests/min (authenticated).

**Terms of Use:** https://www.moonpay.com/legal/terms_of_use_europe_hypermint

---

## Core Tools

### Wallet Management

Wallets are HD (BIP39) — one mnemonic derives addresses for all chains. EVM wallets share a single address across Ethereum, Base, Polygon, Arbitrum, Optimism, BNB, and Avalanche.

```bash
mp wallet create --name main          # Create HD wallet (Solana + EVM + Bitcoin + TRON)
mp wallet import --name funded        # Import from mnemonic or private key (interactive)
mp wallet list                         # List all wallets (shows all chain addresses)
mp wallet retrieve --wallet main       # Get wallet details
mp wallet rename --wallet old --name new  # Rename a wallet
mp wallet export --wallet main         # Export mnemonic (interactive only)
mp wallet delete --wallet old          # Permanently delete a wallet
```

### Token Trading

Swaps, bridges, and transfers sign locally — keys never leave the machine.

```bash
# Swap (same chain)
mp token swap \
  --wallet main --chain solana \
  --from-token EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v \
  --from-amount 5 \
  --to-token So11111111111111111111111111111111111111111

# Bridge (cross chain)
mp token bridge \
  --from-wallet main --from-chain polygon \
  --from-token 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 \
  --from-amount 6 \
  --to-chain solana \
  --to-token EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v \
  --to-wallet <solana-address>

# Transfer
mp token transfer \
  --wallet main --chain solana \
  --token EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v \
  --amount 10 \
  --to <recipient-address>
```

### Market Data

```bash
# Search tokens
mp token search --query "BONK" --chain solana --limit 5

# Token details + market data
mp token retrieve --token <address> --chain solana

# Trending tokens
mp token trending list --chain solana --limit 10 --page 1

# Check balances
mp token balance list --wallet <address> --chain solana
```

### Fiat On-Ramp

```bash
# Buy crypto with fiat (amount in USD, returns checkout URL)
mp buy --token sol --amount 50 --wallet <address> --email <email>

# Virtual account (KYC-based fiat on-ramp)
mp virtual-account create
mp virtual-account wallet register --wallet main --chain solana
mp virtual-account onramp create --name "USD to USDC" --fiat USD --chain solana --stablecoin USDC
```

### Deposits

```bash
# Create a multi-chain deposit link
mp deposit create --name "My Deposit" --wallet <address> --chain solana --token USDC

# Check deposit details
mp deposit retrieve --id <deposit-id>

# List deposit transactions
mp deposit transaction list --id <deposit-id>
```

### Signing

```bash
# Sign a message
mp message sign --wallet main --chain solana --message "hello"

# Sign a transaction
mp transaction sign --wallet main --chain solana --transaction <base64>

# Send a signed transaction
mp transaction send --chain solana --transaction <signed-base64>
```

---

## Safety Rules

CLI tools (`mp token swap`, `mp token bridge`, `mp token transfer`) handle the full build, sign, broadcast flow automatically. Keys are signed locally and never sent to the server.

For server-side tools (REST API / MCP), use the **simulate-then-execute** pattern:

1. **Always simulate first** — call with `"simulation": true` to get a quote
2. **Show the quote** — display expected output, fees, slippage
3. **Get explicit confirmation** — never auto-execute without user approval
4. **Execute** — call with `"simulation": false` only after confirmation

---

## CLI Tools by Category

### Auth
| Tool | Description |
|------|-------------|
| `login` | Open browser for hCaptcha verification, sends email code |
| `verify` | Verify login code and store encrypted credentials |
| `logout` | Log out and clear stored credentials |
| `user retrieve` | Get the currently authenticated user |
| `consent check` | Check whether Terms of Service have been accepted |
| `consent accept` | Accept the Terms of Service and Privacy Policy |

### Wallet
| Tool | Description |
|------|-------------|
| `wallet create` | Create multi-chain HD wallet |
| `wallet import` | Import from mnemonic or private key |
| `wallet list` | List all local wallets |
| `wallet retrieve` | Get wallet details |
| `wallet rename` | Rename a wallet |
| `wallet delete` | Delete a local wallet |
| `wallet export` | Export mnemonic (interactive only) |

### Token Trading
| Tool | Description |
|------|-------------|
| `token swap` | Swap tokens on the same chain |
| `token bridge` | Bridge tokens across chains |
| `token transfer` | Transfer tokens to another address |

### Market Data
| Tool | Description |
|------|-------------|
| `token search` | Search tokens by name/symbol/address |
| `token retrieve` | Token metadata + market data |
| `token trending list` | Trending tokens by chain |
| `token balance list` | List token balances for a wallet |
| `bitcoin balance retrieve` | Get BTC balance |

### Transactions
| Tool | Description |
|------|-------------|
| `transaction list` | List swap/bridge transaction history |
| `transaction retrieve` | Get transaction details |
| `transaction sign` | Sign a transaction locally |
| `transaction send` | Broadcast a signed transaction |
| `message sign` | Sign a message (EIP-191, ed25519, ECDSA) |

### Fiat
| Tool | Description |
|------|-------------|
| `buy` | Buy crypto with fiat via MoonPay checkout (amount in USD) |
| `virtual-account create` | Create virtual account + start KYC |
| `virtual-account retrieve` | Get account status |
| `virtual-account wallet list` | List wallets registered for fiat on-ramp |
| `virtual-account wallet register` | Register wallet for fiat on-ramp |
| `virtual-account onramp create` | Create fiat to stablecoin onramp |
| `virtual-account onramp retrieve` | Get onramp details and banking info |
| `virtual-account onramp list` | List onramps |
| `virtual-account onramp delete` | Cancel an onramp |
| `virtual-account onramp payment create` | Create open banking payment link |
| `virtual-account onramp payment retrieve` | Get payment status |
| `virtual-account transaction list` | List fiat to stablecoin conversion history |
| `virtual-account kyc restart` | Start or restart KYC verification |
| `virtual-account kyc continue` | Check KYC status or get verification link |
| `virtual-account agreement list` | List legal agreements (pending or accepted) |
| `virtual-account agreement accept` | Accept a required legal agreement |

### Deposits
| Tool | Description |
|------|-------------|
| `deposit create` | Create multi-chain deposit link (USDC, USDC.e, USDT) |
| `deposit retrieve` | Get deposit details |
| `deposit transaction list` | List incoming deposit transactions |

### x402
| Tool | Description |
|------|-------------|
| `x402 request` | Make paid API request with automatic payment |

### Skills
| Tool | Description |
|------|-------------|
| `skill list` | List available AI skills |
| `skill retrieve` | Get skill instructions |
| `skill install` | Install skills for Claude Code |

### Feedback
| Tool | Description |
|------|-------------|
| `feedback create` | Submit feedback (type: bug, feature, or general) |

---

## x402 Rate Limit Upgrade

Pay to increase your API rate limit via the x402 protocol.

**Endpoint:** `POST https://agents.moonpay.com/x402/upgrade`

| Duration | Price | Length |
|----------|-------|--------|
| day | $1 USDC | 24 hours |
| month | $20 USDC | 30 days |

```bash
# With CLI (handles payment automatically)
mp upgrade --duration day --wallet main --chain solana
```

Payment: USDC via x402 on Solana or Base. Requires login. Payment is only settled on success.

---

## Pre-Built Skills

Install AI skills for Claude Code:

```bash
mp skill install
```

| Skill | Description |
|-------|-------------|
| `moonpay-auth` | CLI setup, login, wallet creation |
| `moonpay-block-explorer` | Open tx/wallet/token in chain explorers |
| `moonpay-buy-crypto` | Buy crypto with fiat |
| `moonpay-check-wallet` | View balances and portfolio |
| `moonpay-deposit` | Create deposit links with stablecoin conversion |
| `moonpay-discover-tokens` | Search, trending, risk assessment |
| `moonpay-export-data` | Export portfolio/tx history to CSV/JSON |
| `moonpay-feedback` | Submit bug reports and feature requests |
| `moonpay-mcp` | Configure MoonPay as MCP server |
| `moonpay-missions` | Guided walkthrough of capabilities |
| `moonpay-polymarket-ready` | Fund Polygon wallet for Polymarket |
| `moonpay-price-alerts` | Desktop notifications at target prices |
| `moonpay-swap-tokens` | Swap and bridge tokens |
| `moonpay-trading-automation` | DCA, limit orders, stop losses via cron/launchd |
| `moonpay-upgrade` | Upgrade rate limit via x402 payment |
| `moonpay-virtual-account` | Fiat on-ramp with KYC |
| `moonpay-x402` | Paid API requests |

---

## Supported Chains

| Chain | Chain ID | Features |
|-------|----------|----------|
| Solana | `solana` | Full trading, limit orders, DCA |
| Ethereum | `ethereum` | Swap, bridge, transfer, market data |
| Base | `base` | Swap, bridge, transfer, market data |
| Polygon | `polygon` | Swap, bridge, transfer, market data |
| Arbitrum | `arbitrum` | Swap, bridge, transfer, market data |
| Optimism | `optimism` | Swap, bridge, transfer, market data |
| BNB | `bnb` | Swap, bridge, transfer, market data |
| Avalanche | `avalanche` | Swap, bridge, transfer, market data |
| TRON | `tron` | Wallet addresses |
| Bitcoin | `bitcoin` | Balance, bridges |

---

## Tips for Agents

- **Resolve token addresses first** — call `token search` before trading if you only have a name/symbol
- **Check balances** — use `token balance list` before trading to confirm available amounts
- **Native token addresses** — Solana: `So11111111111111111111111111111111111111111`, EVM: `0x0000000000000000000000000000000000000000`
- **EVM wallets share one address** across Ethereum, Base, Polygon, Arbitrum, Optimism, BNB, Avalanche
- **CLI signs locally** — `mp token swap`, `mp token bridge`, `mp token transfer` handle the full flow (build → sign → broadcast)
- **Use `-f compact`** when piping CLI output to `jq` for scripting

---

## Links

- **Web App:** https://agents.moonpay.com
- **CLI:** `npm install -g @moonpay/cli`
- **MCP Server:** `mp mcp` (local, stdio)
- **Skills:** `mp skill install`
