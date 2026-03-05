---
name: orthogonal
version: 1.0.0
description: Orthogonal API Platform - Access 100+ premium APIs using the SDK, Run API, or x402 direct payment. Search, discover, and integrate APIs with simple tool calls.
homepage: https://orthogonal.com
---

# Orthogonal Platform

Orthogonal is a platform for monetizing and consuming APIs. Use these tools to discover, understand, and call any API on the platform.

**Base URL**: `https://api.orth.sh/v1`

## Authentication

Get your API key at https://orthogonal.com/dashboard/settings

```bash
export ORTHOGONAL_API_KEY=orth_live_your_api_key
```

## Tools

### 1. search

Search for APIs using natural language. Returns a lightweight list of matching endpoints.

**Endpoint**: `POST /v1/search`

```bash
curl -X POST 'https://api.orth.sh/v1/search' \
  -H 'Authorization: Bearer $ORTHOGONAL_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "scrape websites", "limit": 10}'
```

**Parameters**:
- `prompt` (string, required): Natural language description of what you're looking for
- `limit` (number, optional): Max results (default: 10, max: 50)

**Response**: List of matching APIs with endpoints (name, description, method, path, price)

---

### 2. get_details

Get full details about a specific endpoint including all parameters.

**Endpoint**: `POST /v1/details`

```bash
curl -X POST 'https://api.orth.sh/v1/details' \
  -H 'Authorization: Bearer $ORTHOGONAL_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"api": "olostep", "path": "/v1/scrapes"}'
```

**Parameters**:
- `api` (string, required): API slug from search results (e.g., "olostep", "linkup")
- `path` (string, required): Endpoint path from search results (e.g., "/v1/scrapes")

**Response**: Full endpoint details including:
- Path parameters
- Query parameters (name, type, required, description)
- Body parameters (name, type, required, description)
- Pricing information
- Documentation URL

---

### 3. integrate

Get ready-to-use code snippets for integrating an endpoint.

**Endpoint**: `POST /v1/integrate`

```bash
curl -X POST 'https://api.orth.sh/v1/integrate' \
  -H 'Authorization: Bearer $ORTHOGONAL_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"api": "olostep", "path": "/v1/scrapes", "format": "orth-sdk"}'
```

**Parameters**:
- `api` (string, required): API slug
- `path` (string, required): Endpoint path
- `format` (string, optional): Code format - one of:
  - `orth-sdk` (default) - Orthogonal SDK (@orth/sdk)
  - `run-api` - Direct HTTP to /v1/run
  - `x402-fetch` - x402 payment with JavaScript
  - `x402-python` - x402 payment with Python
  - `curl` - cURL command
  - `all` - All formats

**Response**: Code snippets ready to copy-paste

---

### 4. use (run)

Call an API endpoint using your Orthogonal credits.

**Endpoint**: `POST /v1/run`

```bash
curl -X POST 'https://api.orth.sh/v1/run' \
  -H 'Authorization: Bearer $ORTHOGONAL_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "api": "olostep",
    "path": "/v1/scrapes",
    "body": {
      "url_to_scrape": "https://example.com"
    }
  }'
```

**Parameters**:
- `api` (string, required): API slug
- `path` (string, required): Endpoint path
- `query` (object, optional): Query parameters
- `body` (object, optional): Request body

**Response**:
```json
{
  "success": true,
  "price": 0.01,
  "data": { /* API response */ }
}
```

---

### 5. list_all (optional)

List all discoverable APIs with their endpoints. Returns paginated APIs, each containing their endpoints. Use sparingly - prefer search for specific needs.

**Endpoint**: `GET /v1/list-endpoints`

```bash
curl 'https://api.orth.sh/v1/list-endpoints?limit=100' \
  -H 'Authorization: Bearer $ORTHOGONAL_API_KEY'
```

**Parameters**:
- `limit` (number, optional): Max APIs to return per page (default: 100, max: 500)
- `offset` (number, optional): Pagination offset for APIs

**Response**: List of APIs, each with nested endpoints array

---

## Typical Workflow

1. **Search** for what you need: `POST /v1/search` with natural language
2. **Get details** for the endpoint: `POST /v1/details` to see required params
3. **Use** the endpoint: `POST /v1/run` with the params

Or for integration:
1. **Search** → **Get details** → **Integrate** to get code snippets

## SDK Integration

For the simplest integration, use the Orthogonal SDK:

```bash
npm install @orth/sdk
```

```javascript
import Orthogonal from "@orth/sdk";

const orthogonal = new Orthogonal({
  apiKey: process.env.ORTHOGONAL_API_KEY,
});

// Search for APIs
const search = await orthogonal.search("web scraping");

// Call an API
const result = await orthogonal.run({
  api: "olostep",
  path: "/v1/scrapes",
  body: { url_to_scrape: "https://example.com" }
});
```

## x402 Direct Payment

Pay directly with USDC on Base blockchain - no API key required:

```javascript
import { wrapFetchWithPayment } from "x402-fetch";
import { privateKeyToAccount } from "viem/accounts";

const account = privateKeyToAccount(process.env.PRIVATE_KEY);
const fetchWithPayment = wrapFetchWithPayment(fetch, account);

const response = await fetchWithPayment(
  "https://x402.orth.sh/olostep/v1/scrapes",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url_to_scrape: "https://example.com" })
  }
);
```

## Support

- Documentation: https://orthogonal.com/dashboard/docs
- Browse APIs: https://orthogonal.com/discover
- Book a call: https://orthogonal.com/book
