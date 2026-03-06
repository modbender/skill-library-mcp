---
name: web3-data
description: >
  Explore Web3 on-chain data using Chainbase APIs. Use this skill when the user asks about
  blockchain data, token holders, wallet addresses, token prices, NFTs, ENS domains, transactions,
  DeFi portfolios, or any on-chain analytics. Triggers include: "top holders of", "who holds",
  "wallet address", "address labels", "token price", "token transfers", "NFT owners",
  "ENS domain", "on-chain data", "blockchain query", "SQL query on-chain", or any request
  to look up, analyze, or explore Web3/blockchain data across Ethereum, BSC, Polygon, Arbitrum,
  Optimism, Base, Avalanche, zkSync, and other EVM chains.
---

# Web3 Data Explorer (Chainbase)

Query on-chain data via Chainbase Web3 API and SQL API.

## Quick Reference

**API Key**: Use env `CHAINBASE_API_KEY`, falls back to `demo`. If rate-limited, direct user to https://console.chainbase.com to upgrade.

**Script**: `scripts/chainbase.sh <endpoint> [params...]`

```bash
# Top token holders
scripts/chainbase.sh /v1/token/top-holders chain_id=1 contract_address=0xdAC17F958D2ee523a2206206994597C13D831ec7 limit=10

# Address labels
scripts/chainbase.sh /v1/address/labels chain_id=1 address=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# SQL query
scripts/chainbase.sh /query/execute --sql="SELECT * FROM ethereum.blocks ORDER BY number DESC LIMIT 5"
```

## Chain IDs

| Chain | ID | Chain | ID |
|---|---|---|---|
| Ethereum | 1 | Optimism | 10 |
| BSC | 56 | Base | 8453 |
| Polygon | 137 | zkSync | 324 |
| Avalanche | 43114 | Merlin | 4200 |
| Arbitrum | 42161 | | |

Default to Ethereum (chain_id=1) unless user specifies otherwise.

## Routing Logic

Match user intent to the right endpoint:

| User wants | Endpoint |
|---|---|
| Top token holders / who holds a token | `GET /v1/token/top-holders` |
| List of holder addresses | `GET /v1/token/holders` |
| Token price | `GET /v1/token/price` |
| Historical token price | `GET /v1/token/price/history` |
| Token info (name, symbol, supply) | `GET /v1/token/metadata` |
| Token transfer history | `GET /v1/token/transfers` |
| Address labels/tags | `GET /v1/address/labels` |
| Wallet transaction history | `GET /v1/account/txs` |
| Single transaction detail | `GET /v1/tx/detail` |
| Native token balance (ETH/BNB) | `GET /v1/account/balance` |
| ERC20 token balances of wallet | `GET /v1/account/tokens` |
| NFTs owned by wallet | `GET /v1/account/nfts` |
| DeFi portfolio positions | `GET /v1/account/portfolios` |
| ENS domain lookup | `GET /v1/ens/records` or `/v1/ens/reverse` |
| NFT metadata/owner/rarity | `GET /v1/nft/metadata`, `/owner`, `/rarity` |
| Trending NFT collections | `GET /v1/nft/collection/trending` |
| **Anything not covered above** | **SQL API** (`POST /query/execute`) |

## Workflow

1. **Identify intent** — Determine what data the user needs
2. **Resolve identifiers** — If user gives token name (e.g. "USDT"), look up the contract address. Common tokens:
   - USDT: `0xdAC17F958D2ee523a2206206994597C13D831ec7` (ETH)
   - USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` (ETH)
   - WETH: `0xC02aaA39b223FE8D0A0e5c4F27eAD9083C756Cc2` (ETH)
   - DAI: `0x6B175474E89094C44Da98b954EedeAC495271d0F` (ETH)
   - WBTC: `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` (ETH)
   - If unknown, use `GET /v1/token/metadata` or ask the user for the contract address
3. **Select endpoint** — Use the routing table above; fall back to SQL API for complex/custom queries
4. **Execute** — Run via `scripts/chainbase.sh` or direct `curl`
5. **Present results** — Format data clearly with tables for lists, highlight key insights

## SQL API Fallback

When fixed endpoints don't cover the query, translate user intent to SQL:

```bash
scripts/chainbase.sh /query/execute --sql="SELECT from_address, SUM(value) as total FROM ethereum.token_transfers WHERE contract_address = '0x...' GROUP BY from_address ORDER BY total DESC LIMIT 20"
```

Common table patterns (replace `ethereum` with chain name):
- `{chain}.blocks` — Block data
- `{chain}.transactions` — Transactions
- `{chain}.token_transfers` — ERC20 transfers
- `{chain}.token_metas` — Token metadata
- `{chain}.logs` — Event logs

SQL constraints: max 100,000 results per query.

For complete endpoint parameters and response schemas, read [references/api-endpoints.md](references/api-endpoints.md).
