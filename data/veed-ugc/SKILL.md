---
name: veed-ugc
description: Generate UGC-style promotional videos with AI lip-sync. Takes an image (person with product from Morpheus/Ad-Ready) and a script (pure dialogue), creates a video of the person speaking. Uses ElevenLabs for voice synthesis.
---

# Veed-UGC

Generate UGC (User Generated Content) style promotional videos with AI lip-sync using ComfyDeploy's Veed-UGC workflow.

## Overview

Veed-UGC transforms static images into dynamic promotional videos:
1. Takes a photo of a person with a product (from Morpheus or Ad-Ready)
2. Receives a **script** (pure dialogue text)
3. Creates a lip-synced video of the person speaking the script

Perfect for creating authentic-feeling promotional content at scale.

## API Details

**Endpoint:** `https://api.comfydeploy.com/api/run/deployment/queue`
**Deployment ID:** `627c8fb5-1285-4074-a17c-ae54f8a5b5c6`

## Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `image` | URL of person+product image | Output from Morpheus/Ad-Ready |
| `script` | Pure dialogue text | `"Hola che! Cómo anda todo por allá?"` |
| `voice_id` | ElevenLabs voice ID | Default: `PBi4M0xL4G7oVYxKgqww` |

## ⚠️ CRITICAL: Script Format

The `script` input must be **PURE DIALOGUE ONLY**:

✅ **CORRECT:**
```
Hola che! Cómo anda todo por allá? Mirá esto que acabo de probar, una locura total.
```

❌ **WRONG - No annotations:**
```
[Entusiasta] Hola che! (pausa) Cómo anda?
```

❌ **WRONG - No tone directions:**
```
Tono argentino informal: Hola che!
```

❌ **WRONG - No stage directions:**
```
*sonríe* Hola che! *levanta el producto*
```

❌ **WRONG - No titles/labels:**
```
ESCENA 1:
Hola che!
```

**Just write exactly what the person should say. Nothing else.**

## Voice IDs (ElevenLabs)

| Voice | ID | Description |
|-------|-----|-------------|
| Default | `PBi4M0xL4G7oVYxKgqww` | Main voice |

*More voices can be added from ElevenLabs*

## Usage

```bash
uv run ~/.clawdbot/skills/veed-ugc/scripts/generate.py \
  --image "https://example.com/person-with-product.png" \
  --script "Hola! Les quiero mostrar este producto increíble que acabo de probar." \
  --output "ugc-video.mp4"
```

### With local image file:
```bash
uv run ~/.clawdbot/skills/veed-ugc/scripts/generate.py \
  --image "./morpheus-output.png" \
  --script "Mirá, yo antes no usaba esto pero ahora no puedo vivir sin él." \
  --voice-id "PBi4M0xL4G7oVYxKgqww" \
  --output "promo-video.mp4"
```

## Direct API Call

```javascript
const response = await fetch("https://api.comfydeploy.com/api/run/deployment/queue", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
  },
  body: JSON.stringify({
    "deployment_id": "627c8fb5-1285-4074-a17c-ae54f8a5b5c6",
    "inputs": {
      "image": "/* put your image url here */",
      "voice_id": "PBi4M0xL4G7oVYxKgqww",
      "script": "Hola che! Cómo anda todo por allá?"
    }
  })
});
```

## Workflow Integration

### Typical Pipeline

1. **Generate image with Morpheus/Ad-Ready**
   ```bash
   uv run morpheus... --output product-shot.png
   ```

2. **Write the script** (pure dialogue)

3. **Create UGC video from the image**
   ```bash
   uv run veed-ugc... --image product-shot.png --script "..." --output promo.mp4
   ```

## Output

The workflow outputs an MP4 video file with:
- The original image animated with lip-sync
- AI-generated voiceover from the script
- Natural head movements and expressions

## Notes

- Image should clearly show a person's face (frontal or 3/4 view works best)
- Script is spoken **exactly as written** - no interpretation
- Video length depends on script length
- Processing time: ~2-5 minutes depending on script length
