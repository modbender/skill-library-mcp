# Wallet Endpoints Reference

## Table of Contents
- [GET /v1/wallets/{address}/portfolio](#portfolio)
- [GET /v1/wallets/{address}/positions/](#positions)
- [GET /v1/wallets/{address}/transactions/](#transactions)
- [GET /v1/wallets/{address}/pnl](#pnl)
- [GET /v1/wallets/{address}/charts/{chart_period}](#balance-chart)
- [GET /v1/wallets/{address}/nft-positions/](#nft-positions)
- [GET /v1/wallets/{address}/nft-collections/](#nft-collections)
- [GET /v1/wallets/{address}/nft-portfolio](#nft-portfolio)

---

## Portfolio

`GET /v1/wallets/{address}/portfolio`

Returns portfolio overview: total value, daily changes, distribution by chain and position type.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `address` (path) | Yes | — | Wallet address (0x... or Solana) |
| `currency` | No | `usd` | Price currency: usd, eth, btc, eur, krw, rub, gbp, aud, cad, inr, jpy, nzd, try, zar, cny, chf |
| `filter[positions]` | No | `only_simple` | `only_simple` (wallet only), `only_complex` (DeFi only), `no_filter` (all) |
| `sync` | No | `false` | `true` waits up to 30s for fresh data from blockchain |

### Response Shape

```json
{
  "data": {
    "type": "portfolio",
    "id": "0x...",
    "attributes": {
      "total": { "positions": 2017.49 },
      "changes": { "absolute_1d": 102.03, "percent_1d": 5.33 },
      "positions_distribution_by_type": {
        "wallet": 1864.77, "deposited": 78.04, "borrowed": 0.98,
        "locked": 5.78, "staked": 66.13
      },
      "positions_distribution_by_chain": {
        "ethereum": 1214.01, "optimism": 573.03, "arbitrum": 458.36
      }
    }
  }
}
```

---

## Positions

`GET /v1/wallets/{address}/positions/`

Returns list of individual fungible token positions with value, price, quantity, and DeFi metadata.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `address` (path) | Yes | — | Wallet address |
| `currency` | No | `usd` | Price currency |
| `filter[positions]` | No | `only_simple` | `only_simple`, `only_complex`, `no_filter` |
| `filter[position_types]` | No | — | Comma-separated: `deposit`, `loan`, `locked`, `staked`, `reward`, `wallet`, `investment` |
| `filter[chain_ids]` | No | — | Comma-separated chain IDs (e.g., `ethereum,polygon`) |
| `filter[fungible_ids]` | No | — | Comma-separated fungible IDs |
| `filter[dapp_ids]` | No | — | Comma-separated DApp IDs |
| `filter[trash]` | No | `only_non_trash` | `only_trash`, `only_non_trash`, `no_filter` |
| `sort` | No | `value` | `-value` (desc) or `value` (asc) |
| `sync` | No | `false` | Wait for fresh data |
| `X-Env` header | No | — | Set to `testnet` for testnet data |

### Response Shape (per item)

```json
{
  "type": "positions",
  "id": "...",
  "attributes": {
    "name": "Asset",
    "position_type": "wallet",
    "quantity": { "float": 123.46, "numeric": "123.45678" },
    "value": 5.38,
    "price": 0.0436,
    "changes": { "absolute_1d": 0.27, "percent_1d": 5.33 },
    "fungible_info": {
      "name": "Bankless BED Index", "symbol": "BED",
      "icon": { "url": "..." },
      "flags": { "verified": true },
      "implementations": [{ "chain_id": "ethereum", "address": "0x...", "decimals": 18 }]
    },
    "protocol": "aave-v3",
    "protocol_module": "lending",
    "group_id": "...",
    "application_metadata": { "name": "AAVE", "url": "https://app.aave.com/" }
  },
  "relationships": {
    "chain": { "data": { "type": "chains", "id": "polygon" } },
    "fungible": { "data": { "type": "fungibles", "id": "0x..." } },
    "dapp": { "data": { "type": "dapps", "id": "aave-v3" } }
  }
}
```

**LP positions**: Positions in the same liquidity pool share a `group_id`. Group by it to display pool tokens together.

---

## Transactions

`GET /v1/wallets/{address}/transactions/`

Returns paginated transaction history with transfers, approvals, and DApp metadata.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `address` (path) | Yes | — | Wallet address |
| `currency` | No | `usd` | Price currency |
| `filter[operation_types]` | No | — | Comma-separated: `approve`, `burn`, `claim`, `delegate`, `deploy`, `deposit`, `execute`, `mint`, `receive`, `revoke`, `revoke_delegation`, `send`, `trade`, `withdraw` |
| `filter[asset_types]` | No | — | `fungible`, `nft` |
| `filter[chain_ids]` | No | — | Comma-separated chain IDs |
| `filter[fungible_ids]` | No | — | Filter by specific tokens |
| `filter[min_mined_at]` | No | — | Start timestamp (ms), e.g., `1688842525735` |
| `filter[max_mined_at]` | No | — | End timestamp (ms) |
| `filter[search_query]` | No | — | Full-text search (2-64 chars) |
| `filter[trash]` | No | `no_filter` | Spam filtering |
| `page[size]` | No | 100 | Max items per page (1-100) |
| `X-Env` header | No | — | `testnet` for testnet data |

### Pagination

Use `links.next` from the response to get the next page. Do not construct `page[after]` manually.

### Response Shape (per item)

```json
{
  "type": "transactions",
  "id": "...",
  "attributes": {
    "operation_type": "trade",
    "hash": "0x...",
    "mined_at": "2022-08-15T11:26:31+00:00",
    "mined_at_block": 15345739,
    "sent_from": "0x...",
    "sent_to": "0x...",
    "status": "confirmed",
    "nonce": 3757,
    "fee": {
      "fungible_info": { "name": "Ether", "symbol": "ETH" },
      "quantity": { "float": 0.015 },
      "price": 2542.23,
      "value": 39.97
    },
    "transfers": [
      {
        "fungible_info": { "name": "USDC", "symbol": "USDC" },
        "direction": "out",
        "quantity": { "float": 1000.0 },
        "value": 1000.0,
        "price": 1.0,
        "sender": "0x...",
        "recipient": "0x..."
      }
    ],
    "approvals": [],
    "application_metadata": {
      "name": "Uniswap",
      "method": { "name": "Swap" }
    }
  }
}
```

---

## PnL

`GET /v1/wallets/{address}/pnl`

Returns profit/loss analysis using FIFO accounting.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `address` (path) | Yes | — | Wallet address |
| `currency` | No | `usd` | Price currency |
| `filter[chain_ids]` | No | — | Limit to specific chains |
| `filter[fungible_ids]` | No | — | Limit to specific tokens (max 100) |
| `filter[fungible_implementations]` | No | — | chain:address pairs (max 100) |

### Response Shape

```json
{
  "data": {
    "type": "pnl",
    "attributes": {
      "realized_gain": -655.36,
      "unrealized_gain": 17.54,
      "total_fee": 281.91,
      "net_invested": 45.84,
      "received_external": 133971.29,
      "sent_external": 133270.09,
      "sent_for_nfts": 133971.29,
      "received_for_nfts": 133971.29
    }
  }
}
```

**Note**: When filtering by `fungible_ids` or `fungible_implementations`, assets without prices are auto-excluded. Check `meta.excluded_fungible_ids` in response.

---

## Balance Chart

`GET /v1/wallets/{address}/charts/{chart_period}`

Returns time-series balance data for charting.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `address` (path) | Yes | — | Wallet address |
| `chart_period` (path) | Yes | — | `hour`, `day`, `week`, `month`, `3months`, `6months`, `year`, `5years`, `max` |
| `currency` | No | `usd` | Price currency |
| `filter[chain_ids]` | No | — | Limit to specific chains |
| `filter[fungible_ids]` | No | — | Limit to specific tokens |

### Response Shape

```json
{
  "data": {
    "type": "wallet_charts",
    "attributes": {
      "begin_at": "2023-01-18T11:00:00Z",
      "end_at": "2023-01-25T10:30:00Z",
      "points": [[1674039600, 1145.01], [1674041400, 1148.23]]
    }
  }
}
```

Each point is `[unix_timestamp, balance_in_currency]`.

---

## NFT Positions

`GET /v1/wallets/{address}/nft-positions/`

Returns individual NFT positions with floor prices and collection info.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `address` (path) | Yes | — | Wallet address |
| `currency` | No | `usd` | Price currency |
| `filter[chain_ids]` | No | — | Filter by chains |
| `filter[collections_ids]` | No | — | Filter by collection IDs |
| `sort` | No | — | `created_at`, `-created_at`, `floor_price`, `-floor_price` |
| `include` | No | — | `nfts`, `nft_collections`, `wallet_nft_collections` |
| `page[size]` | No | 100 | Max items (1-100) |

**Note**: May return 202 if positions are still being aggregated. Retry until 200.

---

## NFT Collections

`GET /v1/wallets/{address}/nft-collections/`

Returns NFT collections held by the wallet with aggregate data.

---

## NFT Portfolio

`GET /v1/wallets/{address}/nft-portfolio`

Returns total NFT portfolio value for the wallet.
