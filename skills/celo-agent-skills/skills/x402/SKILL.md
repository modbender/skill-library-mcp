---
name: x402
description: x402 HTTP-native payment protocol for AI agents on Celo. Use when implementing pay-per-use APIs, agent micropayments, or HTTP 402 Payment Required flows with stablecoins.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# x402: HTTP-Native Agent Payments

x402 is an open protocol that activates the HTTP 402 "Payment Required" status code, enabling AI agents and applications to make instant, permissionless micropayments using stablecoins.

## When to Use

- Implementing pay-per-use API endpoints
- Building AI agents that pay for services autonomously
- Creating micropayment flows for content or data access
- Accepting stablecoin payments without traditional payment infrastructure

## Key Benefits

| Feature | Traditional Payments | x402 |
|---------|---------------------|------|
| Setup Time | Days to weeks | Minutes |
| Settlement | 2-7 days | Sub-second on Celo |
| Fees | 2-3% + $0.30 | ~$0.001 gas |
| Minimum Payment | $0.50+ | $0.001 |
| AI Agent Support | Not possible | Native |

## Installation

```bash
npm install thirdweb
```

## Client Side (React)

Use the `useFetchWithPayment` hook for automatic payment handling:

```typescript
import { useFetchWithPayment } from "thirdweb/react";
import { createThirdwebClient } from "thirdweb";

const client = createThirdwebClient({ clientId: "your-client-id" });

function PaidAPIComponent() {
  const { fetchWithPayment, isPending } = useFetchWithPayment(client);

  const handleApiCall = async () => {
    // Automatically handles:
    // - Wallet connection prompts
    // - Payment signing
    // - Insufficient funds UI
    // - Retry logic
    const data = await fetchWithPayment(
      "https://api.example.com/paid-endpoint"
    );
    console.log(data);
  };

  return (
    <button onClick={handleApiCall} disabled={isPending}>
      {isPending ? "Processing..." : "Access Premium Content"}
    </button>
  );
}
```

## Client Side (TypeScript)

For non-React applications, use `wrapFetchWithPayment`:

```typescript
import { wrapFetchWithPayment } from "thirdweb/x402";
import { createThirdwebClient } from "thirdweb";
import { privateKeyToAccount } from "thirdweb/wallets";

const client = createThirdwebClient({ clientId: "your-client-id" });
const account = privateKeyToAccount({ client, privateKey: "0x..." });

const fetchWithPayment = wrapFetchWithPayment({
  client,
  account,
  paymentOptions: {
    maxValue: "1000000", // Max payment in base units
  },
});

// Use like regular fetch - payments handled automatically
const response = await fetchWithPayment("https://api.example.com/premium");
const data = await response.json();
```

## Server Side (Next.js)

Accept x402 payments in API endpoints:

```typescript
// app/api/premium-content/route.ts
import { settlePayment, facilitator } from "thirdweb/x402";
import { createThirdwebClient } from "thirdweb";
import { celo } from "thirdweb/chains";

const client = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY,
});

const thirdwebFacilitator = facilitator({
  client,
  serverWalletAddress: "0xYourServerWalletAddress",
});

export async function GET(request: Request) {
  const paymentData =
    request.headers.get("PAYMENT-SIGNATURE") ||
    request.headers.get("X-PAYMENT");

  const result = await settlePayment({
    resourceUrl: "https://your-api.com/premium-content",
    method: "GET",
    paymentData,
    payTo: "0xYourWalletAddress",
    network: celo, // Use Celo chain
    price: "$0.01", // Price in USD
    facilitator: thirdwebFacilitator,
    routeConfig: {
      description: "Access to premium API content",
      mimeType: "application/json",
    },
  });

  if (result.status === 200) {
    return Response.json({ data: "premium content" });
  } else {
    return Response.json(result.responseBody, {
      status: result.status,
      headers: result.responseHeaders,
    });
  }
}
```

## Server Side (Express)

```typescript
import express from "express";
import { settlePayment, facilitator } from "thirdweb/x402";
import { createThirdwebClient } from "thirdweb";
import { celo } from "thirdweb/chains";

const app = express();

const client = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY,
});

const thirdwebFacilitator = facilitator({
  client,
  serverWalletAddress: "0xYourServerWalletAddress",
});

app.get("/api/premium", async (req, res) => {
  const paymentData = req.headers["payment-signature"] || req.headers["x-payment"];

  const result = await settlePayment({
    resourceUrl: `${req.protocol}://${req.get("host")}${req.originalUrl}`,
    method: "GET",
    paymentData,
    payTo: "0xYourWalletAddress",
    network: celo,
    price: "$0.05",
    facilitator: thirdwebFacilitator,
  });

  if (result.status === 200) {
    res.json({ data: "premium content" });
  } else {
    res.status(result.status).set(result.responseHeaders).json(result.responseBody);
  }
});
```

## Payment Flow

1. **Client requests resource** - AI agent or app sends HTTP request
2. **Server returns 402** - If no payment, returns `HTTP 402 Payment Required` with payment details
3. **Client signs payment** - Client signs payment authorization
4. **Client retries with payment** - Request sent with `X-PAYMENT` header
5. **Server verifies and settles** - Payment verified and settled on-chain
6. **Server delivers resource** - Content returned with receipt

## Supported Payment Tokens on Celo

| Token | Address | Decimals |
|-------|---------|----------|
| USDC | `0xcebA9300f2b948710d2653dD7B07f33A8B32118C` | 6 |
| USDT | `0x48065fbbe25f71c9282ddf5e1cd6d6a887483d5e` | 6 |
| USDm | `0x765DE816845861e75A25fCA122bb6898B8B1282a` | 18 |

## Celo Configuration

```typescript
import { celo, celoSepolia } from "thirdweb/chains";

// Mainnet
const mainnetConfig = {
  network: celo,
  price: "$0.01",
};

// Testnet (Sepolia)
const testnetConfig = {
  network: celoSepolia,
  price: "$0.01",
};
```

## AI Agent Usage

### Autonomous API Payments

```typescript
// AI agent paying for API calls autonomously
const agent = {
  wallet: agentWallet,
  fetchWithPayment: wrapFetchWithPayment({
    client,
    account: agentWallet
  }),
};

// Agent pays per API call - no API keys needed
const marketData = await agent.fetchWithPayment("https://api.market.com/prices");
const analysis = await agent.fetchWithPayment("https://api.ai.com/analyze");
```

### Pay-Per-Use AI Inference

```typescript
// Server: Charge based on actual token usage with "upto" scheme
const result = await settlePayment({
  resourceUrl: request.url,
  method: "POST",
  paymentData,
  payTo: "0xYourWallet",
  network: celo,
  scheme: "upto",           // Dynamic pricing
  price: "$1.00",           // Maximum amount
  minPrice: "$0.01",        // Minimum amount
  facilitator: thirdwebFacilitator,
});

// Verify first, then charge based on actual usage
const { tokens } = await runAIInference(prompt);
const actualPrice = tokens * 0.0001; // $0.0001 per token

await settlePayment({
  ...paymentArgs,
  price: actualPrice,
});
```

### Micropayments for Content

```typescript
// Pay-per-article instead of subscriptions
app.get("/articles/:id", async (req, res) => {
  const result = await settlePayment({
    resourceUrl: req.url,
    method: "GET",
    paymentData: req.headers["x-payment"],
    payTo: publisherWallet,
    network: celo,
    price: "$0.10",
    facilitator: thirdwebFacilitator,
    routeConfig: {
      description: "Premium article access",
    },
  });
  // ...
});
```

## Integration with ERC-8004

Combine trust verification with payments:

```typescript
import { ReputationRegistry } from '@chaoschain/sdk';
import { wrapFetchWithPayment } from 'thirdweb/x402';

async function payTrustedService(agentId, serviceUrl) {
  // 1. Check reputation first
  const summary = await reputationRegistry.getSummary(agentId);
  if (summary.averageScore < 80) {
    throw new Error('Service reputation too low');
  }

  // 2. Make payment
  const response = await fetchWithPayment(serviceUrl);

  // 3. Submit feedback
  await reputationRegistry.giveFeedback(agentId, 90, 0, 'starred', ...);

  return response.json();
}
```

## Environment Variables

```bash
# Client-side
NEXT_PUBLIC_THIRDWEB_CLIENT_ID=your_client_id

# Server-side
THIRDWEB_SECRET_KEY=your_secret_key
```

## Celo Network Reference

| Network | Chain ID | RPC Endpoint |
|---------|----------|--------------|
| Celo Mainnet | 42220 | https://forno.celo.org |
| Celo Sepolia | 11142220 | https://forno.celo-sepolia.celo-testnet.org |

## Why Celo for x402?

- **Low fees**: Gas costs under $0.001 per transaction
- **Fast finality**: ~1 second block times
- **Stablecoin support**: Native USDC, USDT, USDm
- **Fee abstraction**: Users can pay gas in stablecoins

## Additional Resources

- [x402 Official Website](https://www.x402.org)
- [thirdweb x402 Docs](https://portal.thirdweb.com/x402)
- [thirdweb Playground](https://playground.thirdweb.com/x402)
- [x402 Whitepaper](https://www.x402.org/x402-whitepaper.pdf)
- [GitHub Repository](https://github.com/coinbase/x402)

## Related Skills

- [8004](../8004/SKILL.md) - Trust layer for AI agents
- [thirdweb](../thirdweb/SKILL.md) - Full-stack Web3 development
- [fee-abstraction](../fee-abstraction/SKILL.md) - Pay gas with stablecoins
