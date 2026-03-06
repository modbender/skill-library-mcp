# Carbium API Reference

> Source: https://docs.carbium.io/page/skill
> Drop this into any AI assistant's context to enable Carbium-aware Solana development.

---

## Products & Base URLs

| Product | What it does | Base URL |
|---|---|---|
| RPC | Standard JSON-RPC (reads, writes, subscriptions) | https://rpc.carbium.io |
| gRPC / Stream | Real-time Yellowstone Full Block streaming | wss://grpc.carbium.io |
| Swap API | Aggregated DEX quotes, routing, swap execution | https://api.carbium.io |
| DEX | UI DEX (user-facing, wallet connect) | https://carbium.io |
| Docs | Full documentation | https://docs.carbium.io |

## Signup

| Product | Signup URL | Notes |
|---|---|---|
| RPC + gRPC | https://rpc.carbium.io/signup | One key covers both endpoints |
| Swap API | https://api.carbium.io/login | Free account, key available instantly |

## Pricing Tiers

| Tier | Price | Credits/mo | Max RPS | gRPC |
|---|---|---|---|---|
| Free | $0 | 500K | 10 | ❌ |
| Developer | $32/mo | 10M | 50 | ❌ |
| Business | $320/mo | 100M | 200 | ✅ |
| Professional | $640/mo | 200M | 500 | ✅ |

gRPC streaming requires Business tier or above.

---

## RPC

Endpoint: `https://rpc.carbium.io/?apiKey=YOUR_RPC_KEY`

Standard Solana JSON-RPC. Any Solana SDK works: `@solana/web3.js`, `solana-py`, Rust crate.

### JavaScript / TypeScript

```ts
import { Connection, PublicKey, LAMPORTS_PER_SOL } from "@solana/web3.js";

const connection = new Connection(
  `https://rpc.carbium.io/?apiKey=${process.env.CARBIUM_RPC_KEY}`,
  "confirmed"
);

// Get balance
const pubkey = new PublicKey("YOUR_WALLET_ADDRESS");
const balance = await connection.getBalance(pubkey);
console.log(`Balance: ${balance / LAMPORTS_PER_SOL} SOL`);

// Send transaction
const sig = await connection.sendRawTransaction(transaction.serialize(), {
  skipPreflight: false,
  maxRetries: 3,
});
await connection.confirmTransaction(sig, "confirmed");
```

### Python

```python
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import os

rpc = Client(f"https://rpc.carbium.io/?apiKey={os.environ['CARBIUM_RPC_KEY']}")
pubkey = Pubkey.from_string("YOUR_WALLET_ADDRESS")
resp = rpc.get_balance(pubkey)
print(f"Balance: {resp.value / 1e9} SOL")
```

### Rust

```rust
use solana_client::rpc_client::RpcClient;
use solana_sdk::pubkey::Pubkey;
use std::str::FromStr;

let url = format!(
  "https://rpc.carbium.io/?apiKey={}",
  std::env::var("CARBIUM_RPC_KEY").unwrap()
);
let client = RpcClient::new(url);
let pubkey = Pubkey::from_str("YOUR_WALLET_ADDRESS").unwrap();
let balance = client.get_balance(&pubkey).unwrap();
```

---

## gRPC / Yellowstone Streaming

Real-time Full Block stream. ~22ms latency. Atomic complete blocks — no shred reassembly needed.

Requires **Business tier or above**.

| Method | Format |
|---|---|
| WebSocket query param | `wss://grpc.carbium.io/?apiKey=YOUR_RPC_KEY` |
| HTTP/2 header (Rust) | `x-token: YOUR_RPC_KEY` |

### JavaScript — Subscribe to program transactions

```js
import WebSocket from "ws";

const PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"; // e.g. pump.fun

const ws = new WebSocket(
  `wss://grpc.carbium.io/?apiKey=${process.env.CARBIUM_RPC_KEY}`
);

ws.on("open", () => {
  ws.send(JSON.stringify({
    jsonrpc: "2.0", id: 1,
    method: "transactionSubscribe",
    params: [
      {
        vote: false,
        failed: false,
        accountInclude: [PROGRAM_ID], // at least one of accountInclude or accountRequired required
        accountExclude: [],
        accountRequired: [],
      },
      {
        commitment: "confirmed",
        encoding: "base64",
        transactionDetails: "full",
        showRewards: false,
        maxSupportedTransactionVersion: 0,
      },
    ],
  }));
});

// WS keepalive — ping every 30s
setInterval(() => ws.ping(), 30_000);

ws.on("message", (raw) => {
  const msg = JSON.parse(raw.toString());
  if (msg.result !== undefined) {
    console.log(`Subscribed, ID: ${msg.result}`);
    return;
  }
  if (msg.method === "transactionNotification") {
    const { signature, slot } = msg.params.result;
    console.log(`tx ${signature} in slot ${slot}`);
  }
});

ws.on("close", (code) => {
  // Always reconnect with exponential backoff
  console.warn(`Disconnected (${code}), reconnecting...`);
});
```

### Python

```python
import asyncio, json, os
import websockets

PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

async def subscribe():
  uri = f"wss://grpc.carbium.io/?apiKey={os.environ['CARBIUM_RPC_KEY']}"
  async with websockets.connect(uri) as ws:
    await ws.send(json.dumps({
      "jsonrpc": "2.0", "id": 1,
      "method": "transactionSubscribe",
      "params": [
        { "vote": False, "failed": False, "accountInclude": [PROGRAM_ID],
          "accountExclude": [], "accountRequired": [] },
        { "commitment": "confirmed", "encoding": "base64",
          "transactionDetails": "full", "showRewards": False,
          "maxSupportedTransactionVersion": 0 },
      ],
    }))
    async for message in ws:
      data = json.loads(message)
      if "result" in data:
        print(f"Subscribed: {data['result']}")
      elif data.get("method") == "transactionNotification":
        print(f"tx: {data['params']['result']['signature'][:20]}...")

asyncio.run(subscribe())
```

### Rust (Yellowstone gRPC client)

```rust
use yellowstone_grpc_client::GeyserGrpcClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
  let mut client = GeyserGrpcClient::connect(
    "https://grpc.carbium.io",
    "YOUR_RPC_KEY", // passed as x-token header automatically
    None,
  )?;
  let (_subscribe_tx, mut stream) = client.subscribe().await?;
  // define subscription filters and consume stream...
  Ok(())
}
```

### Filter parameters

| Field | Type | Description |
|---|---|---|
| vote | bool | Include vote transactions |
| failed | bool | Include failed transactions |
| accountInclude | string[] | Include txs involving ANY of these accounts |
| accountExclude | string[] | Exclude txs involving these accounts |
| accountRequired | string[] | Only include txs involving ALL of these accounts |

### Unsubscribe

```json
{"jsonrpc": "2.0", "id": 2, "method": "transactionUnsubscribe", "params": [SUBSCRIPTION_ID]}
```

---

## Swap API

Single API: get quote → get swap transaction → execute on-chain.
Aggregates Solana DEX liquidity via CQ1 engine (sub-ms quotes, ~10ms chain → queryable).

Base URL: `https://api.carbium.io`  
API version: `v2`  
Auth: `X-API-KEY: YOUR_API_KEY` header on all requests

### GET /api/v2/quote

| Param | Description | Example |
|---|---|---|
| src_mint | Input token mint | `So111...112` (SOL) |
| dst_mint | Output token mint | `EPjFW...t1v` (USDC) |
| amount_in | Input amount in smallest unit (lamports) | `1000000000` |
| slippage_bps | Slippage tolerance in basis points | `100` (= 1%) |

```js
// JavaScript
fetch(
  'https://api.carbium.io/api/v2/quote' +
  '?src_mint=So11111111111111111111111111111111111111112' +
  '&dst_mint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v' +
  '&amount_in=1000000000' +
  '&slippage_bps=100',
  { headers: { 'X-API-KEY': process.env.CARBIUM_API_KEY } }
)
  .then(res => res.json())
  .then(console.log);
```

```python
# Python
import httpx, os

resp = httpx.get(
  "https://api.carbium.io/api/v2/quote",
  params={
    "src_mint": "So11111111111111111111111111111111111111112",
    "dst_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "amount_in": 1_000_000_000,
    "slippage_bps": 100,
  },
  headers={"X-API-KEY": os.environ["CARBIUM_API_KEY"]},
)
print(resp.json())
```

### GET /api/v2/swap

| Param | Description | Example |
|---|---|---|
| fromMint | Input token mint | `So111...112` |
| toMint | Output token mint | `EPjFW...t1v` |
| amount | Input amount in smallest unit | `100000000` |
| slippage | Slippage in basis points | `100` |
| provider | DEX/AMM to route through | `raydium` |

> Returns a serialized transaction (base64). Deserialize, sign with your wallet, then send via RPC.

```ts
// TypeScript — full execute flow
import { Connection, VersionedTransaction } from "@solana/web3.js";

const connection = new Connection(
  `https://rpc.carbium.io/?apiKey=${process.env.CARBIUM_RPC_KEY}`,
  "confirmed"
);

const res = await fetch(
  `https://api.carbium.io/api/v2/swap` +
  `?fromMint=So11111111111111111111111111111111111111112` +
  `&toMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` +
  `&amount=100000000&slippage=100&provider=raydium`,
  { headers: { accept: "text/plain", "X-API-KEY": process.env.CARBIUM_API_KEY! } }
);
const { transaction } = await res.json();

const tx = VersionedTransaction.deserialize(Buffer.from(transaction, "base64"));
// tx.sign([yourKeypair]);
const sig = await connection.sendRawTransaction(tx.serialize(), { maxRetries: 3 });
await connection.confirmTransaction(sig, "confirmed");
console.log("Swap confirmed:", sig);
```

### GET /api/v2/swap/bundle (Jito)

```js
fetch('https://api.carbium.io/api/v2/swap/bundle', {
  headers: { accept: 'application/json', 'X-API-KEY': process.env.CARBIUM_API_KEY }
})
  .then(res => res.json())
  .then(console.log);
```

> ⚠️ Carbium Swap API cannot route pump.fun / Raydium CPMM tokens. For pre-graduation tokens use gRPC + raw bonding curve transactions (see below).

---

## pump.fun Sniping

> Requires Business tier (gRPC access).

### Constants

```ts
const PUMP_PROGRAM   = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P";
const PUMP_GLOBAL    = "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf";
const PUMP_FEE_RECIPIENT = "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM";
const PUMP_EVENT_AUTH    = "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1";
const GRADUATION_SOL = 85_000_000_000n; // 85 SOL in lamports
const TOTAL_SUPPLY   = 1_000_000_000_000_000n; // 1 quadrillion (6 decimals)

const DISCRIMINATORS = {
  create: [0xe4, 0x45, 0xa5, 0x2e, 0x51, 0xcb, 0x9a, 0x1d],
  buy:    [0x66, 0x06, 0x3d, 0x12, 0x01, 0xda, 0xeb, 0xea],
  sell:   [0x33, 0xe6, 0x85, 0xa4, 0x01, 0x7f, 0x83, 0xad],
};
```

### Detect new token launches (gRPC)

```ts
ws.on("message", (raw) => {
  const msg = JSON.parse(raw.toString());
  if (msg.method !== "transactionNotification") return;

  const { signature, transaction } = msg.params.result;
  const logs = transaction.meta.logMessages || [];

  for (const log of logs) {
    if (log.includes("Instruction: Create")) {
      const mint = transaction.meta.postTokenBalances[0]?.mint;
      if (mint) handleNewToken(mint, signature);
    }
  }
});
```

### Derive bonding curve address

```ts
import { PublicKey } from "@solana/web3.js";

function deriveBondingCurve(mint: string): PublicKey {
  const [address] = PublicKey.findProgramAddressSync(
    [Buffer.from("bonding-curve"), new PublicKey(mint).toBuffer()],
    new PublicKey(PUMP_PROGRAM)
  );
  return address;
}
```

### Bonding curve layout (81 bytes)

```
[0-7]   discriminator
[8-15]  virtualTokenReserves  (u64 LE)
[16-23] virtualSolReserves    (u64 LE)
[24-31] realTokenReserves     (u64 LE)
[32-39] realSolReserves       (u64 LE)
[40-47] tokenTotalSupply      (u64 LE)
[72]    complete              (bool)
```

```ts
async function fetchBondingCurve(bondingCurveAddress: PublicKey) {
  const res = await fetch(`https://rpc.carbium.io/?apiKey=${process.env.CARBIUM_RPC_KEY}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0", id: 1,
      method: "getAccountInfo",
      params: [bondingCurveAddress.toBase58(), { encoding: "base64" }],
    }),
  });
  const { result } = await res.json();
  const data = Buffer.from(result.value.data[0], "base64");
  return {
    virtualTokenReserves: data.readBigUInt64LE(8),
    virtualSolReserves:   data.readBigUInt64LE(16),
    realTokenReserves:    data.readBigUInt64LE(24),
    realSolReserves:      data.readBigUInt64LE(32),
    complete:             data.readUInt8(72) === 1,
  };
}
```

### Price math

```ts
// Buy: tokens out for X SOL in
function quoteBuy(curve: CurveState, solLamports: number): bigint {
  const num = curve.virtualTokenReserves * BigInt(solLamports);
  const den = curve.virtualSolReserves + BigInt(solLamports);
  return num / den;
}

// Sell: SOL out for X tokens in
function quoteSell(curve: CurveState, tokens: bigint): bigint {
  const num = curve.virtualSolReserves * tokens;
  const den = curve.virtualTokenReserves + tokens;
  return num / den;
}

// Bonding progress
const bondingPct = Math.min(100,
  (Number(curve.realSolReserves) / Number(GRADUATION_SOL)) * 100
);
```

### Buy instruction accounts (order matters)

```
0  PUMP_GLOBAL           (read)
1  PUMP_FEE_RECIPIENT    (write)
2  mint                  (read)
3  bondingCurve          (write)
4  bondingCurve ATA      (write)
5  user ATA              (write)
6  user/payer            (write, signer)
7  SystemProgram
8  TokenProgram
9  AssociatedTokenProgram
10 Rent sysvar
11 PUMP_EVENT_AUTH       (read)
12 PUMP_PROGRAM          (read)
```

### Submit transaction

```ts
// skipPreflight: true saves ~200ms
const submitRes = await fetch(
  `https://rpc.carbium.io/?apiKey=${process.env.CARBIUM_RPC_KEY}`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0", id: 1,
      method: "sendTransaction",
      params: [
        signedTxBase64,
        { skipPreflight: true, preflightCommitment: "confirmed", maxRetries: 3 },
      ],
    }),
  }
);
```

### Snipe flow

```
gRPC "Create" event → extract mint
  → deriveBondingCurve(mint)
  → [optional] fetchBondingCurve() for price check
  → build buy instruction with desired SOL
  → sendTransaction(skipPreflight: true)
  → monitor bonding curve state for exit
  → sell when target % reached or graduation imminent
```

---

## Operational Guardrails

### Performance tips
- `skipPreflight: true` — saves ~200ms on submits
- Pre-build tx templates — swap in mint at launch time
- Fetch bonding curve in parallel while building tx
- WS keepalive ping every 30s to avoid silent disconnects

### Retry with exponential backoff

```ts
const delay = (ms: number) => new Promise(r => setTimeout(r, ms));

async function withRetry<T>(fn: () => Promise<T>, retries = 3, baseMs = 300): Promise<T> {
  for (let i = 0; i < retries; i++) {
    try { return await fn(); }
    catch (e) {
      if (i === retries - 1) throw e;
      await delay(baseMs * 2 ** i + Math.random() * 100); // exponential + jitter
    }
  }
  throw new Error("unreachable");
}
```

### WebSocket reconnect

```ts
async function connectWithReconnect() {
  let backoff = 1000;
  while (true) {
    try {
      await connect(); // your ws connect logic
      backoff = 1000;
    } catch {
      await delay(backoff);
      backoff = Math.min(backoff * 2, 30_000); // cap at 30s
    }
  }
}
```

### Error reference

| Error | Cause | Fix |
|---|---|---|
| Blockhash expired | Tx took too long | Fresher blockhash; reduce latency |
| Insufficient funds | Not enough SOL | Balance must cover amount + fees (~0.005 SOL) |
| Account not found | Token just created | Retry with 50–100ms delay |
| Slippage exceeded | Price moved | Increase maxSolCost or reduce size |
| Quote: no route found | Unsupported token pair | Use gRPC + raw bonding curve |
| Simulation failed | Pre-flight error | Do NOT send — inspect and log |
| HTTP 429 | Rate limit | Back off immediately; retry after delay |

### HTTP status codes

| Code | Meaning | Action |
|---|---|---|
| 401 | Invalid / missing API key | Check key and auth format |
| 403 | Plan restriction (e.g. gRPC on free tier) | Upgrade at rpc.carbium.io |
| 429 | Rate limit exceeded | Backoff + retry |
| 500 | Server error | Retry after 1s |
| 503 | Temporary unavailability | Retry with backoff |

---

## Architecture Notes

- **CQ1 engine**: Carbium's DEX routing — decoupled write/read paths, binary-native state. ~10ms chain → queryable. Sub-ms quote generation.
- **Full Blocks vs Shreds**: Carbium streams Full Blocks (~22ms). Shreds (~9ms) require client-side reassembly. Difference negligible vs ~400ms Solana slot time.
- **MEV protection + Jito bundling**: Built into Swap API. Use `/api/v2/swap/bundle`.
- **Gasless swaps**: Supported via Swap API.
- **Commitment levels**: `processed` (fastest, may roll back) → `confirmed` (recommended) → `finalized` (slowest, guaranteed).

---

## Further Reading

| Topic | URL |
|---|---|
| Ecosystem overview | https://docs.carbium.io/docs/the-carbium-ecosystem |
| RPC Quick Start | https://docs.carbium.io/docs/quick-start-rpc |
| Swap API Quick Start | https://docs.carbium.io/docs/quick-start-dex-api |
| gRPC / Streaming | https://docs.carbium.io/docs/solana-grpc |
| CQ1 Engine | https://docs.carbium.io/docs/cq1-engine-overview |
| RPC Pricing | https://docs.carbium.io/docs/carbium-rpc-pricing |
| API Recipes | https://docs.carbium.io/recipes |
| FAQ | https://docs.carbium.io/docs/faq |
| Support (Discord) | https://discord.gg/jW7BUkQS5U |
