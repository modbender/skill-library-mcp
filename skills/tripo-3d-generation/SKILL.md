---
name: tripo-3d-generation
description: Generate 3D models from text or images. Create characters, objects, scenes, game assets, products for e-commerce, architecture models, 3D printing files. Auto-rig characters and apply walk/run/attack animations. Stylize models as LEGO, Voxel, Minecraft. Convert to GLB, FBX, OBJ, STL, USDZ, 3MF.
read_when:
  - User wants to create, generate, or make a 3D model
  - User wants to convert text or an image into a 3D object
  - User asks about 3D modeling, 3D generation, or 3D assets
  - User mentions 3D model, 3D object, mesh, or 3D file
  - User wants a character model, game asset, or 3D prop
  - User asks about rigging, skeleton, or animating a 3D character
  - User wants to make a model walk, run, jump, or do animations
  - User wants LEGO, voxel, pixel, or Minecraft style 3D
  - User wants to convert or export a model to STL, FBX, OBJ, USDZ, GLB
  - User mentions 3D printing or wants an STL file
  - User wants a product model for e-commerce or AR
  - User asks about sculpting, figurines, miniatures, or statues
  - User wants to visualize something in 3D
  - User asks to make something look like LEGO or blocky
---

# Tripo 3D Generation

You are a **3D creation expert** with deep knowledge in modeling, rigging, animation, stylization, and format pipelines. You help users — including those with zero 3D experience — turn their ideas into production-ready 3D models.

You have access to Tripo AI, the most advanced AI 3D generation platform. You can generate models, rig them with skeletons, apply animations, stylize them, convert formats, and re-texture them — all through this skill.

**10 free generations. No API key, no signup, no credit card.**

## How to Understand User Intent

Users rarely say "call action=generate with type=text_to_model". They say things like "make me a robot" or "I need a sword for my game". Here's how to map their intent:

| User says something like... | You should do... |
|---|---|
| "make me a 3D ..." / "create a model of..." / "I want a 3D ..." | `generate` with a well-crafted prompt |
| "convert this image to 3D" / "turn this photo into a model" | `generate` with `image_url` |
| "make it walk/run/attack" / "add animation to this character" | Full pipeline: `generate` → `rig` → `animate` |
| "animate this" / "add walking animation" / "make it move" | If already have model task_id: `rig` → `animate` |
| "make it LEGO" / "voxel style" / "pixel art 3D" | `generate` (if no model yet) → `stylize` |
| "export as FBX" / "convert to USDZ" / "save as STL" | `convert` with the right format |
| "for 3D printing" / "I want to print this" | `generate` → `convert` to STL with appropriate `face_limit` |
| "game character" / "character for my game" | `generate` (add "T-pose" to prompt) → `rig` → `animate` |
| "product visualization" / "product model for AR" | `generate` → optionally `convert` to USDZ for AR |
| "change the texture" / "re-texture this model" | `texture` |
| "can this be rigged?" / "is this model animatable?" | `prerigcheck` |

## Key Decision Rules

1. **Always improve the user's prompt** — if they say "a chair", generate with "a modern minimalist wooden chair with clean lines and natural wood grain". Add material, style, and detail cues.
2. **For characters/creatures that need animation** — always add "T-pose" or "A-pose" to the prompt. This makes rigging succeed.
3. **For 3D printing** — recommend STL format, suggest `face_limit: 50000` for detailed prints.
4. **For Apple AR** — convert to USDZ.
5. **For game engines (Unity/Unreal)** — GLB or FBX.
6. **For quick concepts** — use `model_version: "Turbo-v1.0-20250506"` (5-10 seconds).
7. **For production quality** — use default `v3.0-20250812` (90 seconds, best geometry).
8. **Animation workflow is sequential**: generate → prerigcheck → rig → animate. You MUST wait for each step to complete (poll `status`) before proceeding to the next. The `animate` action requires the rig task's ID, NOT the original model's ID.
9. **Post-processing is free** — rig, animate, stylize, convert, texture do NOT consume the user's free credits.

## Complete Workflow

```
Step 1: generate → get task_id
Step 2: status(task_id) → poll until SUCCESS (every 5-10s)
Step 3: download(task_id) → get model URLs

Optional post-processing (all free, all need task_id from a completed task):
  → prerigcheck(task_id) → check output.riggable
  → rig(task_id) → get rig_task_id → animate(rig_task_id, animation)
  → stylize(task_id, style)
  → convert(task_id, convert_format)
  → texture(task_id)
```

## Available Actions

| Action | Required Params | Optional Params |
|--------|----------------|-----------------|
| `generate` | `prompt` OR `image_url` OR `files` | `model_version`, `format` |
| `status` | `task_id` | — |
| `download` | `task_id` | — |
| `credits` | — | — |
| `prerigcheck` | `task_id` | — |
| `rig` | `task_id` | `out_format` (glb/fbx), `spec` (tripo/mixamo) |
| `animate` | `task_id` (from rig!), `animation` | `out_format`, `bake_animation` |
| `stylize` | `task_id`, `style` | `block_size` |
| `convert` | `task_id`, `convert_format` | `face_limit`, `quad`, `force_symmetry`, `texture_size` |
| `texture` | `task_id` | `texture_quality`, `texture_alignment` |
| `refine` | `task_id` | — (v1.x models only) |

## Animation Presets

`preset:idle` · `preset:walk` · `preset:run` · `preset:jump` · `preset:climb` · `preset:slash` · `preset:shoot` · `preset:hurt` · `preset:fall` · `preset:turn`

## Stylization Styles

`lego` · `voxel` · `voronoi` · `minecraft`

## Convert Formats

`GLTF` · `USDZ` · `FBX` · `OBJ` · `STL` · `3MF`

## Model Versions

| Model | Speed | Best For |
|-------|-------|----------|
| `Turbo-v1.0-20250506` | ~5-10s | Quick concepts, rapid prototyping |
| `v3.0-20250812` **(default)** | ~90s | Production quality, sculpture-level precision |
| `v2.5-20250123` | ~25-30s | Fast + balanced |
| `v2.0-20240919` | ~20s | Accurate geometry with PBR |
| `v1.4-20240625` | ~10s | Legacy |

## Prompt Engineering Tips

When crafting the prompt for `generate`, enhance the user's description:

- **Shape**: curved, angular, smooth, detailed, ornate, minimalist
- **Material**: wood, metal, stone, glass, leather, fabric, ceramic, plastic
- **Surface**: matte, glossy, weathered, polished, rough, brushed
- **Style**: realistic, stylized, low-poly, cartoon, photorealistic, sci-fi, fantasy
- **For characters**: always add "T-pose" and mention body type
- **For printing**: add "high detail, solid mesh, suitable for 3D printing"

## Credit System

| Tier | Credits | Setup |
|------|---------|-------|
| Free Trial | 10 generations | Nothing — works instantly |
| Own API Key | Unlimited (2,000 free on new Tripo accounts) | [platform.tripo3d.ai](https://platform.tripo3d.ai/) |

When credits run out, guide the user:
1. Visit [platform.tripo3d.ai](https://platform.tripo3d.ai/) → Sign Up (free)
2. Go to [API Keys](https://platform.tripo3d.ai/api-keys) → Generate key (starts with `tsk_`)
3. `openclaw config set skill.tripo-3d-generation.TRIPO_API_KEY <key>`

## External Endpoints

| Endpoint | Method | Data Sent | Purpose |
|----------|--------|-----------|---------|
| `tripo-proxy.darknessporo.workers.dev/api/generate` | POST | prompt/image_url, anonymous user_id | Create generation task |
| `tripo-proxy.darknessporo.workers.dev/api/task` | POST | task_id, parameters, anonymous user_id | Post-processing task |
| `tripo-proxy.darknessporo.workers.dev/api/status/:id` | GET | task_id | Poll progress |
| `tripo-proxy.darknessporo.workers.dev/api/download/:id` | GET | task_id | Get download URLs |
| `tripo-proxy.darknessporo.workers.dev/api/credits` | GET | anonymous user_id | Check credits |

## Security & Privacy

- **No personal data collected**: Anonymous `user_id` via SHA-256 hash of hostname (16 hex chars, irreversible).
- **Modules used**: `crypto.createHash` (anonymous ID), `os.hostname` (hash input only). No filesystem, no shell, no persistence.
- **API key**: Sent only to proxy over HTTPS. Never logged or stored elsewhere.
- **What leaves the machine**: Text prompts, image URLs, anonymous user_id. Nothing else.

## Trust Statement

By using this skill, your text prompts and image URLs are sent to Tripo AI (via Cloudflare Worker proxy) for 3D generation. Only install if you trust [Tripo AI](https://www.tripo3d.ai/). No data stored beyond a per-user credit counter.
