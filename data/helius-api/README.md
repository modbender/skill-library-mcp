# helius-api

An [OpenClaw](https://github.com/openclaw/openclaw) skill for querying Solana data via the [Helius API](https://www.helius.dev/).

## What's Covered

### Wallet API (Beta)
- **Balances** — Token + NFT holdings with USD values
- **History** — Parsed transaction history with balance changes
- **Transfers** — Sent/received activity with counterparty info
- **Identity** — Wallet labels (exchanges, protocols, known entities)
- **Batch Identity** — Look up 100 addresses at once
- **Funded By** — Original funding source for attribution & sybil detection

### Enhanced Transactions API
- **Parse Transactions** — Turn raw signatures into human-readable structured data
- **Transaction History** — Enhanced history with type, time, and slot filtering

## Setup

1. Get an API key at [dashboard.helius.dev](https://dashboard.helius.dev)
2. Set the environment variable:
   ```bash
   export HELIUS_API_KEY="your-key-here"
   ```

## Installation

Drop the `helius-api` folder into your OpenClaw skills directory:

```
~/.openclaw/skills/helius-api/
```

Or install the packaged `.skill` file via OpenClaw.

## Structure

```
helius-api/
├── SKILL.md                          # Main skill file (triggers + overview)
└── references/
    ├── balances.md                   # Wallet balances endpoint
    ├── history.md                    # Wallet transaction history
    ├── transfers.md                  # Token transfer activity
    ├── identity.md                   # Wallet identity lookup
    ├── funded-by.md                  # Wallet funding source
    └── enhanced-transactions.md      # Parse + enhanced tx history
```

## Links

- [Helius Docs](https://www.helius.dev/docs)
- [Wallet API Overview](https://www.helius.dev/docs/wallet-api/overview)
- [Enhanced Transactions Overview](https://www.helius.dev/docs/enhanced-transactions/overview)
- [OpenClaw](https://github.com/openclaw/openclaw)
