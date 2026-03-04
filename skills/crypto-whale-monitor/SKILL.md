---
name: crypto-whale-monitor
description: Monitors large cryptocurrency wallet balances (whales) on-chain using Web3 RPC to detect potential market-moving activity. Can read from `references/wallets.md` or accept custom addresses.
---

# Crypto Whale Monitor

This skill contains the logic to connect to blockchain explorers and track large balances for a defined set of "whale" wallets.

## Workflow

1. **Define Wallets**: Add known whale addresses to `references/wallets.md`.
2. **Execute**: Run `npm start` (or `./scripts/monitor.js`) to scan the list.
3. **Analyze**: Review output for "WHALE DETECTED" alerts.
4. **Schedule**: Set up a cron job to run `npm start` periodically for automated monitoring.

## Scripts
- `scripts/monitor.js`: Core logic for checking balances via public RPC. Reads from `references/wallets.md` by default.

## References
- `references/wallets.md`: A list of known, public whale wallet addresses.
