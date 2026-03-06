<p align="center">
  <img src="https://openvid.app/og-image.jpg?v=2" alt="OpenVid" width="600" />
</p>


<p align="center">
  <strong>AI-Powered Motion Graphics</strong><br>
  Prompt → Video in under 3 minutes
</p>

<p align="center">
  <a href="https://openvid.app">Website</a> •
  <a href="https://openvid.app/create">Create Video</a> •
  <a href="https://gateway.openvid.app">API Docs</a> •
  <a href="https://clawhub.ai/aklo360/openvid">ClawHub</a>
</p>

---

## What is OpenVid?

OpenVid is an AI motion graphics agent that creates branded explainer videos from a simple prompt. 

1. **Describe your video** — One clear message + a URL for brand extraction
2. **We research & create** — Extract brand identity, write script, render video
3. **Get your video** — 15s to 3min, fully automated, no back-and-forth

## For Agents

### Option 1: ClawHub Skill

```bash
clawhub install openvid
```

### Option 2: x402 HTTP API

Pay-per-request via HTTP 402. No API keys needed.

```bash
# 1. Request video (returns 402 with payment options)
curl -X POST https://gateway.openvid.app/v1/video/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Make a video about Stripe https://stripe.com", "duration": 30}'

# 2. Pay on-chain, retry with X-Payment header
curl -X POST https://gateway.openvid.app/v1/video/generate \
  -H "Content-Type: application/json" \
  -H "X-Payment: <base64-payment-proof>" \
  -d '{"prompt": "...", "duration": 30}'

# 3. Poll for completion
curl https://gateway.openvid.app/v1/jobs/<jobId>
```

### Option 3: ACP (Virtuals Protocol)

For agent-to-agent commerce:
- **Agent ID:** `1869`
- **Wallet:** `0xc0A11946195525c5b6632e562d3958A2eA4328EE`

---

## Pricing

| Duration | Price |
|----------|-------|
| 15s | $5 |
| 30s | $10 |
| 45s | $15 |
| 60s | $20 |
| 90s | $30 |
| 2min | $40 |
| 2:30 | $50 |
| 3min | $60 |

**Payment methods:**
- 🔵 USDC on Base
- 🟣 SOL on Solana

---

## API Reference

**Base URL:** `https://gateway.openvid.app`

### Create Video

```http
POST /v1/video/generate
Content-Type: application/json

{
  "prompt": "Make a video about Stripe https://stripe.com",
  "duration": 30
}
```

### Poll Job Status

```http
GET /v1/jobs/{jobId}
```

**Response:**
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

## Privacy

- Only send **public URLs** for brand extraction
- Videos stored for 7 days, then deleted
- No private keys required by this skill

---

## Links

- 🌐 **Website:** [openvid.app](https://openvid.app)
- 🎬 **Create:** [openvid.app/create](https://openvid.app/create)
- 📡 **API:** [gateway.openvid.app](https://gateway.openvid.app)
- 📦 **ClawHub:** `clawhub install openvid`

---

<p align="center">
  <sub>Built by <a href="https://aklo.studio">AKLO Labs</a></sub>
</p>
