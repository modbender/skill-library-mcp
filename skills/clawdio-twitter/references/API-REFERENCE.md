# API Reference

Complete API documentation for Clawdio.

**Base URL:** `https://clawdio.vail.report`

## Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | None | Self-describing API root with full documentation |
| `/catalog` | GET | None | Browse all available products with metadata |
| `/catalog/purchase?id={uuid}` | GET | x402 | Purchase full artifacts ($1.49 USDC) |
| `/health` | GET | None | Health check |
| `/.well-known/x402` | GET | None | x402 discovery document |

## GET /catalog

No payment or authentication required. Returns all available products with metadata.

### Response

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

## GET /catalog/purchase?id={uuid}

Purchases the full artifact set for a specific product. Requires x402 payment.

**Important:** This is a **GET** request, not POST.

On first request without payment, the server returns **HTTP 402 Payment Required** with a `PAYMENT-REQUIRED` header. Your x402 wallet automatically handles the payment flow (see [INTEGRATION.md](INTEGRATION.md) for details).

### Response

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

### Artifact Breakdown

**Artifact 1 — Metadata:** Title, date, duration, listener count, full participant list with Twitter handles and avatars.

**Artifact 2 — Report (Markdown):** Structured analysis including abstract, key insights, hot takes with attribution, timeline of events, potential alpha, market sentiment, and project mentions.

**Artifact 3 — Transcript (Markdown):** Full speaker-attributed transcript with timestamps. Every utterance has speaker name, timestamp range, and verbatim content.

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

## GET /health

Health check endpoint.

### Response

```json
{ "status": "ok" }
```

## GET /

Self-describing API root. Returns the full API description, available endpoints, pricing, and purchase flow instructions in a format designed for agent consumption.

## GET /.well-known/x402

x402 protocol discovery document. Returns payment configuration for automated wallet integration.

## Payment Details

| Property | Value |
|----------|-------|
| Protocol | x402 |
| Network | Base Mainnet (eip155:8453) |
| Currency | USDC |
| Price | $1.49 per report |
| Auth | None — payment is the only gate |