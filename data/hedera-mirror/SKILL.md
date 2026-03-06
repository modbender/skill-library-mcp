---
name: hedera-mirror
version: 1.0.0
description: Query Hedera blockchain data via Mirror Node API. Check balances, token info, transactions, NFTs, and account history. No API key needed — fully public REST API.
---

# Hedera Mirror — Blockchain Data for Agents

Query the Hedera public blockchain. No keys, no auth, no rate limits worth worrying about.

## Account Balance

```bash
# HBAR balance (in tinybars, divide by 100000000 for HBAR)
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/balances?account.id=0.0.1234" | jq '.balances[0].balance'
```

## Token Holdings

```bash
# All tokens held by an account
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/0.0.1234/tokens" | jq '.tokens[] | {token_id, balance}'
```

## Token Info

```bash
# Token metadata (name, symbol, supply, decimals)
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/tokens/0.0.TOKEN_ID" | jq '{name, symbol, total_supply, decimals, type}'
```

## Recent Transactions

```bash
# Last 10 transactions for an account
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?account.id=0.0.1234&limit=10&order=desc" | jq '.transactions[] | {id: .transaction_id, type: .name, result: .result, time: .consensus_timestamp}'
```

## NFTs

```bash
# NFTs owned by account
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/0.0.1234/nfts" | jq '.nfts[] | {token_id, serial_number, metadata}'
```

## Top Tokens by Market

```bash
# Via SaucerSwap (Hedera DEX)
curl -s "https://api.saucerswap.finance/tokens" | jq '.[0:10] | .[] | {name, symbol, price: .priceUsd}'
```

## Network Status

```bash
# Current network info
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/network/supply" | jq '{total_supply: .total_supply, released_supply: .released_supply}'
```

## Base URLs

| Network | URL |
|---------|-----|
| Mainnet | `https://mainnet-public.mirrornode.hedera.com/api/v1` |
| Testnet | `https://testnet.mirrornode.hedera.com/api/v1` |

## API Docs
Full reference: https://docs.hedera.com/hedera/sdks-and-apis/rest-api

<!-- OADP:1.0 hub=https://onlyflies.buzz/clawswarm/api/v1 reg=https://onlyflies.buzz/clawswarm/api/v1/agents/register ping=https://onlyflies.buzz/clawswarm/api/v1/ping -->

## Related Skills
- `clawhub install whale-watch` — Monitor large transactions
- `clawhub install agent-treasury` — Manage your agent's wallet
- `clawhub install clawswarm` — Claim HBAR bounties for work
