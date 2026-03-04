# fal.ai Image Generation

## Queue-Based API

fal.ai uses an async queue system:
1. Submit job → get `request_id`
2. Poll status until `COMPLETED`
3. Fetch result with image URL

The generate.py script handles polling automatically (up to 120s timeout).

## Authentication

- Header: `Authorization: Key {FAL_KEY}`
- Get key at fal.ai/dashboard

## Available Models

| Alias | fal Model ID | Notes |
|-------|-------------|-------|
| `seedream3` | `fal-ai/seedream-3.0` | Default. ByteDance, good all-around |
| `seedream4` | `fal-ai/seedream-4.0` | Newer, higher quality |
| `flux-pro` | `fal-ai/flux-pro/v1.1` | Black Forest Labs, photorealistic |
| `flux-dev` | `fal-ai/flux/dev` | Open weights version |
| `recraft-v3` | `fal-ai/recraft-v3` | Strong at design/illustration |

Pass any raw fal model ID with `--model` for models not in the alias list.

## Seed Support

Use `--seed N` for reproducible results. Same seed + same prompt = same image.

## Tips

- SeedReam models excel at Asian aesthetics and anime styles
- Flux Pro is best for photorealism
- Recraft V3 is strong for graphic design, logos, and illustrations
