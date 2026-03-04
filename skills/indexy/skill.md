# Indexy Agent Skill

## Overview

Indexy is a cryptocurrency index management platform that enables AI agents to create, manage, and analyze crypto indices similar to ETFs. The platform provides comprehensive data access for KPIs, mindshare metrics, and public index analytics.

**Base API:** `https://indexy.co`
**Web App:** `https://indexy.xyz`
**Full API Docs:** `https://docs.indexy.xyz/api`
**Version:** 1.0.0

> **Important:** `indexy.co` is the API domain for all programmatic requests. `indexy.xyz` is the web app for human users. Never send API requests to `indexy.xyz`.

## Authentication

Indexy supports two authentication methods. Choose the one that fits your use case:

### Method 1: API Key (Recommended for most agents)

Include your API key as a Bearer token. API keys always start with the `agent_` prefix:

```http
Authorization: Bearer agent_your_key_here
```

**Get Your API Key:**
1. Log in to [indexy.xyz](https://indexy.xyz)
2. Navigate to **Settings > Agent**
3. Create and manage your API keys

**Key Format:** All valid keys start with `agent_` followed by 64 hex characters (e.g., `agent_a1b2c3d4...`).

**Security Warning:** NEVER share your API key or send it to domains other than `indexy.co` or `indexy.xyz`.

### Method 2: Web3 Authentication (For on-chain agents)

Authenticate using EIP-191 signatures with an ERC-8004 Agent Identity NFT:

**Required Headers:**
```http
x-web3-address: 0xYourWalletAddress
x-web3-chain: base
x-web3-signature: 0xSignedMessage...
x-web3-message: Base64EncodedMessage
x-web3-timestamp: 1707500000000
```

**Supported Chains:** `base`, `ethereum`

See full Web3 authentication flow at: `https://docs.indexy.xyz/api`

## Rate Limits

- **Default:** 60 requests/minute per API key (configurable per key)
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Exceeded:** Returns `429 Too Many Requests`

Custom rate limits can be configured per API key. Contact support for adjustments.

## Core Capabilities

### 1. Index Management (Create & Update)

**Create an Index**

Use this when agents want to build their own crypto portfolios:

```
Create a DeFi blue chip index with:
- Uniswap: 40%
- Aave: 35%
- Curve: 25%
```

**Tool:** `create_index`
**Endpoint:** `POST /beta/indexes/agent`
**Auth:** Required (API Key or Web3)

All agent-created indices are marked as `index_category = 'agentic'`.

**Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Index name (max 40 characters) |
| `description` | string | No | Index description (max 500 characters) |
| `weightsType` | string | No | `market_caps` or `custom` (default: `custom`) |
| `selectedAssets` | array | Yes | Array of 1-50 assets (weights must sum to 100) |
| `selectedAssets[].contractAddress` | string | Yes | Token contract address |
| `selectedAssets[].network` | string | Yes | Blockchain network (see Supported Networks below) |
| `selectedAssets[].weight` | number | Yes | Weight percentage (0-100) |
| `methodologyAssetEligibility` | string | No | Asset eligibility criteria (max 2000 characters) |
| `methodologyWeightCaps` | string | No | Weight caps methodology (max 2000 characters) |
| `methodologyRebalancingCadence` | string | No | Rebalancing schedule (max 2000 characters) |

**Request Body Example:**
```json
{
  "name": "AI Layer-1 Index",
  "description": "Top Layer-1 blockchains with AI integration capabilities",
  "weightsType": "custom",
  "selectedAssets": [
    {
      "contractAddress": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
      "network": "ethereum",
      "weight": 40
    },
    {
      "contractAddress": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
      "network": "ethereum",
      "weight": 35
    },
    {
      "contractAddress": "0xd533a949740bb3306d119cc777fa900ba034cd52",
      "network": "ethereum",
      "weight": 25
    }
  ],
  "methodologyAssetEligibility": "Tokens must have a minimum market cap of $100M and be listed on at least 2 major exchanges.",
  "methodologyWeightCaps": "No single asset can exceed 40% of the total index weight.",
  "methodologyRebalancingCadence": "The index is rebalanced monthly on the first trading day of each month."
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Index created successfully",
  "data": {
    "indexId": 823,
    "name": "AI Layer-1 Index",
    "description": "Top Layer-1 blockchains with AI integration capabilities",
    "weightsType": "custom",
    "methodologyAssetEligibility": "Tokens must have a minimum market cap of $100M...",
    "methodologyWeightCaps": "No single asset can exceed 40%...",
    "methodologyRebalancingCadence": "The index is rebalanced monthly...",
    "createdAt": "2026-02-10T16:30:00.000Z"
  }
}
```

---

**Update an Index**

Modify existing indices you own:

```
Update my index #123 to rebalance: increase Uniswap to 50%, decrease others proportionally
```

**Tool:** `update_index`
**Endpoint:** `PATCH /beta/indexes/agent/{indexId}`
**Auth:** Required (must be the index creator)

Supports two modes determined by the fields you include:
- **Metadata only:** Send only `name`, `description`, or `methodology*` fields. The asset composition remains unchanged.
- **Full rebalance:** Include a `selectedAssets` array. This **replaces the entire asset composition** - you must provide the complete list of assets with new weights summing to 100.

**Metadata-Only Update Example:**
```json
{
  "name": "Updated AI Index",
  "description": "Refined strategy focusing on top AI-integrated chains",
  "methodologyRebalancingCadence": "Rebalanced bi-weekly on Mondays"
}
```

**Full Rebalance Example:**
```json
{
  "selectedAssets": [
    {
      "contractAddress": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
      "network": "ethereum",
      "weight": 60
    },
    {
      "contractAddress": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
      "network": "ethereum",
      "weight": 40
    }
  ],
  "methodologyWeightCaps": "Maximum single asset weight increased to 60%"
}
```

**Response Example (200):**
```json
{
  "success": true,
  "message": "Index updated successfully",
  "data": {
    "indexId": 823
  }
}
```

### 2. Read Your Indices

**List Your Indices**

```
Show me all indices I've created
```

**Tool:** `list_my_indexes`
**Endpoint:** `GET /beta/indexes/agent`
**Auth:** Required

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Results per page (max: 50) |

**Response Example:**
```json
{
  "success": true,
  "data": [
    {
      "id": 823,
      "name": "AI Layer-1 Index",
      "description": "Top Layer-1 blockchains with AI integration capabilities",
      "weights_type": "custom",
      "index_category": "agentic",
      "current_bps": 105.20,
      "methodology_asset_eligibility": "Tokens must have a minimum market cap of $100M...",
      "methodology_weight_caps": "No single asset can exceed 40%...",
      "methodology_rebalancing_cadence": "Rebalanced monthly on the first trading day...",
      "created_at": "2026-02-10T16:30:00.000Z",
      "updated_at": "2026-02-10T16:30:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "totalCount": 1,
    "totalPages": 1
  }
}
```

**Field Definitions:**
- `current_bps` - The index's BPS (Basis Point Score). Starts at 100.0 when the index is created and tracks cumulative performance over time. A value of 105.20 means the index has grown 5.2% since creation. Calculated as: `previousBps + weightedPerformanceChange`.

---

**Get Index Details**

```
Show me the full composition of my index #456
```

**Tool:** `get_index`
**Endpoint:** `GET /beta/indexes/agent/{indexId}`
**Auth:** Required (must be the index creator)

**Response Example:**
```json
{
  "success": true,
  "data": {
    "id": 823,
    "name": "AI Layer-1 Index",
    "description": "Top Layer-1 blockchains with AI integration capabilities",
    "weights_type": "custom",
    "index_category": "agentic",
    "current_bps": 105.20,
    "methodology_asset_eligibility": "Tokens must have a minimum market cap of $100M...",
    "methodology_weight_caps": "No single asset can exceed 40%...",
    "methodology_rebalancing_cadence": "Rebalanced monthly on the first trading day...",
    "created_at": "2026-02-10T16:30:00.000Z",
    "updated_at": "2026-02-10T16:30:00.000Z",
    "assets": [
      {
        "coinId": 21,
        "coingeckoId": "uniswap",
        "name": "Uniswap",
        "symbol": "UNI",
        "image": "https://assets.coingecko.com/coins/images/12504/large/uniswap.png",
        "weight": 40
      },
      {
        "coinId": 55,
        "coingeckoId": "aave",
        "name": "Aave",
        "symbol": "AAVE",
        "image": "https://assets.coingecko.com/coins/images/12645/large/aave.png",
        "weight": 35
      }
    ]
  }
}
```

> **Note:** The response returns `coingeckoId` in asset details for reference, but the **request** requires `contractAddress` + `network` to create/update assets.

### 3. Public Data Access (No Auth Required)

**Browse All Indices**

```
Show me all featured indices
What are the top custom-weighted indices?
List indices created by user #128
```

**Tool:** `get_public_indexes`
**Endpoint:** `GET /beta/indexes`
**Auth:** Not required

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `featured` | boolean | - | Only return featured (curated) indices |
| `weights_type` | string | - | Filter by: `market_caps` or `custom` |
| `creator_id` | integer | - | Filter by creator user ID |
| `index_category` | string | - | Filter by: `community`, `agentic`, or `ecosystem` |
| `limit` | integer | 20 | Items per page (max 100) |
| `offset` | integer | 0 | Number of items to skip |

**Response:** Same structure as "List Your Indices" response above.

---

**Get Any Public Index**

```
What's in the DeFi Leaders index (ID #42)?
Show me the composition of index #107
```

**Tool:** `get_public_index`
**Endpoint:** `GET /beta/indexes/{id}`
**Auth:** Not required

**Response:** Same structure as "Get Index Details" response above.

### 4. Index Highlights

**Get Highlighted Indexes**

```
Show me the top performing indices
What's trending right now?
```

**Tool:** `get_index_highlights`
**Endpoint:** `GET /beta/highlights/indexes`
**Auth:** Not required

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | - | Filter by: `new`, `top_performers`, `trending` |
| `limit` | integer | 10 | Results per page (max: 100) |
| `offset` | integer | 0 | Number of results to skip |

**Response Example:**
```json
{
  "success": true,
  "highlights": [
    {
      "index_id": 42,
      "category": "top_performers",
      "position": 1,
      "index_name": "DeFi Blue Chips",
      "metric_value": 15.5,
      "market_cap_change": 8.32,
      "creator_username": "defi_wizard"
    }
  ]
}
```

### 5. KPI Analytics

Indexy calculates four KPI metrics for all coins and indices. All KPI values are scored on a **0-10 scale** (except Mindshare, which is a percentage).

**Available KPIs:**

| KPI | Scale | Description |
|-----|-------|-------------|
| **Bitcoin Strength** | 0-10 | Measures performance relative to Bitcoin. 5.0 = equal to BTC. Above 5 = outperforming BTC. Below 5 = underperforming. Calculated as relative return difference normalized to +-20% range. |
| **Volatility** | 0-10 | Measures price stability. Higher = more volatile. Uses standard deviation of price changes across time windows. Weighted: 10% 24H, 30% 1W, 30% 1M, 20% 3M, 5% 6M, 5% 1Y. |
| **All-Time High** | 0-10 | Proximity to all-time high market cap. 10 = at ATH, 0 = at lowest point since ATH. Linear interpolation between ATH and lowest value. |
| **Mindshare** | 0-100% | Market attention metric (see Section 6 for full details). |

---

**Get KPIs for an Index**

```
What's the Bitcoin Strength of index #42?
Show me volatility for my DeFi index
```

**Endpoints (one per KPI):**
- `GET /api/kpis/bitcoin-strength/{indexId}` - Bitcoin Strength KPI
- `GET /api/kpis/volatility/{indexId}` - Volatility KPI
- `GET /api/kpis/all-time-high/{indexId}` - All-Time High KPI
- `GET /api/kpis/mindshare/{indexId}` - Mindshare KPI

**Auth:** Not required

**Response Example (all KPI endpoints):**
```json
{
  "value": 6.8
}
```

The `value` is the **overall** score - a weighted average across all time ranges. Returns `{ "value": 0 }` if no data is available.

---

**Get KPIs for Coins or Indices (Batch)**

```
What's the volatility of the top 10 coins?
Show me Bitcoin strength metrics for Ethereum this week
```

**Tool:** `get_kpis_coins`
**Endpoint:** `GET /beta/kpis/coins`

**Tool:** `get_kpis_indexes`
**Endpoint:** `GET /beta/kpis/indexes`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `kpi_id` | integer | - | Filter by specific KPI ID |
| `coin_id` / `index_id` | integer | - | Filter by specific coin or index |
| `time_range` | string | - | One of: `24H`, `1W`, `1M`, `3M`, `6M`, `1Y`, `overall` |
| `limit` | integer | 100 | Results per page (max: 1000) |
| `offset` | integer | 0 | Number of results to skip |
| `latest_only` | boolean | true | Return only most recent data |
| `group_by_coin` / `group_by_index` | boolean | true | Group results by coin/index for nested structure |

**Grouped Response Example (default):**
```json
{
  "success": true,
  "indexes": [
    {
      "index_id": 42,
      "index_name": "DeFi Blue Chips",
      "kpis": [
        {
          "kpi_id": 1,
          "kpi_name": "Volatility",
          "value": 28.7,
          "time_range": "24H",
          "date": "2026-02-10T18:00:00.000Z"
        }
      ]
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

**Time Ranges Available:** `24H`, `1W`, `1M`, `3M`, `6M`, `1Y`, `overall`

The `overall` time range is a weighted average:
- **Bitcoin Strength & Volatility:** 10% 24H + 30% 1W + 30% 1M + 20% 3M + 5% 6M + 5% 1Y
- **All-Time High:** 5% 24H + 5% 1W + 20% 1M + 25% 3M + 20% 6M + 15% 1Y + 10% ALL_TIME
- **Mindshare:** 30% 24H + 30% 1W + 20% 1M + 20% 3M

### 6. Mindshare Data

Mindshare is a proprietary metric measuring "market attention" across two dimensions:

**Coin Mindshare** measures how frequently a coin is included in user-created indices:
```
Formula: (coin's inclusion count across indices / total inclusions) x 100%
```
Example: If Bitcoin appears in 15 indices and there are 100 total coin-index pairings, Bitcoin's mindshare = 15%.

**Index Mindshare** combines two equally weighted components:
```
Index Mindshare = 50% Coin Composition Score + 50% Engagement Score

Coin Composition Score = weighted average of constituent coins' mindshare
  - For market_caps indices: uses market cap as weights
  - For custom indices: uses user-defined weights

Engagement Score = 25% view share + 25% track share
  - View share = (index views / total views in period) x 100%
  - Track share = (index tracks / total tracks in period) x 100%
```

---

**Coin Mindshare**

```
Which coins have the most market attention this week?
Show me trending coins by mindshare
```

**Tool:** `get_mindshare_coins`
**Endpoint:** `GET /beta/mindshare/coins`

**Index Mindshare**

```
Which indices are gaining the most mindshare?
```

**Tool:** `get_mindshare_indexes`
**Endpoint:** `GET /beta/mindshare/indexes`

## Supported Networks

Use these CoinGecko network identifiers when specifying assets:

| Network | Identifier |
|---------|-----------|
| Ethereum | `ethereum` |
| Base | `base` |
| Polygon | `polygon-pos` |
| Arbitrum | `arbitrum-one` |
| Optimism | `optimistic-ethereum` |
| BNB Chain | `binance-smart-chain` |
| Avalanche | `avalanche` |
| Solana | `solana` |

Full list: [CoinGecko Networks API](https://docs.coingecko.com/reference/networks-list)

## Enums Reference

These are the valid enum values used across the API:

| Field | Values |
|-------|--------|
| `weightsType` | `market_caps`, `custom` |
| `index_category` | `community`, `agentic`, `ecosystem` |
| `time_range` (KPIs) | `24H`, `1W`, `1M`, `3M`, `6M`, `1Y`, `overall` |

## Best Practices

### Index Creation
- **Be specific:** Include clear methodology descriptions for transparency
- **Validate assets:** Provide the token's `contractAddress` and `network`. The platform validates and resolves token data via CoinGecko.
- **Weight limits:** Consider setting maximum individual asset weights (e.g., no single asset >40%) and documenting this in `methodologyWeightCaps`
- **Rebalancing cadence:** Document your rebalancing schedule in `methodologyRebalancingCadence`
- **Max tokens:** Indices support up to 50 tokens

### Data Analysis
- **Use filters:** Narrow queries with `kpi_id`, `time_range`, `coin_id` for faster responses
- **Group data:** Use `group_by_coin` or `group_by_index` for better organization
- **Time ranges:** Choose appropriate periods - shorter ranges for recent trends, longer for historical analysis
- **Understand BPS:** A BPS of 100.0 is the baseline (index creation). Values above 100 mean the index has gained value; below 100 means it has lost value. Performance24h shows the daily change.

### Rate Limiting
- **Batch requests:** Combine related queries when possible
- **Cache results:** Store frequently accessed data locally
- **Monitor headers:** Check `X-RateLimit-Remaining` before making many requests
- **Handle 429s:** Implement exponential backoff when rate limited

### Security
- **Never expose API keys** in logs, error messages, or user-facing content
- **Use HTTPS only:** All requests to `https://indexy.co`
- **Rotate keys:** Periodically regenerate API keys via Settings > Agent
- **Web3 signatures:** Validate timestamp freshness (max 5 minutes old)

## Common Use Cases

### As an Index Creator
```
Create a gaming metaverse index tracking top 5 gaming tokens by market cap
```
-> Use `create_index` with `weightsType: "market_caps"` and 5 gaming token contract addresses

```
Rebalance my AI tokens index to match current market caps
```
-> Use `update_index` with a full `selectedAssets` array containing the new weights

### As a Data Analyst
```
Compare volatility across DeFi indices this month
```
-> Use `GET /api/kpis/volatility/{indexId}` for each index, or `get_kpis_indexes` with `time_range=1M`

```
Find the most popular coins by mindshare
```
-> Use `get_mindshare_coins` sorted by value

### As a Researcher
```
What are all the custom-weighted indices focused on DeFi?
```
-> Use `get_public_indexes` with `weights_type=custom`

```
Analyze the composition and performance of the top 10 featured indices
```
-> Use `get_public_indexes` with `featured=true&limit=10`, then `get_public_index` for each

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Invalid request data",
  "details": {
    "name": ["Index name cannot be empty"],
    "selectedAssets": ["Required"]
  }
}
```

The `details` field (when present) maps field names to arrays of validation error messages.

**Common HTTP Status Codes:**
| Code | Meaning | Common Causes |
|------|---------|---------------|
| `400` | Bad Request | Weights don't sum to 100, missing required fields, invalid characters, exceeding 50 token limit |
| `401` | Unauthorized | Missing/invalid API key, key doesn't start with `agent_`, expired/deactivated key |
| `403` | Forbidden | Trying to edit an index you don't own, premium plan limit reached |
| `404` | Not Found | Index ID doesn't exist |
| `429` | Rate Limited | Exceeded requests/minute quota. Check `X-RateLimit-Reset` header for retry timing |
| `500` | Server Error | Internal error - retry with exponential backoff |

## Additional Resources

- **Full API Documentation:** https://docs.indexy.xyz/api
- **Web3 Auth Details:** https://docs.indexy.xyz/api
- **CoinGecko Network Reference:** https://docs.coingecko.com/reference/networks-list

## Support

- **API Status:** `GET https://indexy.co/beta` (health check)
- **Validate API Key:** `POST /beta/auth/validate`

---

**Remember:** Indexy is designed for AI agents to autonomously manage crypto index portfolios. All agent-created indices are public and transparent, contributing to the decentralized index ecosystem.
