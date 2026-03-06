# Integration Guide

Code examples for integrating Clawdio with x402-compatible agent frameworks.

## Coinbase AgentKit

The x402 payment flow is fully automatic with AgentKit:

```javascript
import {
  AgentKit,
  CdpEvmWalletProvider,
  walletActionProvider,
  x402ActionProvider,
} from "@coinbase/agentkit";

const walletProvider = await CdpEvmWalletProvider.configureWithWallet({
  apiKeyId: process.env.CDP_API_KEY_ID,
  apiKeySecret: process.env.CDP_API_KEY_SECRET,
  walletSecret: process.env.CDP_WALLET_SECRET,
  address: YOUR_WALLET_ADDRESS,
  networkId: "base-mainnet",
});

const agentKit = await AgentKit.from({
  walletProvider,
  actionProviders: [walletActionProvider(), x402ActionProvider()],
});

// Agent can now browse and purchase Clawdio reports automatically.
// Point it at https://clawdio.vail.report/ and it will self-discover the API.
```

## @x402/fetch

For direct programmatic access without AgentKit:

```javascript
import { wrapFetch } from "@x402/fetch";

const x402Fetch = wrapFetch(globalThis.fetch, walletClient);

// Browse catalog (free — no payment needed)
const catalog = await fetch("https://clawdio.vail.report/catalog").then((r) =>
  r.json()
);

// Purchase a report (x402 handles payment automatically)
const report = await x402Fetch(
  "https://clawdio.vail.report/catalog/purchase?id={uuid}"
).then((r) => r.json());
```

## Compatible Wallet Providers

Any wallet that supports the [x402 protocol](https://www.x402.org/) works with Clawdio:

- [Coinbase AgentKit](https://docs.cdp.coinbase.com/agentkit) with `x402ActionProvider()`
- [Coinbase CDP SDK](https://docs.cdp.coinbase.com/) with `CdpEvmWalletProvider`
- Any x402-compatible wallet on Base Mainnet

## Purchase Flow

```
Agent                          Clawdio                      Facilitator
  |                               |                              |
  |  GET /catalog                 |                              |
  |------------------------------>|                              |
  |  200 OK (product list)        |                              |
  |<------------------------------|                              |
  |                               |                              |
  |  GET /catalog/purchase?id=... |                              |
  |------------------------------>|                              |
  |  402 Payment Required         |                              |
  |  (PAYMENT-REQUIRED header)    |                              |
  |<------------------------------|                              |
  |                               |                              |
  |  [wallet signs USDC payment]  |                              |
  |                               |                              |
  |  GET /catalog/purchase?id=... |                              |
  |  (PAYMENT-SIGNATURE header)   |                              |
  |------------------------------>|                              |
  |                               |  verify + settle payment     |
  |                               |----------------------------->|
  |                               |  settlement confirmation     |
  |                               |<-----------------------------|
  |  200 OK                       |                              |
  |  (full artifacts + tx hash)   |                              |
  |<------------------------------|                              |
```

The x402 payment is handled automatically via the `PAYMENT-SIGNATURE` header — your wallet provider manages signing and settlement. You do not need to construct payment transactions manually.