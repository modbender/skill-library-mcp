---
name: Bitpanda Portfolio Skill
description: Check Bitpanda crypto portfolio, wallet balances, and trade history via CLI.
---

# Bitpanda Portfolio Skill

Check Bitpanda crypto portfolio, wallet balances, and trade history via CLI.

## Auth

API key is read from (in order):
1. `BITPANDA_API_KEY` environment variable
2. `~/.openclaw/credentials/bitpanda/config.json` → `{"api_key": "..."}`

Generate at: https://web.bitpanda.com/my-account/apikey
Recommended scopes: **Balance**, **Trade**, **Transaction**

## Commands

```bash
bitpanda portfolio                    # Non-zero wallets grouped by crypto/fiat/index
bitpanda wallets                      # All non-zero wallets with balances
bitpanda transactions --limit 20      # Recent trades
bitpanda transactions --flow buy      # Buy trades only
bitpanda transactions --flow sell     # Sell trades only
bitpanda asset BTC                    # Current price + your balance
```

## Notes

- **Read-only** — no trading or transfers
- Assets in **Bitpanda Earn/Staking** are not exposed by the API and won't show in balances
- The `asset` command uses the public ticker (no auth needed) for prices
- Pagination is automatic
- Requires: `curl`, `jq`, `bc`
