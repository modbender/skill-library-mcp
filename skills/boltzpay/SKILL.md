---
name: boltzpay
description: Pay for API data automatically — multi-protocol (x402 + L402), multi-chain
metadata: {"openclaw": {"emoji": "\u26a1", "requires": {"bins": ["npx"]}, "install": [{"id": "boltzpay-cli", "kind": "node", "label": "BoltzPay CLI"}]}}
---

# BoltzPay — Paid API Access for AI Agents

BoltzPay lets AI agents pay for API data automatically. It supports multiple payment protocols (x402 and L402) and multiple blockchains (Base and Solana), paying with USDC or Bitcoin Lightning. Agents can discover, evaluate, and purchase API data in a single workflow.

## Quick Start

Fetch data from a paid API endpoint:

```
npx @boltzpay/cli fetch https://invy.bot/api
```

## Commands

| Command | Description | Credentials Needed |
|---------|-------------|--------------------|
| `npx @boltzpay/cli fetch <url>` | Fetch and pay for API data | Yes |
| `npx @boltzpay/cli check <url>` | Check if URL requires payment | No |
| `npx @boltzpay/cli quote <url>` | Get a price quote | No |
| `npx @boltzpay/cli discover` | Browse compatible APIs | No |
| `npx @boltzpay/cli budget` | Check spending budget | No |
| `npx @boltzpay/cli history` | View payment history | No |
| `npx @boltzpay/cli wallet` | Check wallet address and balance | No |
| `npx @boltzpay/cli demo` | Interactive demo walkthrough | No |

## Setup

Set the following environment variables for paid API access:

- `COINBASE_API_KEY_ID` — Your Coinbase CDP API key ID
- `COINBASE_API_KEY_SECRET` — Your Coinbase CDP API key secret
- `COINBASE_WALLET_SECRET` — Your Coinbase CDP wallet secret
- `BOLTZPAY_DAILY_BUDGET` — Daily spending limit in USD (optional, default: unlimited)

Get your Coinbase CDP keys at [portal.cdp.coinbase.com](https://portal.cdp.coinbase.com).

## Examples

### 1. Discover available APIs

```
npx @boltzpay/cli discover
```

Browse the directory of paid APIs compatible with BoltzPay. No credentials needed.

### 2. Check price before paying

```
npx @boltzpay/cli check https://invy.bot/api
```

See the payment protocol, amount, and chain options without spending anything.

### 3. Fetch paid data

```
npx @boltzpay/cli fetch https://invy.bot/api
```

Automatically detects the payment protocol, pays with USDC, and returns the API response.

## No Credentials?

Seven of the eight commands work without any Coinbase credentials:

- `check` — see if a URL requires payment
- `quote` — get detailed pricing
- `discover` — browse the API directory
- `budget` — check spending limits
- `history` — view past transactions
- `wallet` — check wallet address and balance
- `demo` — interactive demo walkthrough

Only `fetch` requires credentials (it makes actual payments).

## Links

- [GitHub](https://github.com/leventilo/boltzpay)
- [npm](https://www.npmjs.com/package/@boltzpay/sdk)
- [Documentation](https://boltzpay.ai)
