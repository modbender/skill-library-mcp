---
name: okx-dex-market-price
description: >
  Fetch token prices from OKX DEX Market Price API (v6). Use this skill when a user wants to:
  1. Get the latest price of one or more tokens on supported EVM/Solana chains
  2. Batch query token prices (up to 100 tokens per request) for portfolios or UIs
  3. Build applications that need real-time DEX market price data
  Core value: Correct authenticated POST requests with JSON body, HMAC-SHA256 signing
  including body in prehash, and proper handling of batch request/response.
version: 1.0.0
allowed_tools: [bash_tool, create_file, str_replace, view]
required_context: [api_key, secret_key, passphrase]
license: MIT
author: Claude Assistant
tags: [defi, dex, okx, market, price, web3, token, evm, solana, batch]
---

# OKX DEX Market Price API Skill

## Overview

This skill generates production-ready code for fetching **token prices** from the **OKX DEX Market Price API v6**. The API returns the latest price for one or more tokens on a given chain. It is a **batch endpoint**: you send a list of `(chainIndex, tokenContractAddress)` and receive a list of price results.

**Key capabilities:**
- Authenticated **POST** API requests with HMAC-SHA256 signing (prehash includes request body)
- **Batch support**: 1–100 tokens per request
- Multi-chain support (Ethereum, BSC, Polygon, Arbitrum, Base, Solana, etc.)
- Response includes `time` (price timestamp in ms) and `price` (string for precision)

## Prerequisites

### Required Credentials
- `OKX_ACCESS_KEY` — API key
- `OKX_SECRET_KEY` — Secret key for HMAC signing
- `OKX_PASSPHRASE` — Account passphrase

### Environment
- **Python**: `requests`, `hmac`, `hashlib`, `base64`, `datetime`, `json` (stdlib except `requests`)
- **Node.js**: `axios` or `node-fetch`, built-in `crypto`
- No blockchain dependencies (read-only HTTP API)

### API Endpoint
```
POST https://web3.okx.com/api/v6/dex/market/price
```

## Workflow

### Step 1: Validate User Input

1. **Request body** — Must be a **JSON array** of 1–100 objects. Each object:
   - `chainIndex` (String, required): Supported chain ID, e.g. `"1"` = Ethereum, `"56"` = BSC.
   - `tokenContractAddress` (String, required): Token contract address.
     - **EVM**: 42-character hex, **all lowercase** (e.g. `0x382bb369d343125bfb2117af9c149795c6c65c50`).
     - **Native token** (ETH, BNB, etc.): use `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`.
     - Solana: base58 address.

2. **Batch size** — Between 1 and 100 (inclusive). Empty array or >100 items will result in API error.

### Step 2: Construct Authentication Headers (POST)

OKX API requires HMAC-SHA256 signed requests. For **POST**, the **body is part of the prehash**.

**Headers:**
```
Content-Type: application/json
OK-ACCESS-KEY: <api_key>
OK-ACCESS-SIGN: <hmac_signature>
OK-ACCESS-PASSPHRASE: <passphrase>
OK-ACCESS-TIMESTAMP: <iso8601_timestamp>
```

**Signing algorithm (POST):**
```
timestamp = ISO 8601 UTC (e.g. "2025-01-15T12:00:00.000Z")
request_path = "/api/v6/dex/market/price"   // no query string for this endpoint
body = exact JSON string that will be sent (e.g. '[{"chainIndex":"1","tokenContractAddress":"0x..."}]'
prehash = timestamp + "POST" + request_path + body
signature = Base64(HMAC-SHA256(secret_key, prehash))
```

**CRITICAL for POST:**
- The **body** must be the **exact** JSON string (same as sent). No extra spaces; use canonical JSON (e.g. no extra whitespace).
- Method is uppercase `"POST"`.
- Request path is **without** query string (this endpoint has no query params).

### Step 3: Send Request and Parse Response

**Request body example:**
```json
[
  { "chainIndex": "1", "tokenContractAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48" },
  { "chainIndex": "56", "tokenContractAddress": "0x382bb369d343125bfb2117af9c149795c6c65c50" }
]
```

**Success response structure:**
```json
{
  "code": "0",
  "data": [
    {
      "chainIndex": "1",
      "tokenContractAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "time": "1716892020000",
      "price": "1.00012345"
    }
  ],
  "msg": ""
}
```

**Fields:**
- `code`: `"0"` = success; non-zero = error (see `msg`).
- `data`: Array of price objects, one per requested token (order may match request).
- `chainIndex`, `tokenContractAddress`: Echo of request.
- `time`: Price timestamp in **Unix milliseconds** (string).
- `price`: Latest token price (string to preserve precision).

### Step 4: Format Output for User

- Convert `price` (string) to number only when needed for display/math to avoid precision loss.
- Use `time` for “price as of” display (e.g. convert ms to local time).
- If `code !== "0"`, surface `msg` and do not treat as success.

## Best Practices

### Security
- **Never hardcode** API credentials; use environment variables or secure config.
- **Never log** secret key or raw signature.
- Validate `tokenContractAddress` format (EVM hex length/case, Solana base58) before sending.

### POST body and signing
- Use **identical** JSON string for both signing and request body (no re-pretty-print between sign and send).
- In Python: `json.dumps(payload, separators=(',', ':'))` for deterministic output.
- In JavaScript: `JSON.stringify(payload)` — ensure no trailing spaces.

### Error handling
- Check `response["code"] == "0"` before using `data`.
- Empty or invalid `tokenParamList` (e.g. empty list or >100 items) returns param error.
- HTTP 401 = auth failure (check prehash: timestamp + "POST" + path + body).
- HTTP 429 = rate limit; implement backoff.

### Rate limits
- Respect OKX rate limits; cache prices when polling frequently.

## Examples

### Example 1: Python — Batch get token prices

```python
import os
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone

API_KEY = os.environ["OKX_ACCESS_KEY"]
SECRET_KEY = os.environ["OKX_SECRET_KEY"]
PASSPHRASE = os.environ["OKX_PASSPHRASE"]
BASE_URL = "https://web3.okx.com"
PRICE_PATH = "/api/v6/dex/market/price"

def get_prices(token_param_list):
    # 1–100 items
    if not token_param_list or len(token_param_list) > 100:
        raise ValueError("token_param_list must have 1–100 items")

    body = json.dumps(token_param_list, separators=(',', ':'))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    prehash = timestamp + "POST" + PRICE_PATH + body
    signature = base64.b64encode(
        hmac.new(SECRET_KEY.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()

    headers = {
        "Content-Type": "application/json",
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "OK-ACCESS-TIMESTAMP": timestamp,
    }
    resp = requests.post(BASE_URL + PRICE_PATH, headers=headers, data=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != "0":
        raise Exception(f"OKX API error: {data.get('msg', 'Unknown')}")
    return data.get("data", [])

# One token on Ethereum (USDC)
payload = [{"chainIndex": "1", "tokenContractAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"}]
prices = get_prices(payload)
for p in prices:
    print(f"{p['tokenContractAddress']} @ {p['time']}: {p['price']}")
```

### Example 2: Node.js — POST with body in prehash

```javascript
const crypto = require("crypto");
const https = require("https");

const API_KEY = process.env.OKX_ACCESS_KEY;
const SECRET_KEY = process.env.OKX_SECRET_KEY;
const PASSPHRASE = process.env.OKX_PASSPHRASE;
const BASE = "https://web3.okx.com";
const PATH = "/api/v6/dex/market/price";

function getPrices(tokenParamList) {
  const body = JSON.stringify(tokenParamList);
  const timestamp = new Date().toISOString();
  const prehash = timestamp + "POST" + PATH + body;
  const signature = crypto.createHmac("sha256", SECRET_KEY).update(prehash).digest("base64");

  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "OK-ACCESS-KEY": API_KEY,
      "OK-ACCESS-SIGN": signature,
      "OK-ACCESS-PASSPHRASE": PASSPHRASE,
      "OK-ACCESS-TIMESTAMP": timestamp,
    },
  };

  return new Promise((resolve, reject) => {
    const req = https.request(BASE + PATH, options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        const json = JSON.parse(data);
        if (json.code !== "0") reject(new Error(json.msg || "API error"));
        else resolve(json.data || []);
      });
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}
```

## Troubleshooting

| Problem | Cause | Solution |
|--------|-------|----------|
| 401 Unauthorized | Signature mismatch | Ensure prehash = timestamp + "POST" + path + **exact body**; same body for sign and request. |
| tokenParamList param error | Empty or >100 items | Send array with 1–100 elements. |
| Invalid token address | Wrong format or chain | EVM: 42-char hex lowercase; use native token placeholder for ETH/BNB. |
| code non-zero | API / param error | Read `msg`; check chain support and address validity. |
| Missing price for a token | Token not supported or no liquidity | API may omit or fail for that pair; check supported chains/tokens. |

## Reference: Common Chain IDs

| Chain     | chainIndex |
|----------|------------|
| Ethereum | 1          |
| BSC      | 56         |
| Polygon  | 137        |
| Arbitrum | 42161      |
| Optimism | 10         |
| Base     | 8453       |
| Solana   | 501        |
| Unichain | 130        |

## Reference: Request/Response Summary

| Item | Description |
|------|-------------|
| Method | POST |
| URL | `https://web3.okx.com/api/v6/dex/market/price` |
| Body | JSON array of `{ "chainIndex": string, "tokenContractAddress": string }`, length 1–100 |
| Success code | `"0"` |
| data[] | `chainIndex`, `tokenContractAddress`, `time` (ms string), `price` (string) |
