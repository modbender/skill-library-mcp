---
name: kuvera
description: "Kuvera portfolio & market data CLI. Query mutual fund data, gold prices, USD/INR rates, fund category returns, and user portfolio info from Kuvera. Use when the user asks about their investments, mutual funds, gold prices, market overview, or Kuvera portfolio."
homepage: https://kuvera.in
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "bins": ["kuvera-cli"] },
      },
  }
---

# Kuvera Portfolio & Market Data CLI

Get Indian market data, mutual fund info, gold prices, and portfolio data from Kuvera.

## When to Use

✅ **USE this skill when:**

- "What's the gold price?"
- "How's the market doing?"
- "Top mutual funds"
- "Dollar rate / USD INR"
- "Show me mutual fund category returns"
- "Tell me about fund XYZ"
- "Show my Kuvera portfolio"
- "How are my investments doing?"
- "Show my recent transactions"
- "What are my active SIPs?"
- "What's my P&L / returns?"

## Commands

### Market Overview (gold + USD + MF categories)

```bash
kuvera-cli market
```

### Gold Price

```bash
kuvera-cli gold
```

### USD/INR Exchange Rate

```bash
kuvera-cli usd
```

### Mutual Fund Category Returns

```bash
kuvera-cli categories
```

### Mutual Fund Details (by code)

```bash
# Example: look up a specific fund
kuvera-cli fund LFAG-GR
```

### Top Mutual Funds

```bash
# Top bought funds
kuvera-cli top bought

# Top sold funds
kuvera-cli top sold

# Most watched funds
kuvera-cli top watched
```

### User Profile (requires login)

```bash
kuvera-cli user
```

### Investment Portfolio with P&L (requires login)

```bash
kuvera-cli portfolio
```

### Recent Transactions (requires login)

```bash
# Show last 20 transactions (default)
kuvera-cli transactions

# Show last N transactions
kuvera-cli transactions 10
```

### Active SIPs (requires login)

```bash
kuvera-cli sips
```

## ⛔ SAFETY — READ-ONLY

**This skill is strictly read-only. NEVER attempt to:**
- Buy, sell, redeem, or switch any mutual fund
- Place any order or modify any transaction
- Change any user settings or portfolio configuration
- Call any Kuvera API endpoint that modifies data

The CLI enforces this at the code level — all non-GET requests (except login) are blocked.

## Notes

- All market data commands work without login.
- `kuvera-cli user`, `portfolio`, `transactions`, and `sips` require prior login via `kuvera-cli login <email> <password>`.
- This is read-only. No buy/sell/trade operations are supported.
