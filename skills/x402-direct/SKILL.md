---
name: x402-direct
description: Discover and search x402-enabled services via the x402.direct directory API. Use when an agent needs to find paid API services that accept x402 payments, browse the x402 ecosystem, look up service details, check trust scores, or search for specific capabilities (AI, image, weather, search, data, audio, video, developer, finance, language, storage). Triggers on "find x402 service", "x402 directory", "search x402", "x402 API", "paid API search", "x402.direct", agent-to-agent payments, crypto-native API discovery.
---

# x402.direct -- Service Directory

The x402.direct API is a directory of x402-enabled services. It indexes services that accept x402 payments (HTTP 402 + crypto) and provides search, browsing, and trust scoring.

Base URL: `https://x402.direct`

## Endpoints

### 1. Search (Paid -- $0.001 via x402)

```
GET /api/search?q=<query>
```

Full-text search across all indexed services. Results ranked by blended text relevance + trust score. Protected by x402 middleware -- first request returns HTTP 402, re-send with payment proof.

**Parameters:**

| Param    | Type    | Required | Description                          |
|----------|---------|----------|--------------------------------------|
| q        | string  | yes      | Search query (max 500 chars)         |
| category | string  | no       | Filter by category                   |
| network  | string  | no       | Filter by blockchain network         |
| maxPrice | string  | no       | Max price in atomic units (bigint)   |
| minScore | integer | no       | Minimum trust score (0-100)          |
| limit    | integer | no       | Max results (default 20, max 50)     |

**Example:**

```bash
curl "https://x402.direct/api/search?q=weather+api&minScore=60&limit=5"
```

**Response shape:**

```json
{
  "query": "weather api",
  "count": 3,
  "results": [
    {
      "id": 42,
      "resourceUrl": "https://example.com/api/weather",
      "description": "Real-time weather data for any location",
      "category": "weather",
      "provider": "example.com",
      "network": "base-mainnet",
      "price": "1000",
      "priceUsd": "0.001",
      "scoutScore": 85,
      "scoutVerdict": "safe",
      "relevance": 0.3214,
      "score": 58.11
    }
  ]
}
```

**x402 payment flow:**

1. Send GET to `/api/search?q=...` with no payment header.
2. Server returns HTTP 402 with payment details in the response body (price, network, payTo address, facilitator URL).
3. Pay $0.001 USDC on Base (via agent wallet or Coinbase Agentic Wallet).
4. Re-send the same request with `X-402-Payment: <proof>` header.
5. Server verifies payment via facilitator and returns search results.

If using an x402-aware HTTP client (e.g., `x402` npm package), the payment is handled automatically:

```typescript
import { createX402Client } from "x402";
const client = createX402Client({ wallet: agentWallet });
const resp = await client.fetch("https://x402.direct/api/search?q=weather+api");
```

### 2. Browse Services (Free)

```
GET /api/services
```

Paginated list of all indexed services. No payment required.

**Parameters:**

| Param    | Type    | Default | Description                          |
|----------|---------|---------|--------------------------------------|
| page     | integer | 1       | Page number                          |
| limit    | integer | 50      | Results per page (max 100)           |
| category | string  | --      | Filter by category                   |
| network  | string  | --      | Filter by network                    |
| sort     | string  | score   | Sort: `score`, `newest`, `price`     |
| minScore | integer | --      | Minimum trust score (0-100)          |

**Examples:**

```bash
# Top-rated AI services
curl "https://x402.direct/api/services?category=ai&sort=score&limit=10"

# Newest services on Base mainnet
curl "https://x402.direct/api/services?network=base-mainnet&sort=newest"

# Only high-trust services
curl "https://x402.direct/api/services?minScore=70&sort=score"
```

**Response shape:**

```json
{
  "services": [
    {
      "id": 1,
      "resourceUrl": "https://example.com/api/generate",
      "type": "x402",
      "description": "AI text generation endpoint",
      "category": "ai",
      "provider": "example.com",
      "network": "base-mainnet",
      "scheme": "exact",
      "price": "5000",
      "priceUsd": "0.005",
      "scoutScore": 92,
      "scoutVerdict": "safe",
      "lastSeen": "2025-05-01T12:00:00.000Z",
      "createdAt": "2025-04-15T08:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 127,
    "totalPages": 3
  }
}
```

### 3. Service Details (Free)

```
GET /api/services/:id
```

Full details for a single service including payment options, raw metadata, and facilitator info.

**Example:**

```bash
curl "https://x402.direct/api/services/42"
```

**Response shape:**

```json
{
  "id": 42,
  "resourceUrl": "https://example.com/api/weather",
  "type": "x402",
  "x402Version": "1",
  "description": "Real-time weather data for any location",
  "mimeType": "application/json",
  "category": "weather",
  "provider": "example.com",
  "network": "base-mainnet",
  "scheme": "exact",
  "price": "1000",
  "priceUsd": "0.001",
  "payTo": "0xAbC123...",
  "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "scoutScore": 85,
  "scoutVerdict": "safe",
  "accepts": [{"scheme": "exact", "network": "base-mainnet", "maxAmountRequired": "1000", "asset": "..."}],
  "metadata": {"description": "...", "mimeType": "application/json"},
  "lastSeen": "2025-05-01T12:00:00.000Z",
  "lastUpdated": "2025-05-01T12:00:00.000Z",
  "createdAt": "2025-04-15T08:00:00.000Z",
  "facilitator": {
    "name": "x402.org",
    "url": "https://x402.org/facilitator",
    "facilitatorId": "x402-org-mainnet"
  }
}
```

### 4. Ecosystem Stats (Free)

```
GET /api/stats
```

High-level directory statistics. Good for dashboards or understanding the ecosystem at a glance.

**Example:**

```bash
curl "https://x402.direct/api/stats"
```

**Response shape:**

```json
{
  "services": 247,
  "providers": 38,
  "categories": 12,
  "facilitators": 3,
  "avgScoutScore": 62,
  "networks": [
    { "network": "base-mainnet", "count": 180 },
    { "network": "base-sepolia", "count": 45 },
    { "network": "polygon", "count": 15 },
    { "network": "solana", "count": 7 }
  ]
}
```

## Filter Values

**Categories:** `ai`, `image`, `weather`, `search`, `data`, `audio`, `video`, `developer`, `finance`, `language`, `storage`, `other`

**Networks:** `base-mainnet`, `base-sepolia`, `polygon`, `solana` (more may appear as the ecosystem grows)

**Sort options:** `score` (trust score, default), `newest` (creation date), `price` (cheapest first)

## Trust Score (ScoutScore)

Every service is scored 0-100 based on automated trust signals:

- HTTPS transport security
- Mainnet vs testnet deployment
- Domain uniqueness and provider reputation
- Description quality and documentation
- Pricing reasonableness
- Valid payment address
- Custom domain (not generic hosting)

**Verdicts:**

| Score Range | Verdict   | Meaning                                |
|-------------|-----------|----------------------------------------|
| 70-100      | `safe`    | Well-documented, mainnet, custom domain |
| 40-69       | `caution` | Some trust signals missing              |
| 0-39        | `avoid`   | Missing critical trust signals          |

**Recommendation:** Use `minScore=60` or higher when searching for production-ready services. Use `minScore=0` only when exploring or debugging.

## Usage Patterns

**Find a service for a specific task:**

```bash
# Agent needs image generation
curl "https://x402.direct/api/services?category=image&sort=score&minScore=60&limit=5"
```

**Search with specific capability in mind (paid):**

```bash
curl "https://x402.direct/api/search?q=text+to+speech&minScore=70" \
  -H "X-402-Payment: <proof>"
```

**Get full details before calling a service:**

```bash
# Found service ID 42 from browse/search, now get payment details
curl "https://x402.direct/api/services/42"
# Use the payTo, asset, network, and price fields to construct the x402 payment
```

**Check ecosystem health:**

```bash
curl "https://x402.direct/api/stats"
```

## Decision Guide

| Goal                              | Endpoint          | Cost  |
|-----------------------------------|-------------------|-------|
| Browse by category/network        | `/api/services`   | Free  |
| Get service payment details       | `/api/services/:id` | Free |
| Natural language search           | `/api/search`     | $0.001 |
| Ecosystem overview                | `/api/stats`      | Free  |

Prefer `/api/services` with filters when the category is known. Use `/api/search` when the agent needs semantic/keyword matching across descriptions and providers.
