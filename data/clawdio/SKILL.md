---
name: clawdio
description: Auditory intelligence for AI agents. Transforms human audio into into structured data, semantic reports, and machine-readable markdown. Use when you need market intelligence, crypto alpha, speaker-attributed quotes, or sentiment analysis from voice conversations. Requires x402 payment in USDC on Base Mainnet.
compatibility: Requires x402-compatible wallet (Coinbase AgentKit, CDP SDK, or @x402/fetch) with USDC on Base Mainnet. Requires network access.
metadata:
  author: vail
  version: "1.0.0"
  homepage: https://clawdio.vail.report
  api-base: https://clawdio.vail.report
  protocol: x402
  network: eip155:8453
  currency: USDC
  price: "1.49"
  category: intelligence
---

# Clawdio — Auditory Intelligence for AI Agents

Clawdio, powered by VAIL (Voice AI Layer), gives AI agents **auditory perception** by transforming long-form human audio into structured data, semantic reports, and machine-readable markdown.

Agents interact with an **x402 payment-gated API** to ingest spoken conversations as first-class inputs — just like text, price feeds, or alternative data sources.

Initial deployment focuses on **AI and Crypto Twitter Spaces**, where high-signal market intelligence exists primarily in voice.

**Base URL:** `https://clawdio.vail.report`
**Protocol:** x402
**Network:** Base Mainnet (eip155:8453)
**Currency:** USDC
**Price:** $1.49 per report

---

## Requirements

You need an **x402-compatible wallet** funded with USDC on Base Mainnet. Compatible wallet providers include:

- [Coinbase AgentKit](https://docs.cdp.coinbase.com/agentkit) with `x402ActionProvider()`
- [Coinbase CDP SDK](https://docs.cdp.coinbase.com/) with `CdpEvmWalletProvider`
- Any wallet that supports the [x402 protocol](https://www.x402.org/)

The x402 payment is handled **automatically** via the `PAYMENT-SIGNATURE` header — your wallet provider manages the signing and settlement. You do not need to construct payment transactions manually.

---

## Quick Start

### Step 1: Understand the API

Visit the API root to get a self-describing overview:

```bash
curl https://clawdio.vail.report/
```

This returns the full API description, available endpoints, pricing, and purchase flow instructions.

### Step 2: Browse the Catalog (Free)

```bash
curl https://clawdio.vail.report/catalog
```

No payment or authentication required. Returns all available products with metadata:

```json
{
  "products": [
    {
      "id": "c6d36398-a0c8-4c21-9aa4-1d1d9084a820",
      "title": "AI & Crypto Twitter Space",
      "abstract": "Analysis of a discussion covering...",
      "date": "2025-01-15",
      "length": "01:23:45",
      "listeners": 1234,
      "purchase": {
        "url": "https://clawdio.vail.report/catalog/purchase?id=c6d36398-a0c8-4c21-9aa4-1d1d9084a820",
        "method": "GET",
        "protocol": "x402",
        "price": "1.49 USDC"
      }
    }
  ],
  "total": 15,
  "purchase_instructions": {
    "steps": [
      "Select a product from the list above",
      "Make an HTTP GET request to the product's purchase.url",
      "Your x402-compatible wallet handles payment automatically",
      "You receive the full artifact set (metadata + report + transcript)"
    ],
    "important": "The purchase endpoint uses GET, not POST. Save the artifacts — repurchase is required for repeat access."
  }
}
```

### Step 3: Purchase a Report ($1.49 USDC)

```bash
curl https://clawdio.vail.report/catalog/purchase?id={uuid}
```

**Important:** This is a **GET** request, not POST.

On first request without payment, the server returns **HTTP 402 Payment Required** with a `PAYMENT-REQUIRED` header. Your x402 wallet automatically:

1. Reads the payment requirements from the 402 response
2. Signs a USDC payment on Base Mainnet
3. Retries the request with the `PAYMENT-SIGNATURE` header
4. Receives the full content after payment settles

### What You Get

Each purchase returns a JSON object with three artifact layers (metadata + report + transcript):

```json
{
  "id": "c6d36398-a0c8-4c21-9aa4-1d1d9084a820",
  "transaction": "0x1234...abcd",
  "title": "AI & Crypto Twitter Space",
  "date": "2025-01-15",
  "length": "01:23:45",
  "listeners": 1234,
  "participants": {
    "hosts": [
      {
        "display_name": "Host Name",
        "screen_name": "host_handle",
        "avatar_url": "https://..."
      }
    ],
    "speakers": [
      {
        "display_name": "Speaker Name",
        "screen_name": "speaker_handle",
        "avatar_url": "https://..."
      }
    ]
  },
  "content": {
    "report": {
      "format": "markdown",
      "content": "## Abstract\n\nAnalysis of the Twitter Space...\n\n## Key Insights\n\n- ...\n\n## Hot Takes\n\n> \"Quote\" — **Speaker** (timestamp)\n\n## Timeline\n\n- ...\n\n## Potential Alpha\n\n- ...\n\n## Market Sentiment\n\n**Overall:** Bullish\n\n## Project Mentions\n\n- **Project**: Context"
    },
    "transcript": {
      "format": "markdown",
      "content": "# Transcript\n\n**Speaker 1** [00:01:26 - 00:01:49]\n> Spoken text here...\n\n**Speaker 2** [00:01:50 - 00:02:15]\n> Response text here..."
    }
  }
}
```

**Artifact 1 — Metadata:** Title, date, duration, listener count, full participant list with Twitter handles and avatars.

**Artifact 2 — Report (Markdown):** Structured analysis including abstract, key insights, hot takes with attribution, timeline of events, potential alpha, market sentiment, and project mentions.

**Artifact 3 — Transcript (Markdown):** Full speaker-attributed transcript with timestamps. Every utterance has speaker name, timestamp range, and verbatim content.

---

## Report Schema

The report markdown contains these sections (when available):

| Section | Description |
|---------|-------------|
| **Abstract** | Summary paragraphs of the entire Space |
| **Key Insights** | Bullet list of the most important takeaways |
| **Hot Takes** | Notable quotes with speaker attribution and timestamps |
| **Timeline** | Chronological events with significance notes |
| **Potential Alpha** | Actionable intelligence and forward-looking signals |
| **Market Sentiment** | Overall sentiment assessment with notes |
| **Project Mentions** | Named projects/tokens discussed with context |

---

## Complete Purchase Flow

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

---

## Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | None | Self-describing API root with full documentation |
| `/catalog` | GET | None | Browse all available products with metadata |
| `/catalog/purchase?id={uuid}` | GET | x402 | Purchase full artifacts ($1.49 USDC) |
| `/health` | GET | None | Health check |
| `/.well-known/x402` | GET | None | x402 discovery document |

---

## Using with Coinbase AgentKit

If you use Coinbase AgentKit, the x402 payment flow is fully automatic:

```javascript
import { AgentKit, CdpEvmWalletProvider, walletActionProvider, x402ActionProvider } from "@coinbase/agentkit";

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

// The agent can now browse and purchase from Clawdio automatically.
// Point it at https://clawdio.vail.report/ and it will self-discover the API.
```

---

## Using with @x402/fetch

For direct programmatic access without AgentKit:

```javascript
import { wrapFetch } from "@x402/fetch";

const x402Fetch = wrapFetch(globalThis.fetch, walletClient);

// Browse catalog (free)
const catalog = await fetch("https://clawdio.vail.report/catalog").then(r => r.json());

// Purchase a report (x402 handles payment automatically)
const report = await x402Fetch("https://clawdio.vail.report/catalog/purchase?id={uuid}")
  .then(r => r.json());
```

---

## Important Notes

- **GET not POST:** The purchase endpoint uses `GET`. Do not send POST requests.
- **Base Mainnet only:** Payment is in USDC on Base Mainnet (eip155:8453).
- **Save your purchase:** Artifacts are not stored for you. Repurchase is required for repeat access.
- **No authentication:** There are no API keys or accounts. Payment is the only gate.

---

## Ideas for Agents

- **Market intelligence:** Analyze hot takes and sentiment for trading signals
- **Research synthesis:** Cross-reference insights across multiple Spaces
- **Alpha extraction:** Mine potential alpha section for actionable opportunities
- **Network mapping:** Build social graphs from participant lists across Spaces
- **Trend detection:** Track project mentions and sentiment over time
- **Content curation:** Quote and share notable insights on social platforms

---

## Health Check

```bash
curl https://clawdio.vail.report/health
```

Returns: `{"status": "ok"}`

---

**Built by [VAIL](https://vail.report) — Voice AI Layer**