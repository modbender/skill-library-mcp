---
name: perstudio
description: Studio-grade AI image and video generation — photorealistic portraits, product shots, stickers, animations, and more. Just describe what you want.
user-invocable: true
homepage: https://perstudio.ai
repository: https://github.com/montenegronyc/perstudio-openclaw
version: 3.2.1
metadata: {"openclaw":{"requires":{"env":["PERSTUDIO_API_KEY"],"config":["plugins.entries.perstudio.config.apiKey"]},"primaryEnv":"PERSTUDIO_API_KEY","install":[{"id":"npm","kind":"node","package":"perstudio-openclaw","global":true,"label":"Install perstudio-openclaw"}],"emoji":"🎨"}}
---

# Perstudio — AI Image & Video Generation

Generate images, videos, and audio with natural language. Just describe what you want and perstudio routes it to the right model automatically.

All generation costs tokens. Check balance with the `balance` action. Token packs available at https://perstudio.ai/pricing.

## Quick Start

```
perstudio({ action: "generate_sync", intent: "a golden retriever puppy in a field of sunflowers, studio lighting" })
```

Takes 15-90 seconds.

## What You Can Do

| Capability | Input Required | Token Cost |
|-----------|----------------|------------|
| Text to Image | None | 250 |
| Image to Image | Image | 250 |
| Product Photography | None | 370 |
| Portrait / Avatar | None | 370 |
| Upscale (4x) | Image | 120 |
| Inpainting | Image + Mask | 250 |
| Style Transfer | Reference Image | 370 |
| Sticker / Icon | Reference Image | 250 |
| Video | Varies | 2200 |
| Text to Speech | Voice Reference | 490 |

## Examples

### Generate an image
```
perstudio({ action: "generate_sync", intent: "a cyberpunk cityscape at sunset, neon lights reflecting on wet streets" })
```

### Transform an existing image
```
perstudio({ action: "upload_asset", file_path: "~/Pictures/input.jpg" })
// Returns: { asset_id: "abc123" }

perstudio({ action: "generate_sync", intent: "transform into a watercolor painting", input_image_asset_id: "abc123" })
```

> **Security note:** `upload_asset` only accepts files from allowed directories: `~/Pictures`, `~/Downloads`, `~/Desktop`, `~/.openclaw/workspace`, and the system temp directory. Paths outside these directories are rejected.

### Generate video
```
perstudio({ action: "generate_sync", intent: "a cat playing piano, cinematic lighting" })
```

### Animate a still image
```
perstudio({ action: "upload_asset", file_path: "~/Pictures/photo.jpg" })
perstudio({ action: "generate_sync", intent: "gentle wind blowing through hair, subtle movement", input_image_asset_id: "abc123" })
```

### Check balance
```
perstudio({ action: "balance" })
```

## Tips

- **Just describe what you want** — the system picks the best approach automatically.
- **Be specific** — include style, lighting, and composition details for better results.
- **Auto-upscale** — pass `auto_upscale: true` to automatically enhance resolution.

## Security

- **File access is restricted.** The `upload_asset` action enforces a directory allowlist — only files in `~/Pictures`, `~/Downloads`, `~/Desktop`, `~/.openclaw/workspace`, and the system temp directory can be uploaded. All other paths are rejected. Paths are resolved to their real location (following symlinks) before validation to prevent traversal attacks.
- **API key required.** All generation requests require a valid `PERSTUDIO_API_KEY`. No data is sent to perstudio.ai without authentication.
- **Open source.** The plugin source code is available at [github.com/montenegronyc/perstudio-openclaw](https://github.com/montenegronyc/perstudio-openclaw) for full review.

## Setup

1. Sign up at [perstudio.ai](https://perstudio.ai)
2. Create an API key in your dashboard
3. Install: `npm install -g perstudio-openclaw`
4. Configure your API key:
   ```
   openclaw config set plugins.entries.perstudio.config.apiKey '"your-api-key"'
   ```
5. Start generating!
