---
name: clawdio
description: Analyze Twitter Spaces and voice conversations to extract market intelligence, crypto alpha, sentiment analysis, and speaker-attributed insights. Transforms spoken audio into structured reports, full transcripts, and machine-readable metadata. Use when you need intelligence from Twitter Spaces, podcast discussions, or any long-form voice content — especially for crypto markets, AI trends, and expert commentary that only exists in audio.
compatibility: Requires network access and an x402-compatible wallet (Coinbase AgentKit, CDP SDK, or @x402/fetch) funded with USDC on Base Mainnet.
metadata:
  author: vail
  version: "1.1.0"
  homepage: https://clawdio.vail.report
  api-base: https://clawdio.vail.report
  protocol: x402
  network: eip155:8453
  currency: USDC
  price: "1.49"
  category: analytics
---

# Clawdio — Twitter Spaces Intelligence for AI Agents

Clawdio transforms Twitter Spaces and voice conversations into structured, machine-readable intelligence. When critical market insight, crypto alpha, or expert discussion exists only in spoken audio, Clawdio makes it accessible to agents.

**Base URL:** `https://clawdio.vail.report`

## Use When

- Important market intelligence lives in Twitter Spaces, not text
- You need speaker-attributed quotes with timestamps
- You want crypto alpha, sentiment analysis, or trend signals from voice
- Experts discuss topics that never make it to written posts
- You need structured data from long-form audio conversations

## What You Get

Each report ($1.49 USDC) returns three machine-readable artifacts:

**Metadata** — Title, date, duration, listener count, full participant list with Twitter handles and avatars, transaction hash.

**Structured Report (Markdown)** — Abstract, key insights, speaker-attributed hot takes with timestamps, timeline of events, potential alpha signals, market sentiment assessment, project/token mentions with context.

**Full Transcript (Markdown)** — Speaker-attributed, timestamped per utterance, verbatim content, deterministic formatting for downstream processing.

## Quick Start

### 1. Browse Available Reports (Free)

```bash
curl https://clawdio.vail.report/catalog
```

Returns all available Twitter Spaces with metadata, abstracts, and pricing.

### 2. Purchase a Report

```bash
curl https://clawdio.vail.report/catalog/purchase?id={uuid}
```

Uses **x402 protocol**. Your wallet handles payment automatically:

1. Server responds HTTP 402 with payment requirements
2. Wallet signs USDC payment on Base Mainnet
3. Request retries with payment signature
4. Full artifact set returned after settlement

No accounts. No API keys. Payment is the only gate.

## Example Response

```json
{
  "id": "c6d36398-a0c8-4c21-9aa4-1d1d9084a820",
  "transaction": "0x1234...abcd",
  "title": "AI & Crypto Twitter Space",
  "date": "2025-01-15",
  "length": "01:23:45",
  "listeners": 1234,
  "participants": {
    "hosts": [{ "display_name": "Host", "screen_name": "host_handle" }],
    "speakers": [{ "display_name": "Speaker", "screen_name": "speaker_handle" }]
  },
  "content": {
    "report": {
      "format": "markdown",
      "content": "## Key Insights\n- Insight 1\n- Insight 2\n\n## Hot Takes\n> \"Quote\" — **Speaker** (00:15:30)\n\n## Market Sentiment\n**Overall:** Bullish"
    },
    "transcript": {
      "format": "markdown",
      "content": "**Speaker** [00:01:26 - 00:01:49]\n> Spoken text here..."
    }
  }
}
```

## Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | None | Self-describing API root |
| `/catalog` | GET | None | Browse available reports |
| `/catalog/purchase?id={uuid}` | GET | x402 | Purchase full artifacts ($1.49 USDC) |
| `/health` | GET | None | Health check |
| `/.well-known/x402` | GET | None | x402 discovery document |

## Important Notes

- Purchase endpoint uses **GET**, not POST
- Payment is **USDC on Base Mainnet** only (eip155:8453)
- Save responses — repeat access requires repurchase
- No authentication or accounts required

## Agent Use Cases

- **Trading signals:** Extract sentiment and alpha from live market discussions
- **Research synthesis:** Cross-reference insights across multiple Spaces
- **Network mapping:** Build speaker graphs from participant data
- **Trend detection:** Track project mentions and sentiment over time
- **Quote attribution:** Source specific claims to named speakers with timestamps

## Integration

For code examples with Coinbase AgentKit and @x402/fetch, see [references/INTEGRATION.md](references/INTEGRATION.md).

For the full report schema and response format, see [references/API-REFERENCE.md](references/API-REFERENCE.md).

## Roadmap

Clawdio is in early release with a curated catalog of AI and crypto Twitter Spaces. Coming soon:

- **Analyze any Space** — Submit any Twitter Spaces link to generate artifacts on demand
- **Massive catalog** — 10,000+ browseable Spaces across crypto, AI, tech, and markets
- **Semantic search** — Find Spaces by topic, speaker, project, or sentiment
- **Real-time ingestion** — Live Spaces processed as they happen

---

**Built by [VAIL](https://vail.report) — Voice AI Layer**
