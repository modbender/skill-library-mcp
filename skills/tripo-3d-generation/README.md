# Tripo 3D — AI 3D Model Generation for OpenClaw

Generate 3D models from text or images using [Tripo AI](https://www.tripo3d.ai/), the most advanced AI 3D generation platform. **10 free credits included — no API key needed to start.**

## Quick Start

### Install

```bash
clawhub install tripo-3d
```

### Generate Your First 3D Model

Just ask your AI assistant:

> "Generate a 3D model of a wooden chair"

That's it! The skill handles everything — task creation, progress polling, and delivering download links.

## Features

- **Text to 3D** — Describe any object and get a 3D model
- **Image to 3D** — Convert photos into 3D models
- **10 Free Credits** — Start generating immediately, no setup required
- **Multiple Formats** — GLB, FBX, OBJ, STL
- **Latest Model** — Uses Tripo v3.0-20250812 by default (best stable quality)
- **Async Generation** — Submit tasks and poll for results, no blocking

## Usage

### Text-to-3D

```
User: "Create a 3D model of a medieval sword with a jeweled hilt"
AI: Creating your 3D model... Task ID: task_abc123
AI: [polls status...] Progress: 45%
AI: Done! Here's your 3D model: [download link]
    (Free credits remaining: 8/10)
```

### Image-to-3D

```
User: "Convert this image to a 3D model: https://example.com/shoe.jpg"
AI: Converting image to 3D... Task ID: task_def456
AI: Done! Download your model here: [link]
```

### Check Credits

```
User: "How many free Tripo credits do I have left?"
AI: You have 7 free credits remaining out of 10.
```

## After Free Credits

When your 10 free credits are used up, you can continue with your own Tripo API key:

1. **Sign up** at [platform.tripo3d.ai](https://platform.tripo3d.ai/) (free, takes 1 minute)
2. **Get your API key** at [platform.tripo3d.ai/api-keys](https://platform.tripo3d.ai/api-keys)
   - Click "Generate New API Key"
   - Copy the key immediately (it starts with `tsk_` and only shows once!)
3. **Configure the skill**:

```bash
openclaw config set skill.tripo-3d.TRIPO_API_KEY tsk_your_key_here
```

New Tripo accounts get **2,000 free credits** (worth $20) — so you'll have plenty to work with.

## Model Versions

| Version | Speed | Quality | Best For |
|---------|-------|---------|----------|
| `Turbo-v1.0-20250506` | ~5-10s | Good | Fastest prototyping |
| `v3.1-20260211` | ~60-100s | Highest | Newest (may be unstable) |
| `v3.0-20250812` (default) | ~90s | Highest stable | Production-quality models |
| `v2.5-20250123` | ~25-30s | High | Quick iterations |
| `v2.0-20240919` | ~20s | High | Accurate geometry |
| `v1.4-20240625` | ~10s | Good | Legacy, realistic textures |

To use a different version, just mention it: "Generate a 3D robot using Tripo v2.5-20250123"

## Output Formats

| Format | Best For |
|--------|----------|
| GLB (default) | Web, game engines, AR/VR |
| FBX | Maya, 3ds Max, Unity |
| OBJ | Universal exchange |
| STL | 3D printing |

## What is Tripo?

[Tripo](https://www.tripo3d.ai/) is the most advanced AI-powered 3D generation platform, offering:

- Text-to-3D and Image-to-3D generation
- Multi-view reconstruction for high-fidelity models
- Automatic rigging and 100+ preset animations
- Stylization (cartoon, clay, steampunk, etc.)
- Post-processing (polycount control, format conversion)

Used by professionals in gaming, architecture, e-commerce, 3D printing, and more. Trusted by Makerworld, Layer AI, and Nilo Technologies.

## Links

- [Tripo Website](https://www.tripo3d.ai/)
- [API Platform](https://platform.tripo3d.ai/)
- [API Documentation](https://platform.tripo3d.ai/docs/generation)
- [Pricing](https://www.tripo3d.ai/pricing)
- [Discord Community](https://discord.gg/chrV6rjAfY)

## License

MIT
