# @translateimage/clawhub-skill

[ClawHub](https://clawhub.ai) skill for [TranslateImage](https://translateimage.io) — AI-powered image translation, OCR, and text removal.

## Overview

This skill lets any [OpenClaw](https://openclaw.ai)-compatible AI agent use TranslateImage's REST API directly via curl — no MCP server required.

- Translate text in images while preserving the original layout
- Extract text from images using OCR with bounding boxes
- Remove text from images using AI inpainting

## Requirements

- `curl` (available on macOS, Linux, Windows WSL by default)
- A TranslateImage API key

## Setup

1. Sign up at [translateimage.io](https://translateimage.io)
2. Go to **Settings → API Keys**, create a key, and enable the required scopes
3. Set the environment variable:

```bash
export TRANSLATEIMAGE_API_KEY=your-api-key
```

OpenClaw will prompt you to set this automatically when the skill is first invoked.

## Installation

### Via OpenClaw CLI

```bash
claw skill install translateimage
```

### Manual

Copy `SKILL.md` into your OpenClaw skills directory:

```bash
mkdir -p ~/.openclaw/skills/translateimage
cp SKILL.md ~/.openclaw/skills/translateimage/
```

## API Endpoints

| Tool | Endpoint | Scope |
|---|---|---|
| Translate Image | `POST /api/translate` | `translate` |
| Extract Text (OCR) | `POST /api/ocr` | `ocr` |
| Remove Text | `POST /api/remove-text` | `remove-text` |
| Image to Text (AI) | `POST /api/image-to-text` | `image-to-text` |

All requests go to `https://translateimage.io` with `Authorization: Bearer $TRANSLATEIMAGE_API_KEY`.

## Quick Example

```bash
# Translate a local image to English
curl -X POST https://translateimage.io/api/translate \
  -H "Authorization: Bearer $TRANSLATEIMAGE_API_KEY" \
  -F "image=@manga-page.jpg" \
  -F 'config={"target_lang":"en","translator":"gemini-2.5-flash","font":"WildWords"}'
```

See [`SKILL.md`](./SKILL.md) for full usage with curl examples, response formats, Shopify integration, and error handling.

## Development

```bash
# Validate SKILL.md before publishing
pnpm validate

# Publish to ClawHub
pnpm publish:skill

# Dry run
pnpm publish:skill:dry-run
```

## License

Proprietary - All rights reserved. See [translateimage.io](https://translateimage.io) for terms.
