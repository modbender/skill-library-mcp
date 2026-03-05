---
name: lighter
description: Interact with Lighter protocol - a ZK rollup orderbook DEX. Use when you need to trade on Lighter, check prices, manage positions, or query account data.
env:
  required:
    - LIGHTER_API_KEY
    - LIGHTER_ACCOUNT_INDEX
  optional:
    - LIGHTER_L1_ADDRESS
---

# Lighter Protocol

Trade on Lighter - a zero-knowledge rollup orderbook DEX with millisecond latency and zero fees.

## Quick Start (Read-Only)

```bash
# Markets are public - no credentials needed
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBooks"
```

## What is Lighter?

- Zero fees for retail traders
- Millisecond latency
- ZK proofs of all operations
- Backed by Founders Fund, Robinhood, Coinbase Ventures

**API Endpoint:** https://mainnet.zklighter.elliot.ai
**Chain ID:** 300

## ⚠️ Security Considerations

### Third-Party Dependencies

This skill can work with **just requests library** for read-only operations. For signing orders, you have two options:

**Option A: Minimal (Read-Only)**
```bash
pip install requests
```
Only for public data (markets, order books, prices).

**Option B: Full Trading**
Requires the official Lighter SDK. Review and verify before installing:
- SDK Repository: https://github.com/elliottech/lighter-python
- Verify the repository owner, stars, and code before running any setup

### External Code

**Only proceed with external SDK if you:**
1. Have reviewed the GitHub repository
2. Understand what the code does
3. Use a dedicated burner wallet, not your main wallet

## Environment Variables

| Variable | Required | Description | Where to Find |
|----------|----------|-------------|---------------|
| `LIGHTER_API_KEY` | For orders | API key from Lighter SDK setup | See "Getting an API Key" section below |
| `LIGHTER_ACCOUNT_INDEX` | For orders | Your Lighter subaccount index (0-252) | See "Getting Your Account Index" section below |
| `LIGHTER_L1_ADDRESS` | Optional | Your ETH address (0x...) used on Lighter | Your MetaMask/Wallet address |

### Setting Up Your Credentials

**Step 1: Get your L1 Address**
- This is your Ethereum address (e.g., `0x1234...abcd`)
- Use the same wallet you connect to Lighter dashboard

**Step 2: Get your Account Index**
```bash
curl "https://mainnet.zklighter.elliot.ai/api/v1/accountsByL1Address?l1_address=YOUR_ETH_ADDRESS"
```
Response returns `sub_accounts[].index` — that's your account index (typically 0 for main account).

**Step 3: Get your API Key**
1. Install Lighter Python SDK: `pip install lighter-python`
2. Follow the setup guide: https://github.com/elliottech/lighter-python/blob/main/examples/system_setup.py
3. The SDK generates API keys tied to your account
4. Store the private key securely — never commit to git

**Quick test (read-only, no credentials):**
```bash
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBooks"
```

## API Usage

### Public Endpoints (No Auth)

```bash
# List all markets
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBooks"

# Get order book
curl "https://mainnet.zklighter.elliot.ai/api/v1/orderBook?market_id=1"

# Get recent trades
curl "https://mainnet.zklighter.elliot.ai/api/v1/trades?market_id=1"
```

### Authenticated Endpoints

```bash
# Account balance (requires API key in header)
curl -H "x-api-key: $LIGHTER_API_KEY" \
  "https://mainnet.zklighter.elliot.ai/api/v1/account?by=index&value=$LIGHTER_ACCOUNT_INDEX"
```

## Getting Your Account Index

See "Setting Up Your Credentials" table above for the quick curl command.

## Getting an API Key

See "Setting Up Your Credentials" table above for the step-by-step guide.

## Common Issues

**"Restricted jurisdiction":**
- Lighter has geographic restrictions - ensure compliance with their terms

**SDK signing issues:**
- Use create_market_order() instead of create_order() for more reliable execution

## Market IDs

| ID | Symbol |
|----|--------|
| 1 | ETH-USD |
| 2 | BTC-USD |
| 3 | SOL-USD |

## Links

- API: https://mainnet.zklighter.elliot.ai
- Dashboard: https://dashboard.zklighter.io
- SDK: https://github.com/elliottech/lighter-python

---

## Additional Examples

See `USAGE.md` in this skill folder for:
- Detailed curl commands for all endpoints
- Order book and trade queries
- Account and position checks
- Signed transaction flow (nonce → sign → broadcast)

**Disclaimer:** Review all external code before running. Use dedicated wallets for trading.
