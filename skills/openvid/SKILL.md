---
name: "Skill: openvid"
description: AI motion graphics video generation service. Send a prompt + URL,
  receive a branded explainer video.
---

# Skill: openvid

## Description
AI motion graphics video generation service. Send a prompt + URL, receive a branded explainer video.

**Pricing:** $5–$20 with volume discounts (15s, 30s, 60s, 90s)

**This is a SERVICE skill** — it calls an external API. No code execution, no local files modified.

---

## Privacy & Data

- **What you send:** Prompt text and (optionally) a public URL for brand extraction
- **What happens:** The service fetches the URL, extracts brand colors/fonts/logo, generates video
- **Data retention:** Videos stored on Cloudflare R2 for 7 days, then deleted
- **Recommendation:** Only send **public URLs**. Do not send internal/private URLs or sensitive text.

---

## x402 Payment Flow

This skill uses the **x402 HTTP payment protocol** — a standard for pay-per-call APIs.

### How It Works

1. **Request** → You POST to the API
2. **402 Response** → API returns payment requirements (amount, wallet address, chain)
3. **Pay** → Your agent/wallet sends payment on-chain (USDC on Base or SOL on Solana)
4. **Retry with proof** → Re-send request with `X-Payment` header containing the signed transaction
5. **Job created** → API returns `jobId`, you poll until complete

### Who Signs Payments?

**Your agent's wallet signs payments, not this skill.** 

The skill only documents the API. Payment signing is handled by:
- Your agent's wallet infrastructure (e.g., OpenClaw's built-in wallet)
- x402-compatible libraries (`@x402/fetch`, `@x402/client`)
- Manual wallet signing if calling directly

**No private keys are needed or requested by this skill.**

---

## API Reference

**Gateway:** `https://gateway.openvid.app`

### Create Video

```http
POST /v1/video/generate
Content-Type: application/json

{
  "prompt": "Make a video about Stripe https://stripe.com",
  "duration": 30
}
```

**First response (402 Payment Required):**
```json
{
  "error": "Payment Required",
  "price": "$10",
  "duration": 30,
  "options": {
    "baseUsdc": {
      "network": "eip155:8453",
      "asset": "USDC",
      "amount": "10000000",
      "payTo": "0xc0A11946195525c5b6632e562d3958A2eA4328EE"
    },
    "solanaSol": {
      "network": "solana:mainnet",
      "asset": "SOL",
      "amount": "116000000",
      "payTo": "DzQB5aqnq8myCGm166v6AfWkJ4fsEq9HdWqhFLX6LQfi"
    }
  }
}
```

**After payment, retry with X-Payment header:**
```http
POST /v1/video/generate
Content-Type: application/json
X-Payment: <base64-encoded-payment-proof>

{
  "prompt": "Make a video about Stripe https://stripe.com",
  "duration": 30
}
```

**Success response:**
```json
{
  "jobId": "abc-123",
  "status": "processing",
  "pollUrl": "https://gateway.openvid.app/v1/jobs/abc-123"
}
```

### Poll Job Status

```http
GET /v1/jobs/{jobId}
```

**Response (completed):**
```json
{
  "jobId": "abc-123",
  "status": "completed",
  "videoUrl": "https://api.openvid.app/api/renders/...",
  "productName": "Stripe",
  "duration": 30
}
```

---

## Pricing

| Duration | Price |
|----------|-------|
| 15s | $5 |
| 30s | $10 |
| 60s | $15 |
| 90s | $20 |

---

## ACP (Virtuals Protocol)

For agent-to-agent commerce via Virtuals Protocol:
- **Agent ID:** `1869`
- **Wallet:** `0xc0A11946195525c5b6632e562d3958A2eA4328EE`

---

## Best Practices

- **Include a public URL** for accurate brand extraction
- **Be specific** about what the video should communicate
- **Shorter is better** — 15-30s videos have highest quality
- **Never send private/internal URLs** — all URLs are fetched by the service
