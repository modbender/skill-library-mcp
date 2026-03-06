---
name: breeze-x402-payment-api
description: Interact with the Breeze yield aggregator through the x402 payment-gated HTTP API. Use when the user wants to check DeFi balances, deposit tokens, withdraw tokens, or manage Solana yield positions via x402 micropayments.
---

# Breeze x402 Payment API

This skill enables interaction with [Breeze](https://breeze.baby), a Solana yield aggregator, through an HTTP API gated by the [x402 payment protocol](https://www.x402.org/). Each API call is automatically paid for with a USDC micropayment on Solana.

## Prerequisites

- A Solana wallet with USDC for x402 micropayments
- An x402-compatible API server (default: `https://x402.breeze.baby`)
- Node.js / TypeScript environment

## Dependencies

```
@faremeter/fetch        — wraps fetch with automatic x402 payment handling
@faremeter/payment-solana — Solana payment handler for x402
@faremeter/wallet-solana  — local wallet abstraction
@scure/base             — base58 encoding/decoding
@solana/web3.js         — Solana transaction signing and sending
```

## Setup: Payment-Wrapped Fetch

All API calls use a payment-wrapped `fetch` that automatically handles x402 challenges (HTTP 402 → sign payment → retry with proof):

```typescript
import { wrap } from "@faremeter/fetch";
import { createPaymentHandler } from "@faremeter/payment-solana/exact";
import { createLocalWallet } from "@faremeter/wallet-solana";
import { Connection, Keypair, PublicKey } from "@solana/web3.js";
import { base58 } from "@scure/base";

const keypair = Keypair.fromSecretKey(base58.decode(WALLET_PRIVATE_KEY));
const connection = new Connection(SOLANA_RPC_URL);
const wallet = await createLocalWallet("mainnet-beta", keypair);
const USDC_MINT = new PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v");
const paymentHandler = createPaymentHandler(wallet, USDC_MINT, connection);

const fetchWithPayment = wrap(fetch, { handlers: [paymentHandler] });
```

## API Endpoints

### Check Balance

```
GET /balance/:fund_user
```

Returns JSON with positions, deposited amounts, yield earned, and APY. Values are in **base units** — divide by `10^decimals` for human-readable amounts (e.g. USDC has 6 decimals).

```typescript
const response = await fetchWithPayment(
  `${API_URL}/balance/${encodeURIComponent(walletPublicKey)}`,
  { method: "GET" }
);
const balances = await response.json();
```

### Deposit

```
POST /deposit
Content-Type: application/json
```

Builds an unsigned deposit transaction. The `amount` must be in **base units**.

```typescript
const response = await fetchWithPayment(`${API_URL}/deposit`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    amount: 10_000_000,        // 10 USDC (6 decimals)
    user_key: walletPublicKey,
    strategy_id: STRATEGY_ID,
    base_asset: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  }),
});
const txString = await response.text(); // encoded unsigned transaction
```

### Withdraw

```
POST /withdraw
Content-Type: application/json
```

Builds an unsigned withdrawal transaction. Supports optional WSOL handling flags.

```typescript
const response = await fetchWithPayment(`${API_URL}/withdraw`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    amount: 5_000_000,
    user_key: walletPublicKey,
    strategy_id: STRATEGY_ID,
    base_asset: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    all: false,
    exclude_fees: true,          // always recommended
    // For wrapped SOL withdrawals only:
    // unwrap_wsol_ata: true,     // unwrap WSOL to native SOL
    // create_wsol_ata: true,     // create WSOL ATA if needed
    // detect_wsol_ata: true,     // auto-detect WSOL ATA existence
  }),
});
const txString = await response.text();
```

**Withdraw parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | number | yes | Amount in base units |
| `user_key` | string | yes | User's Solana public key |
| `strategy_id` | string | yes | Breeze strategy ID |
| `base_asset` | string | yes | Token mint address |
| `all` | boolean | no | Withdraw entire position |
| `exclude_fees` | boolean | no | Exclude fees from amount (recommended: `true`) |
| `unwrap_wsol_ata` | boolean | no | Unwrap WSOL to native SOL after withdraw |
| `create_wsol_ata` | boolean | no | Create WSOL ATA if it doesn't exist |
| `detect_wsol_ata` | boolean | no | Auto-detect WSOL ATA and set flags accordingly |

**WSOL handling:** When withdrawing wrapped SOL (`So11111111111111111111111111111111111111112`), pass `unwrap_wsol_ata: true` to receive native SOL instead.

## Signing and Sending Transactions

The deposit and withdraw endpoints return encoded unsigned transactions. Sign and send them:

```typescript
import { VersionedTransaction, Transaction } from "@solana/web3.js";

function extractTransactionString(responseText: string): string {
  const trimmed = responseText.trim();
  try {
    const parsed = JSON.parse(trimmed);
    if (typeof parsed === "string") return parsed;
    throw new Error("expected transaction string");
  } catch (e) {
    if (e instanceof SyntaxError) return trimmed;
    throw e;
  }
}

async function signAndSend(txString: string) {
  const bytes = Uint8Array.from(Buffer.from(txString, "base64"));

  // Try versioned transaction first, then legacy
  try {
    const tx = VersionedTransaction.deserialize(bytes);
    tx.sign([keypair]);
    const sig = await connection.sendRawTransaction(tx.serialize());
    await connection.confirmTransaction(sig, "confirmed");
    return sig;
  } catch {
    const tx = Transaction.from(bytes);
    tx.partialSign(keypair);
    const sig = await connection.sendRawTransaction(tx.serialize());
    await connection.confirmTransaction(sig, "confirmed");
    return sig;
  }
}
```

## Supported Tokens

| Token | Mint | Decimals |
|-------|------|----------|
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6 |
| USDS | `USDSwr9ApdHk5bvJKMjzff41FfuX8bSxdKcR81vTwcA` | 6 |
| SOL | `So11111111111111111111111111111111111111112` | 9 |
| JitoSOL | `J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn` | 9 |
| mSOL | `mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So` | 9 |
| JupSOL | `jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v` | 9 |
| JLP | `27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4` | 6 |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WALLET_PRIVATE_KEY` | yes | — | Base58-encoded Solana private key |
| `STRATEGY_ID` | yes | — | Breeze strategy ID |
| `X402_API_URL` | no | `https://x402.breeze.baby` | x402 payment API URL |
| `SOLANA_RPC_URL` | no | `https://api.mainnet-beta.solana.com` | Solana RPC endpoint |
| `BASE_ASSET` | no | USDC mint | Default token mint for operations |

## Example: Full Agent Workflow

A typical deposit flow:

1. **Check balance** → `GET /balance/:wallet` (paid via x402)
2. **Build deposit tx** → `POST /deposit` with amount in base units (paid via x402)
3. **Extract transaction** from response text
4. **Sign and send** the transaction to Solana
5. **Report** the transaction signature and explorer link (`https://solscan.io/tx/{sig}`)

See `apps/examples/agent-using-x402-payment-api/` for a complete working implementation with a Claude-powered agentic loop.
