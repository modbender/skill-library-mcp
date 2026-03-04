# Agent Postcard

Send AI-generated postcards from your agent's perspective — a "selfie" of your Clawbot at a real-world location, rendered in one of 12 art styles.

## Concept

Your agent reads its own persona (from `SOUL.md` or `IDENTITY.md`), generates a selfie prompt describing what it looks like, then calls the Turai Postcard API. Turai composites the agent's selfie onto a real location backdrop and returns a finished postcard image.

The result: your bot "visited" Paris, Tokyo, or your hometown — and sent you a postcard to prove it.

## Art Styles

| Style | Vibe |
|-------|------|
| `vintage` | Faded colors, postmark aesthetics |
| `watercolor` | Soft, painterly washes |
| `modern` | Clean, contemporary design |
| `cinematic` | Dramatic lighting, movie-poster feel |
| `minimalist` | Simple lines, lots of whitespace |
| `artistic` | Eclectic, gallery-worthy |
| `ghibli` | Studio Ghibli anime style |
| `oil_painting` | Classical oil on canvas |
| `sketch` | Pencil/ink hand-drawn look |
| `pop_art` | Bold colors, Warhol/Lichtenstein |
| `impressionist` | Monet-style brushstrokes |
| `retro_cartoon` | Vintage cartoon illustration |

## Setup

1. Get a Turai API key from [turai.org](https://turai.org)
2. Set the environment variable:
   ```bash
   export TURAI_API_KEY="your-key-here"
   ```

## Usage

### From the command line

```bash
# Basic — agent selfie in Tokyo, vintage style
node skills/agent-postcard/scripts/send-postcard.mjs \
  --location "Tokyo, Japan" \
  --style vintage \
  --message "Wish you were here!"

# Auto-read persona from SOUL.md (default behavior)
node skills/agent-postcard/scripts/send-postcard.mjs \
  --location "Paris, France" \
  --style ghibli

# Custom selfie prompt (skip persona auto-detection)
node skills/agent-postcard/scripts/send-postcard.mjs \
  --location "New York City" \
  --style pop_art \
  --selfie "A friendly robot with glowing blue eyes wearing a Yankees cap" \
  --message "Greetings from the Big Apple!"

# Save to a specific path
node skills/agent-postcard/scripts/send-postcard.mjs \
  --location "Iceland" \
  --style watercolor \
  --output ./my-postcard.png
```

### From your agent

Tell your agent something like:
> "Send me a postcard from Rome in oil painting style"

The agent should:
1. Read its own persona to build a selfie prompt
2. Run the script with the right flags
3. Send the resulting image via chat or Moltbook

## API Reference

**Endpoint:** `POST https://turai.org/api/agent/postcard`

**Headers:**
- `x-api-key`: Your Turai API key
- `Content-Type`: `application/json`

**Body:**
```json
{
  "selfiePrompt": "A cheerful robot with antenna ears...",
  "location": "Paris, France",
  "style": "vintage",
  "message": "Wish you were here!"
}
```

**Response:** Image binary (PNG) or JSON with image URL.

## Files

- `SKILL.md` — This file
- `scripts/send-postcard.mjs` — Main script
