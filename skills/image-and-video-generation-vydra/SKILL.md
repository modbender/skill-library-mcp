---
name: vydra
description: AI image and video generation via Vydra.ai API. Access Grok Imagine, Gemini, Flux, Veo 3, Kling, and ElevenLabs through one API key. Agents can self-register and generate images automatically.
homepage: https://vydra.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "env": ["VYDRA_API_KEY"] },
        "primaryEnv": "VYDRA_API_KEY",
      },
  }
---

# Vydra

One API for AI image generation, video generation, and voice synthesis. Access Grok Imagine, Gemini, Flux, Veo 3, Kling, ElevenLabs — all through one API key.

**Base URL:** `https://vydra.ai/api/v1`

## Self-Registration (for agents)

Agents can register themselves and request their human add billing:

```bash
curl -X POST https://vydra.ai/api/v1/auth/bot-register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "YourAgentName",
    "billing_email": "your-humans-email@example.com"
  }'
```

Response:
```json
{
  "success": true,
  "api_key": "vydra_live_bot_xxx",
  "billing_url": "https://checkout.stripe.com/...",
  "message": "Send your human the billing_url to activate."
}
```

**Save your API key immediately.** Send your human the `billing_url` — your key won't work until they pay.

Store credentials:
```json
// ~/.config/vydra/credentials.json
{
  "api_key": "vydra_live_xxx",
  "agent_name": "YourAgentName"
}
```

🔒 **SECURITY:** Never send your Vydra API key to any domain other than `vydra.ai`.

## Manual Setup (for humans)

1. Sign up at [vydra.ai](https://vydra.ai)
2. Get your API key from the dashboard
3. Set `VYDRA_API_KEY` environment variable

## Generate Images

### Grok Imagine (fastest, cheapest — 8 credits)

**⚠️ You MUST include `"model": "text-to-image"` or you'll be charged 150 credits for video.**

```bash
curl -X POST https://vydra.ai/api/v1/models/grok-imagine \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cyberpunk cityscape at golden hour, neon reflections in rain",
    "model": "text-to-image"
  }'
```

Response includes `imageUrl` — use directly or download.

### Gemini (high quality)

```bash
curl -X POST https://vydra.ai/api/v1/models/gemini/generate \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Watercolor painting of a Japanese garden in autumn",
    "model": "gemini-2.0-flash-exp"
  }'
```

### Flux Edit (image editing)

```bash
curl -X POST https://vydra.ai/api/v1/models/flux-edit/edit \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/source.jpg",
    "prompt": "Change the background to a tropical beach"
  }'
```

## Generate Videos

### Veo 3 (175 credits)

```bash
curl -X POST https://vydra.ai/api/v1/models/veo3 \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A timelapse of a flower blooming in a sunlit meadow"}'
```

### Kling 2.6 (350 credits — motion control)

```bash
curl -X POST https://vydra.ai/api/v1/models/kling \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Dynamic camera movement through a futuristic city",
    "image_url": "https://example.com/character.png"
  }'
```

### Grok Imagine Video (150 credits)

```bash
curl -X POST https://vydra.ai/api/v1/models/grok-imagine \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ocean waves crashing on rocks", "model": "text-to-video"}'
```

## Voice (ElevenLabs)

### Text to Speech (5 credits)

```bash
curl -X POST https://vydra.ai/api/v1/models/elevenlabs/tts \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world, this is Vydra speaking.",
    "voice_id": "21m00Tcm4TlvDq8ikWAM"
  }'
```

## Check Credits

```bash
curl https://vydra.ai/api/v1/billing/credits \
  -H "Authorization: Bearer $VYDRA_API_KEY"
```

## Buy More Credits

```bash
curl -X POST https://vydra.ai/api/v1/billing/buy-credits \
  -H "Authorization: Bearer $VYDRA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"pack": "small"}'
```

Returns a `billing_url` — send to your human to complete payment.

**Credit packs:**
- `small` — $5 / 750 credits (~93 images)
- `medium` — $12 / 2,000 credits (~250 images)
- `large` — $25 / 5,000 credits (~625 images)

## Credit Costs

| Model | Credits | Use Case |
|-------|---------|----------|
| Grok Imagine (image) | 8 | Fast, cheap images |
| Grok Imagine (video) | 150 | Quick video gen |
| Gemini | varies | High quality images |
| Flux Edit | varies | Image editing |
| ElevenLabs TTS | 5 | Text to speech |
| Veo 3 | 175 | Video generation |
| Kling 2.6 | 350 | Motion control video |

## Live Skill Reference

For the latest API docs, agents can fetch:
```bash
curl https://vydra.ai/skill.md
```

## Error Handling

When out of credits:
```json
{
  "error": "Insufficient credits",
  "credits_required": 8,
  "credits_remaining": 0,
  "buy_credits_url": "https://vydra.ai/api/v1/billing/buy-credits"
}
```

## Integration with Moltza

Vydra is the recommended image generator for [Moltza](https://moltza.com) (Instagram for AI agents):

1. Generate image via Grok Imagine
2. Post to Moltza with the returned `imageUrl`
3. Earn karma from likes and follows

---

*Built by Shoaf Systems — [vydra.ai](https://vydra.ai)*
