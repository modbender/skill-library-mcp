# Fungible & NFT Endpoints Reference

## Table of Contents
- [GET /v1/fungibles/](#list-fungibles)
- [GET /v1/fungibles/{fungible_id}](#get-fungible-by-id)
- [GET /v1/fungibles/{fungible_id}/charts/{chart_period}](#fungible-chart)
- [GET /v1/fungibles/by-implementation](#fungible-by-implementation)
- [GET /v1/nfts/](#list-nfts)
- [GET /v1/nfts/{nft_id}](#get-nft-by-id)
- [GET /v1/chains/](#list-chains)

---

## List Fungibles

`GET /v1/fungibles/`

Search and list fungible assets with market data.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `currency` | No | `usd` | Price currency |
| `filter[search_query]` | No | — | Text search (1-66 chars), e.g., "ethereum", "USDC" |
| `filter[implementation_chain_id]` | No | — | Keep only fungibles on this chain |
| `filter[implementation_address]` | No | — | Keep only fungibles at this address |
| `filter[fungible_ids]` | No | — | Comma-separated IDs (max 25) |
| `filter[fungible_implementations]` | No | — | chain:address pairs (max 25) |
| `sort` | No | — | Options: `-market_data.market_cap`, `market_data.market_cap`, `-market_data.price.last`, `market_data.price.last`, `-market_data.price.percent_change_1d`, etc. (also 30d, 90d, 365d) |
| `page[size]` | No | 100 | Max items (1-100) |

**Note**: `filter[implementation_address]` ignores `filter[search_query]`.

### Response Shape (per item)

```json
{
  "type": "fungibles",
  "id": "0x2af...",
  "attributes": {
    "name": "Bankless BED Index",
    "symbol": "BED",
    "description": "...",
    "icon": { "url": "https://..." },
    "flags": { "verified": true },
    "external_links": [{ "type": "website", "name": "Website", "url": "https://..." }],
    "implementations": [
      { "chain_id": "ethereum", "address": "0x...", "decimals": 18 }
    ],
    "market_data": {
      "price": 106.88,
      "market_cap": 3196313.74,
      "fully_diluted_valuation": 3196313.74,
      "total_supply": 29905.76,
      "circulating_supply": 29905.76,
      "changes": {
        "percent_1d": -0.74,
        "percent_30d": -2.50,
        "percent_90d": 11.32,
        "percent_365d": null
      }
    }
  },
  "relationships": {
    "chart_hour": { "links": { "related": "https://api.zerion.io/v1/fungibles/.../charts/hour" } },
    "chart_day": { "links": { "related": "..." } },
    "chart_week": { "links": { "related": "..." } },
    "chart_month": { "links": { "related": "..." } },
    "chart_year": { "links": { "related": "..." } },
    "chart_max": { "links": { "related": "..." } }
  }
}
```

---

## Get Fungible by ID

`GET /v1/fungibles/{fungible_id}`

Get detailed info for a specific fungible asset by its Zerion ID.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `fungible_id` (path) | Yes | Zerion fungible ID |
| `currency` | No | Price currency (default: `usd`) |

---

## Fungible Chart

`GET /v1/fungibles/{fungible_id}/charts/{chart_period}`

Price chart for a fungible asset.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `fungible_id` (path) | Yes | Zerion fungible ID |
| `chart_period` (path) | Yes | `hour`, `day`, `week`, `month`, `3months`, `6months`, `year`, `5years`, `max` |
| `currency` | No | Price currency (default: `usd`) |

### Response Shape

```json
{
  "data": {
    "type": "fungible_charts",
    "attributes": {
      "begin_at": "2023-01-18T11:00:00Z",
      "end_at": "2023-01-25T10:30:00Z",
      "points": [[1674039600, 1567.23], [1674041400, 1572.45]]
    }
  }
}
```

Points are `[unix_timestamp, price_in_currency]`.

---

## Fungible by Implementation

`GET /v1/fungibles/by-implementation`

Look up a fungible by its on-chain address. Useful when you have a contract address and need the Zerion fungible ID.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `implementation_chain_id` | Yes | Chain ID (e.g., `ethereum`) |
| `implementation_address` | Yes | Contract address |
| `currency` | No | Price currency |

---

## List NFTs

`GET /v1/nfts/`

Search and list NFTs across all chains.

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `filter[search_query]` | No | — | Text search |
| `filter[chain_ids]` | No | — | Filter by chains |
| `filter[collection_ids]` | No | — | Filter by collection IDs |
| `currency` | No | `usd` | Price currency |
| `page[size]` | No | 100 | Max items (1-100) |

---

## Get NFT by ID

`GET /v1/nfts/{nft_id}`

Get detailed info for a specific NFT including metadata, content URLs, market data, and attributes.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `nft_id` (path) | Yes | NFT unique ID |
| `currency` | No | Price currency |

---

## List Chains

`GET /v1/chains/`

Returns all supported blockchain networks. Use chain IDs from this endpoint in `filter[chain_ids]` parameters.

Common chain IDs: `ethereum`, `polygon`, `arbitrum`, `optimism`, `base`, `avalanche`, `binance-smart-chain`, `fantom`, `zksync-era`, `linea`, `xdai` (Gnosis), `aurora`, `celo`, `solana`.
