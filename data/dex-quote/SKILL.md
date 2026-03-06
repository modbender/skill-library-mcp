---
name: okx-dex-quote
description: >
  Fetch optimal swap quotes from OKX DEX Aggregator API (v6). Use this skill when a user wants to:
  1. Get the best price for swapping tokens on any supported EVM/Solana chain
  2. Compare DEX routing paths and price impact for token swaps
  3. Build applications or scripts that query real-time DEX aggregator pricing
  Core value: Generates correct, authenticated API calls with proper token decimals,
  amount formatting, HMAC-SHA256 signing, and comprehensive error handling.
version: 1.0.0
allowed_tools: [bash_tool, create_file, str_replace, view]
required_context: [api_key, secret_key, passphrase]
license: MIT
author: Claude Assistant
tags: [defi, dex, okx, swap, quote, web3, aggregator, evm, solana]
---

# OKX DEX Aggregator Quote Skill

## Overview

This skill generates production-ready code for fetching optimal swap quotes from the **OKX DEX Aggregator API v6**. The API finds the best price across multiple DEX protocols (Uniswap, SushiSwap, Curve, etc.) and returns detailed routing information including price impact, gas estimates, and token safety flags.

**Key capabilities:**
- Authenticated API requests with HMAC-SHA256 signing
- Correct handling of token decimals and amount formatting
- Support for `exactIn` (fixed input) and `exactOut` (fixed output) swap modes
- Multi-chain support (Ethereum, BSC, Arbitrum, Base, Solana, and 20+ chains)
- Price impact protection and honeypot detection
- Fee/commission splitting configuration

## Prerequisites

### Required Credentials
Users must have an OKX Web3 API key set. The skill needs three values:
- `OKX_ACCESS_KEY` — API key
- `OKX_SECRET_KEY` — Secret key for HMAC signing
- `OKX_PASSPHRASE` — Account passphrase

### Environment
- **Python**: `requests`, `hmac`, `hashlib`, `base64`, `datetime` (all stdlib except `requests`)
- **Node.js**: `axios` or `node-fetch`, built-in `crypto`
- No additional blockchain dependencies required (this is a read-only quote endpoint)

### API Endpoint
```
GET https://web3.okx.com/api/v6/dex/aggregator/quote
```

## Workflow

### Step 1: Validate User Input

Before constructing the API call, validate:

1. **Chain ID (`chainIndex`)** — Must be a supported chain. Common values:
   - `1` = Ethereum
   - `56` = BSC
   - `137` = Polygon
   - `42161` = Arbitrum
   - `8453` = Base
   - `130` = Unichain
   - `501` = Solana

2. **Token addresses** — Must be valid contract addresses or the native token placeholder:
   - Native tokens (ETH, BNB, etc.): `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`
   - Contract tokens: Full 42-character hex address (EVM) or base58 (Solana)

3. **Amount** — MUST include token decimals. This is the #1 source of errors:
   - 1 ETH (18 decimals) → `"1000000000000000000"`
   - 1 USDT (6 decimals) → `"1000000"`
   - 1 WBTC (8 decimals) → `"100000000"`
   - Formula: `amount_raw = human_amount * (10 ** token_decimals)`

4. **Swap mode** — `exactIn` (default) or `exactOut`
   - `exactOut` only supported on: Ethereum, Base, BSC, Arbitrum
   - `exactOut` only works with Uniswap V2/V3 pools

### Step 2: Construct Authentication Headers

OKX API requires HMAC-SHA256 signed requests with 4 headers:

```
OK-ACCESS-KEY: <api_key>
OK-ACCESS-SIGN: <hmac_signature>
OK-ACCESS-PASSPHRASE: <passphrase>
OK-ACCESS-TIMESTAMP: <iso8601_timestamp>
```

**Signing algorithm:**
```
timestamp = ISO 8601 UTC time (e.g., "2025-01-15T12:00:00.000Z")
prehash = timestamp + "GET" + request_path_with_query
signature = Base64(HMAC-SHA256(secret_key, prehash))
```

**CRITICAL**: The `request_path_with_query` must include the full path starting from `/api/...` plus the query string. Example:
```
/api/v6/dex/aggregator/quote?chainIndex=1&amount=1000000000000000000&fromTokenAddress=0xeee...&toTokenAddress=0xa0b...
```

### Step 3: Send Request and Parse Response

**Success response structure:**
```json
{
  "code": "0",
  "data": [{
    "chainIndex": "1",
    "fromToken": { "tokenSymbol": "ETH", "decimal": "18", ... },
    "toToken": { "tokenSymbol": "USDC", "decimal": "6", ... },
    "fromTokenAmount": "1000000000000000000",
    "toTokenAmount": "3521432100",
    "dexRouterList": [...],
    "tradeFee": "2.45",
    "estimateGasFee": "150000",
    "priceImpactPercent": "-0.12"
  }],
  "msg": ""
}
```

**Key fields to extract:**
- `toTokenAmount` — The amount you'll receive (in raw units with decimals)
- `tradeFee` — Estimated network fee in USD
- `priceImpactPercent` — Negative = losing value; large negative = danger
- `dexRouterList` — Routing path through various DEX protocols
- `fromToken.isHoneyPot` / `toToken.isHoneyPot` — Scam token flag
- `fromToken.taxRate` / `toToken.taxRate` — Token buy/sell tax

### Step 4: Format Output for User

Convert raw amounts back to human-readable:
```
human_amount = raw_amount / (10 ** decimal)
```

Always display:
1. Exchange rate (e.g., "1 ETH = 3,521.43 USDC")
2. Price impact percentage with warning if > 3%
3. Estimated gas fee in USD
4. Routing summary (which DEXes are used)
5. Honeypot warnings if detected
6. Token tax rates if > 0

## Best Practices

### Security
- **NEVER hardcode API credentials** in generated code. Always use environment variables or config files.
- **NEVER log the secret key or signature** in debug output.
- Validate all token addresses against expected format before sending.
- Check `isHoneyPot` flag on both tokens and warn the user prominently.

### Amount Handling
- **Always use string type** for amounts to avoid floating-point precision loss.
- Python: Use `int()` for amount calculations, never `float()`.
- JavaScript: Use `BigInt` or string math for amounts > 2^53.
- When user provides a human-readable amount like "1.5 ETH", convert: `str(int(1.5 * 10**18))`.

### Error Handling
- Check `response["code"] == "0"` before accessing data.
- Common error codes:
  - Non-zero code with `msg` = API error (e.g., insufficient liquidity, invalid params)
  - HTTP 401 = Authentication failure (check signature algorithm)
  - HTTP 429 = Rate limited
- If `priceImpactPercent` is `null`, warn that price impact couldn't be calculated.

### Rate Limits
- Respect OKX rate limits. For production use, implement exponential backoff.
- Cache quotes if polling repeatedly (quotes are valid for ~15-30 seconds).

### Optional Parameters Usage
- `dexIds` — Use when you want to restrict to specific DEXes (e.g., only Uniswap).
- `directRoute=true` — Only for Solana; forces single-pool routing.
- `priceImpactProtectionPercent` — Set to a sensible default like `10` for safety. Set to `100` to disable.
- `feePercent` — For integrators taking commission. Max 3% (EVM) or 10% (Solana). Up to 9 decimal places.

## Examples

### Example 1: Python — Get ETH to USDC Quote on Ethereum

```python
import os, hmac, hashlib, base64, requests
from datetime import datetime, timezone
from urllib.parse import urlencode

API_KEY = os.environ["OKX_ACCESS_KEY"]
SECRET_KEY = os.environ["OKX_SECRET_KEY"]
PASSPHRASE = os.environ["OKX_PASSPHRASE"]

def get_okx_quote(chain_index, from_token, to_token, amount, swap_mode="exactIn"):
    base_url = "https://web3.okx.com"
    path = "/api/v6/dex/aggregator/quote"

    params = {
        "chainIndex": chain_index,
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": amount,
        "swapMode": swap_mode,
    }

    query_string = urlencode(params)
    request_path = f"{path}?{query_string}"

    # Generate timestamp and signature
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    prehash = timestamp + "GET" + request_path
    signature = base64.b64encode(
        hmac.new(SECRET_KEY.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "OK-ACCESS-TIMESTAMP": timestamp,
    }

    resp = requests.get(base_url + request_path, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    if data["code"] != "0":
        raise Exception(f"OKX API error: {data['msg']}")

    return data["data"][0]


# Swap 1 ETH -> USDC on Ethereum
ETH = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
amount = str(1 * 10**18)  # 1 ETH in wei

quote = get_okx_quote("1", ETH, USDC, amount)

to_decimals = int(quote["toToken"]["decimal"])
received = int(quote["toTokenAmount"]) / (10 ** to_decimals)

print(f"You will receive: {received:,.2f} {quote['toToken']['tokenSymbol']}")
print(f"Price impact: {quote['priceImpactPercent']}%")
print(f"Gas fee (USD): ${quote['tradeFee']}")
print(f"Honeypot check: {'WARNING' if quote['toToken']['isHoneyPot'] else 'Safe'}")
```

### Example 2: Node.js — Get Quote with Commission Fee

```javascript
const crypto = require("crypto");
const https = require("https");

const API_KEY = process.env.OKX_ACCESS_KEY;
const SECRET_KEY = process.env.OKX_SECRET_KEY;
const PASSPHRASE = process.env.OKX_PASSPHRASE;

function getQuote(chainIndex, fromToken, toToken, amount, options = {}) {
  const params = new URLSearchParams({
    chainIndex,
    fromTokenAddress: fromToken,
    toTokenAddress: toToken,
    amount,
    swapMode: options.swapMode || "exactIn",
    ...(options.feePercent && { feePercent: options.feePercent }),
    ...(options.priceImpactProtectionPercent && {
      priceImpactProtectionPercent: options.priceImpactProtectionPercent,
    }),
  });

  const path = `/api/v6/dex/aggregator/quote?${params}`;
  const timestamp = new Date().toISOString();
  const prehash = timestamp + "GET" + path;
  const signature = crypto
    .createHmac("sha256", SECRET_KEY)
    .update(prehash)
    .digest("base64");

  return new Promise((resolve, reject) => {
    const req = https.get(
      `https://web3.okx.com${path}`,
      {
        headers: {
          "OK-ACCESS-KEY": API_KEY,
          "OK-ACCESS-SIGN": signature,
          "OK-ACCESS-PASSPHRASE": PASSPHRASE,
          "OK-ACCESS-TIMESTAMP": timestamp,
        },
      },
      (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          const data = JSON.parse(body);
          if (data.code !== "0") reject(new Error(`OKX: ${data.msg}`));
          else resolve(data.data[0]);
        });
      }
    );
    req.on("error", reject);
  });
}
```

### Example 3: Understanding the Routing Path

```
Router: ETH -> WBTC -> USDC
dexRouterList shows:
  - 55% ETH -> WBTC via Uniswap V4
  - 30% ETH -> USDC via Uniswap V4 (direct)
  - WBTC -> USDC via Euler (73%) + Uniswap V4 (27%)

This means the aggregator splits the trade across multiple paths
to minimize price impact and maximize output.
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `401 Unauthorized` | Signature mismatch | Verify prehash string is exactly `timestamp + "GET" + full_path_with_query`. Check secret key encoding. |
| Amount too small | Missing decimal conversion | Multiply human amount by `10 ** token_decimals`. 1 USDT = `1000000`, not `1`. |
| Invalid token address | Wrong chain/address combo | Verify the token exists on the specified chain. Use native token placeholder for ETH/BNB/etc. |
| `priceImpactPercent` very negative (< -10%) | Low liquidity or large trade | Reduce trade size or split across multiple transactions. |
| `isHoneyPot: true` | Scam token detected | **Do NOT proceed with the swap.** Warn the user immediately. |
| `exactOut` not working | Unsupported chain/protocol | Only works on Ethereum, Base, BSC, Arbitrum with Uniswap V2/V3. |
| `taxRate > 0` | Token has built-in tax | Factor tax into expected output. E.g., 5% tax means receiving 5% less. |
| Empty `dexRouterList` | No liquidity path found | Try a different token pair, smaller amount, or different chain. |
| `code` is non-zero | General API error | Read `msg` field for details. Common: rate limit, maintenance, invalid params. |

## Reference: Common Chain IDs

| Chain | chainIndex |
|-------|-----------|
| Ethereum | 1 |
| BSC | 56 |
| Polygon | 137 |
| Arbitrum | 42161 |
| Optimism | 10 |
| Avalanche | 43114 |
| Base | 8453 |
| Solana | 501 |
| Unichain | 130 |

## Reference: Common Token Addresses (Ethereum)

| Token | Address | Decimals |
|-------|---------|----------|
| ETH (native) | `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` | 18 |
| USDT | `0xdac17f958d2ee523a2206206994597c13d831ec7` | 6 |
| USDC | `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48` | 6 |
| WETH | `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` | 18 |
| WBTC | `0x2260fac5e5542a773aa44fbcfedf7c193bc2c599` | 8 |
| DAI | `0x6b175474e89094c44da98b954eedeac495271d0f` | 18 |

## Reference: Request Parameters Summary

| Parameter | Required | Description |
|-----------|----------|-------------|
| `chainIndex` | Yes | Chain ID (e.g., `1` for Ethereum) |
| `amount` | Yes | Amount in raw units (with decimals) |
| `swapMode` | Yes | `exactIn` or `exactOut` |
| `fromTokenAddress` | Yes | Sell token contract address |
| `toTokenAddress` | Yes | Buy token contract address |
| `dexIds` | No | Comma-separated DEX IDs to restrict routing |
| `directRoute` | No | `true` for single-pool only (Solana only) |
| `priceImpactProtectionPercent` | No | Max allowed price impact 0-100 (default 90) |
| `feePercent` | No | Commission fee percentage for integrators |
