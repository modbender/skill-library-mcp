---
name: Avalanche
description: Assist with Avalanche C-Chain transactions, AVAX transfers, subnets, and cross-chain bridges.
metadata: {"clawdbot":{"emoji":"🔺","os":["linux","darwin","win32"]}}
---

## Network Architecture (Critical)
- Avalanche has three chains: X-Chain, P-Chain, C-Chain — each serves different purpose
- C-Chain is EVM compatible — where most DeFi and tokens live, uses AVAX for gas
- X-Chain for fast transfers — native AVAX transfers, not EVM compatible
- P-Chain for staking — validators and subnet management
- Same AVAX token across all chains — but must transfer between chains to use

## C-Chain (Most Common)
- EVM compatible — MetaMask, same tools as Ethereum
- Uses AVAX for gas — need AVAX to transact
- Chain ID: 43114 — RPC: https://api.avax.network/ext/bc/C/rpc
- Block explorer: snowtrace.io — transaction verification
- Most tokens and DeFi here — Trader Joe, Aave, GMX

## Cross-Chain Transfers
- Moving AVAX between chains uses Avalanche Wallet — not regular transfers
- C-Chain ↔ X-Chain transfer takes seconds — but requires correct process
- Export from one chain, import to another — two-step process
- Use official Core wallet or Avalanche Wallet — supports all three chains
- MetaMask only sees C-Chain — can't transfer to X or P chains directly

## Bridging from Other Networks
- Avalanche Bridge official — bridge.avax.network, from Ethereum
- Bridged tokens are wrapped — ETH becomes WETH.e on Avalanche
- LayerZero, Stargate for multi-chain — faster alternatives with fees
- Bridge fees plus gas on both chains — budget for both
- Withdrawal to Ethereum can take time — depends on bridge used

## Gas and Fees
- Gas model same as Ethereum post-EIP-1559 — base fee + priority fee
- Cheaper than Ethereum, more than some L2s — typically $0.01-0.10 per transaction
- Gas paid in AVAX only — no token payments for gas
- Fast finality (under 2 seconds) — no waiting for confirmations
- Failed transactions cost gas — same as Ethereum

## Tokens and DeFi
- AVAX is native gas token — also tradeable like ETH
- WAVAX is wrapped AVAX — needed for some DeFi protocols
- Major DEXs: Trader Joe, Pangolin — similar to Uniswap
- Lending: Aave, Benqi — borrow and lend
- Verify token addresses — scam tokens exist, check snowtrace.io

## Subnets
- Subnets are custom blockchains on Avalanche — like app-specific chains
- DFK Chain (DeFi Kingdoms), Dexalot — examples of subnets
- Each subnet can have own token for gas — not always AVAX
- Bridging to subnets through official bridges — subnet-specific
- Subnets have independent validators — different security assumptions

## Staking
- Minimum 25 AVAX to delegate — stake with validators
- Minimum 2 weeks lock — staking period required
- Rewards vary by validator — check uptime and commission
- No slashing — underperforming validators just earn less
- Liquid staking: sAVAX, ggAVAX — maintain liquidity while staking

## Wallet Options
- Core Wallet (official) — supports all three chains, subnets
- MetaMask for C-Chain only — familiar interface, limited to C-Chain
- Ledger supported — via Core or MetaMask
- Mobile wallets available — Core has mobile app

## Common Issues
- "Insufficient funds" — need AVAX for gas on C-Chain
- Tokens on wrong chain — bridged to X-Chain instead of C-Chain
- Can't find tokens — wrong chain or need to add custom token
- Slow bridge — some bridges take 10-30 minutes, be patient
- Subnet tokens not showing — need to add subnet network to wallet

## Security
- Standard EVM security on C-Chain — same best practices as Ethereum
- Private key controls all three chains — one seed, all chains
- Verify addresses on all chains — X-Chain addresses start with "X-"
- Revoke unused approvals — snowtrace.io token approval checker
- Official bridges safest — third-party bridges add risk
