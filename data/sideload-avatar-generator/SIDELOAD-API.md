# Sideload 3D Avatar Generation — API Reference

**Source:** https://sideload.gg/agents/raw

---

## Overview

Generate 3D avatars programmatically from text or images. Pay per request with x402 (USDC on Base).

- **Base URL:** `https://sideload.gg`
- **Cost:** $2 USDC per generation
- **Payment:** x402 protocol (USDC on Base, chain ID 8453)
- **Rate Limit:** 10 per 30 min per wallet
- **Output Formats:** GLB, VRM, MML, processed PNG

---

## Endpoints

### 1. Generate Avatar
```
POST /api/agent/generate
```

**Headers:**
- `Content-Type: application/json`
- `x-payment: <x402_payment_token>`

**Body — Text prompt:**
```json
{
  "type": "text",
  "prompt": "A cyberpunk samurai with glowing red armor"
}
```

**Body — Image reference:**
```json
{
  "type": "image",
  "imageUrl": "https://example.com/character.png"
}
```

**Response (200):**
```json
{
  "success": true,
  "jobId": "avt-a1b2c3d4",
  "status": "processing",
  "statusUrl": "/api/agent/generate/avt-a1b2c3d4/status"
}
```

### 2. Poll Status
```
GET /api/agent/generate/{jobId}/status
```
No auth required.

**Processing:**
```json
{
  "jobId": "avt-a1b2c3d4",
  "status": "processing",
  "step": "generating_model",
  "progress": 50
}
```

**Completed:**
```json
{
  "jobId": "568525e8-c930-4e1c-b616-dddfe76374c1",
  "status": "completed",
  "result": {
    "glbUrl": "https://aimml.sideload.gg/models/568525e8-xxx.glb",
    "vrmUrl": "https://aimml.onrender.com/api/download/568525e8-xxx/vrm",
    "mmlUrl": "https://aimml.sideload.gg/mml/568525e8-xxx",
    "processedImageUrl": "https://aimml.sideload.gg/images/568525e8-xxx_processed.png"
  }
}
```

---

## Error Codes

| Status | Meaning |
|--------|---------|
| 400 | Invalid input |
| 402 | Payment required (no x402 header) |
| 429 | Rate limited (check Retry-After) |
| 503 | Service unavailable |

---

## Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `glbUrl` | URL | 3D model in GLB format — for rendering engines |
| `vrmUrl` | URL | Avatar in VRM format — for VRM viewers and apps |
| `mmlUrl` | URL | MML document URL — for metaverse environments supporting MML |
| `processedImageUrl` | URL | Processed reference image used for generation |

---

## Prompt Tips

**Good prompts:**
- "A steampunk engineer with leather tool belt, copper mechanical arm, weathered pilot hat"
- "An anime-style sorceress with long silver hair, glowing purple eyes, ornate golden staff"
- "A futuristic soldier in white and blue power armor with glowing energy shield"

**Image tips:**
- PNG, JPG, or WebP
- Publicly accessible URL
- Front-facing portraits or full-body shots work best
- Clear outlines, distinct clothing/features

---

## Integration Flow

```
1. POST /api/agent/generate  (with x402 payment)
   → Get jobId + statusUrl

2. GET /api/agent/generate/{jobId}/status  (poll every 5s)
   → Wait for status: "completed"

3. Use result URLs (glbUrl, vrmUrl, mmlUrl)
   → Render, download, embed in metaverse
```
