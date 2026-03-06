---
name: moltalyzer
version: 1.7.1
description: >-
  Fetch trending topics, sentiment, and narratives from Moltbook (hourly),
  discover hot new GitHub repos and emerging tools (daily), detect Polymarket
  prediction markets with predetermined outcome signals (every 4 hours), or
  get real-time token intelligence signals for new crypto tokens (every 4 min).
  Four data feeds. x402 micropayments, no API key needed.
homepage: https://moltalyzer.xyz
metadata:
  openclaw:
    emoji: "🔭"
    requires:
      env: ["EVM_PRIVATE_KEY"]
      bins: ["node"]
    primaryEnv: "EVM_PRIVATE_KEY"
    install:
      - id: npm
        kind: command
        command: "npm install @x402/fetch @x402/evm viem"
        bins: ["node"]
        label: "Install x402 payment client"
---

# Moltalyzer — AI Intelligence Feeds

Four data feeds from `https://api.moltalyzer.xyz`:

1. **Moltbook** (hourly) — trending topics, sentiment, emerging/fading narratives, hot discussions
2. **GitHub** (daily) — trending new repos, emerging tools, language trends, notable projects
3. **Polymarket** (every 4h) — markets with predetermined outcome signals, confidence levels, and reasoning
4. **Token Intelligence** (every 4min) — real-time token signals with hybrid rule+LLM scoring, chain filtering

## Try Free First

No setup needed. Test with plain `fetch`:

```typescript
const res = await fetch("https://api.moltalyzer.xyz/api/moltbook/sample");
const { data } = await res.json();
// data.emergingNarratives, data.hotDiscussions, data.fullDigest, etc.
```

All four feeds have free samples: `/api/moltbook/sample`, `/api/github/sample`, `/api/polymarket/sample`, `/api/tokens/sample` (rate limited to 1 req/20min each).

## Paid Endpoints

Payments are automatic via x402 — no API keys or accounts. Prices range from $0.005 to $0.05 per request.

| Feed | Endpoint | Price |
|------|----------|-------|
| Moltbook | `GET /api/moltbook/digests/latest` | $0.005 |
| Moltbook | `GET /api/moltbook/digests?hours=N` | $0.02 |
| GitHub | `GET /api/github/digests/latest` | $0.02 |
| GitHub | `GET /api/github/digests?days=N` | $0.05 |
| GitHub | `GET /api/github/repos?limit=N` | $0.01 |
| Polymarket | `GET /api/polymarket/signal` | $0.01 |
| Polymarket | `GET /api/polymarket/signals?since=N&count=5` | $0.03 |
| Tokens | `GET /api/tokens/signal` | $0.01 |
| Tokens | `GET /api/tokens/signals?since=N&count=5` | $0.05 |
| Tokens | `GET /api/tokens/history?from=YYYY-MM-DD` | $0.03 |

### Quick Start (Paid)

```typescript
import { x402Client, wrapFetchWithPayment } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const signer = privateKeyToAccount(process.env.EVM_PRIVATE_KEY as `0x${string}`);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const fetchWithPayment = wrapFetchWithPayment(fetch, client);

const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/moltbook/digests/latest");
const { data } = await res.json();
```

## Polling Pattern (Polymarket & Tokens)

Polymarket and Token feeds use an index-based signal pattern. Poll the free index endpoint, then fetch new signals:

```typescript
let lastIndex = 0;
// Check for new signals (free)
const indexRes = await fetch("https://api.moltalyzer.xyz/api/polymarket/index");
const { index } = await indexRes.json();
if (index > lastIndex) {
  // Fetch new signals (paid)
  const res = await fetchWithPayment(`https://api.moltalyzer.xyz/api/polymarket/signals?since=${lastIndex}`);
  const { data } = await res.json();
  lastIndex = index;
}
```

## Error Handling

- **402** — Payment failed. Check wallet has USDC on Base Mainnet. Response body has pricing details.
- **429** — Rate limited. Respect `Retry-After` header (seconds to wait).
- **404** — No data available yet (e.g., service just started, no digests generated).

## Reference Docs

For full response schemas, see `{baseDir}/references/response-formats.md`.
For more code examples and error handling patterns, see `{baseDir}/references/code-examples.md`.
For complete endpoint tables and rate limits, see `{baseDir}/references/api-reference.md`.
