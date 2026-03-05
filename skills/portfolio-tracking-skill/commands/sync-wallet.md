# /sync-wallet — Sync from Blockchain Wallet

Fetch token balances from EVM blockchain wallets.

## Behavior

1. Run `npx tsx <skill-path>/scripts/data-store.ts load-config` to get config
2. Find wallet configs with `type === 'wallet'`. If none configured, tell user to run `/setup`
3. For each wallet config (or the one user specifies):
   - If specific chains configured: sync only those chains
   - Otherwise: sync all 5 EVM chains
   - Run `npx tsx <skill-path>/scripts/blockchain-sync.ts sync <address> [chain]`
4. Load portfolio data
5. Merge results:
   - Match by `symbol` + `source.type === 'wallet'` + `source.chain`
   - Update quantities for existing assets
   - Add new assets with `source: { type: 'wallet', walletConfigId, walletName, chain }`
   - Remove assets no longer present
6. Save data
7. Show summary:

```
Synced wallet "0x1234...5678":

ETH chain:
  ETH: 2.500
  USDT: 1,000.00
  USDC: 500.00

BSC chain:
  BNB: 5.000

Total: 4 assets across 2 chains
```

## Supported Chains

- **ETH** — Ethereum (native: ETH)
- **BSC** — BNB Smart Chain (native: BNB)
- **POLYGON** — Polygon (native: MATIC)
- **ARBITRUM** — Arbitrum (native: ETH)
- **OPTIMISM** — Optimism (native: ETH)

## Notes

- All blockchain assets are classified as `type: 'CRYPTO'`, `currency: 'USD'`
- Dust amounts are filtered: native < 0.0001, ERC20 < 0.01
- Only checks common tokens (USDT, USDC, DAI, WBTC, LINK, etc.)
- Uses public RPCs — may be rate-limited on heavy use
- New assets get `currentPrice: 0` — remind user to run `/prices`
- If multiple wallets configured, ask which one to sync (or sync all)
