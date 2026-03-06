---
name: Nano Banana OpenRouter Skill
description: Generate images using Google's Nano Banana (Gemini 2.5 Flash Image)
  models via OpenRouter API.
---

# Nano Banana OpenRouter Skill

Generate images using Google's **Nano Banana** (Gemini 2.5 Flash Image) models via **OpenRouter API**.

## Configuration

Add the following to your `openclaw.json` (or set the env var `OPENROUTER_API_KEY`):

```json
{
  "skills": {
    "entries": {
      "nano-banana-openrouter": {
        "enabled": true,
        "config": {
          "apiKey": "sk-or-v1-..."  
        },
        "env": {
          "OPENROUTER_API_KEY": "sk-or-v1-..."
        }
      }
    }
  }
}
```

## Usage

**Tool Name:** `nano_banana_generate`

**Examples:**
- "Generate a cyberpunk dragon using Nano Banana."
- "Draw a landscape in 16:9 aspect ratio."
- "Use the preview model to generate a logo for a coffee shop."

## Models

- **Default:** `google/gemini-2.0-flash-exp:free` (Free tier, robust text/code, experimental image support)
- **High Quality:** `google/gemini-2.5-flash-image-preview` (The specific "Nano Banana" image model, paid/credits required)

## Notes
- OpenRouter requires the `HTTP-Referer` and `X-Title` headers (included in this skill).
- `modalities: ["image"]` is sent automatically.
