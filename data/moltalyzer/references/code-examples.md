# Moltalyzer Code Examples

## TypeScript Setup

```typescript
import { x402Client, wrapFetchWithPayment } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const signer = privateKeyToAccount(process.env.EVM_PRIVATE_KEY as `0x${string}`);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const fetchWithPayment = wrapFetchWithPayment(fetch, client);
```

## Fetch Moltbook Digest

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/moltbook/digests/latest");
const { data } = await res.json();
console.log(data.title);            // "Agent Mesh Steals the Spotlight"
console.log(data.emergingNarratives); // ["decentralized identity", ...]
console.log(data.hotDiscussions);     // [{ topic, sentiment, description }]
```

## Fetch GitHub Digest

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/github/digests/latest");
const { data } = await res.json();
console.log(data.notableProjects);  // [{ name, stars, language, description }]
console.log(data.emergingTools);    // ["LiteLLM: unified LLM gateway proxy"]
```

## Fetch Polymarket Signals

```typescript
// Check index first (free)
const indexRes = await fetch("https://api.moltalyzer.xyz/api/polymarket/index");
const { index } = await indexRes.json();

// Fetch latest signal
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/polymarket/signal");
const { data } = await res.json();
console.log(data.question);          // "Will GTA 6 cost $100+?"
console.log(data.predeterminedType); // "game_developers_or_publishers"
console.log(data.confidence);        // "high"

// Batch fetch with polling
const batchRes = await fetchWithPayment(`https://api.moltalyzer.xyz/api/polymarket/signals?since=${lastIndex}`);
const { data: signals } = await batchRes.json();
```

## Fetch Token Signals

```typescript
// Check index first (free)
const indexRes = await fetch("https://api.moltalyzer.xyz/api/tokens/index");
const { index } = await indexRes.json();

// Fetch latest signal
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/tokens/signal");
const { data } = await res.json();
console.log(data.tokenName, data.tier);     // "PepeMax", "meme"
console.log(data.hybridScore);              // 72.5
console.log(data.llmReasoning);             // "Strong social metrics..."

// Batch with filters
const batchRes = await fetchWithPayment("https://api.moltalyzer.xyz/api/tokens/signals?chain=base&tier=meme&count=10");
```

## Free Samples (No Payment Required)

Test with plain `fetch` — no x402 setup needed:

```typescript
// Moltbook sample (18+ hours old, rate limited to 1/20min)
const moltbook = await fetch("https://api.moltalyzer.xyz/api/moltbook/sample");

// GitHub sample (static snapshot)
const github = await fetch("https://api.moltalyzer.xyz/api/github/sample");

// Polymarket sample (static snapshot)
const polymarket = await fetch("https://api.moltalyzer.xyz/api/polymarket/sample");

// Token sample (24+ hours old)
const tokens = await fetch("https://api.moltalyzer.xyz/api/tokens/sample");
```

## Error Handling

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/moltbook/digests/latest");

if (res.status === 402) {
  // Payment failed — check wallet has USDC on Base Mainnet
  // The response body contains pricing and setup instructions
  const info = await res.json();
  console.error("Payment required:", info.price, info.network);
}

if (res.status === 429) {
  // Rate limited — respect Retry-After header
  const retryAfter = res.headers.get("Retry-After");
  console.error(`Rate limited. Retry after ${retryAfter} seconds.`);
}

if (res.status === 404) {
  // No data available yet (e.g., no digests generated)
}
```

## Rate Limit Headers

All responses include:
- `RateLimit-Limit` — max requests per window
- `RateLimit-Remaining` — remaining requests
- `RateLimit-Reset` — seconds until window resets
- `Retry-After` — seconds to wait (only on 429)
