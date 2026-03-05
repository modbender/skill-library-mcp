# x402 Payment Integration (v2)

## What is x402?

An open payment protocol by Coinbase that uses HTTP 402 status codes for pay-per-request API access. Agents pay with USDC on Base — no accounts, API keys, or subscriptions needed.

- **Spec**: https://www.x402.org
- **Docs**: https://docs.cdp.coinbase.com/x402/welcome
- **GitHub**: https://github.com/coinbase/x402
- **Migration v1 to v2**: https://docs.cdp.coinbase.com/x402/migration-guide

## How It Works (v2)

```
1. Agent sends HTTP request to a service
2. Server responds: 402 Payment Required
   → PAYMENT-REQUIRED header contains price, token, network (CAIP-2), payTo address
3. Agent signs a USDC payment authorization (EIP-712 / EIP-3009)
4. Agent retries request with PAYMENT-SIGNATURE header
5. Server verifies payment via facilitator → returns resource
   → PAYMENT-RESPONSE header contains settlement proof
```

No actual transaction is broadcast by the agent — only a signed authorization. The facilitator settles on-chain.

### v2 Header Changes (from v1)

| Purpose | v1 (deprecated) | v2 (current) |
|---------|-----------------|--------------|
| Client → Server (payment) | `X-PAYMENT` | `PAYMENT-SIGNATURE` |
| Server → Client (response) | `X-PAYMENT-RESPONSE` | `PAYMENT-RESPONSE` |
| Server → Client (requirements) | (in body) | `PAYMENT-REQUIRED` |
| Network format | String (`base`) | CAIP-2 (`eip155:8453`) |

## Recommended Facilitator

Use the **World.fun facilitator** for Base and Ethereum — fee-free, no API keys required:

```
https://facilitator.world.fun
```

Endpoints:
- `POST /verify` — verify x402 payment signatures
- `POST /settle` — settle x402 payments on-chain
- `GET /supported` — list supported networks and tokens

Other facilitator options:
- **CDP Facilitator** (Coinbase): `https://x402-facilitator.cdp.coinbase.com` — requires CDP API keys, supports Base + Solana
- **x402.org Facilitator**: `https://x402.org/facilitator` — community-operated

## Setup (Node.js) — v2

### Install

```bash
npm install @x402/axios @x402/evm @x402/core
```

### Basic Client (v2)

```javascript
import { x402Client, wrapAxiosWithPayment } from "@x402/axios";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";
import axios from "axios";

// Load private key from credentials
const signer = privateKeyToAccount(process.env.EVM_PRIVATE_KEY);

// Create x402 v2 client and register EVM scheme
const client = new x402Client();
registerExactEvmScheme(client, { signer });

// Wrap axios — automatically handles PAYMENT-REQUIRED / PAYMENT-SIGNATURE
const api = wrapAxiosWithPayment(axios.create(), client);

// Any 402 response is handled automatically
const response = await api.get("https://some-x402-service.com/api/data");
```

### Using fetch wrapper (v2)

```bash
npm install @x402/fetch @x402/evm
```

```javascript
import { x402Client, x402Fetch } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const signer = privateKeyToAccount(process.env.EVM_PRIVATE_KEY);
const client = new x402Client();
registerExactEvmScheme(client, { signer });

const fetch402 = x402Fetch(client);
const response = await fetch402("https://some-x402-service.com/api/data");
```

## Setup (Python) — v2

```bash
pip install x402
```

```python
import asyncio
from eth_account import Account
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact import register_exact_evm_client
from x402.http import x402Client
from x402.http.clients import x402HttpxClient

async def main():
    account = Account.from_key(EVM_PRIVATE_KEY)
    client = x402Client()
    register_exact_evm_client(client, EthAccountSigner(account))

    async with x402HttpxClient(client) as http:
        response = await http.get("https://some-x402-service.com/api/data")
        print(response.text)

asyncio.run(main())
```

For synchronous usage:

```python
from x402.http.clients import x402_requests

session = x402_requests(client)
response = session.get("https://some-x402-service.com/api/data")
```

## Seller-Side Setup (serving x402 endpoints)

If your agent also wants to **sell** services via x402, use the World.fun facilitator:

```javascript
import express from "express";
import { paymentMiddleware } from "@x402/express";

const app = express();

app.use(paymentMiddleware({
  "GET /api/data": {
    accepts: [{
      scheme: "exact",
      network: "eip155:8453",           // Base mainnet (CAIP-2)
      maxAmountRequired: "1000",         // in USDC smallest unit (6 decimals)
      resource: "https://youragent.com/api/data",
      payTo: "0xYourAgentAddress",
      asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", // USDC on Base
      maxTimeoutSeconds: 60,
    }],
  },
}, { facilitatorUrl: "https://facilitator.world.fun" }));
```

## Budget Controls

Implement spending limits to prevent runaway costs:

```javascript
// Track cumulative spend in credentials file
// Before each payment, check against daily limit
const MAX_DAILY_SPEND_USD = 1.0;
```

## Requirements

- **USDC on Base**: The agent wallet must hold USDC on Base mainnet
- **USDC contract (Base)**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Typical API costs: $0.001 - $0.01 per request

## Discovering x402 Services

- **x402 Bazaar**: `curl https://bazaar.x402.org/api/listings`
- **x402 Ecosystem**: https://www.x402.org/ecosystem

## Supported Networks

| Network | CAIP-2 ID | Status |
|---------|-----------|--------|
| Base | `eip155:8453` | Primary (recommended) |
| Ethereum | `eip155:1` | Supported |
| Solana | `solana:mainnet` | Supported (requires SVM signer) |

## v2 Package Reference

| Package | Purpose |
|---------|---------|
| `@x402/core` | Core protocol types and utilities |
| `@x402/evm` | EVM chain support (Base, Ethereum, etc.) |
| `@x402/svm` | Solana chain support |
| `@x402/axios` | Axios wrapper for buyers |
| `@x402/fetch` | Fetch wrapper for buyers |
| `@x402/express` | Express middleware for sellers |
| `@x402/next` | Next.js middleware for sellers |
| `@x402/hono` | Hono middleware for sellers |
| `@coinbase/x402` | CDP facilitator config |
