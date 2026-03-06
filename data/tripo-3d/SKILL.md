---
name: Tripo 3D Generation
description: Turn text or images into production-ready 3D models with
  sculpture-level geometry, sharp edges, and PBR materials — in under 90
  seconds.
---

# Tripo 3D Generation

Turn text or images into production-ready 3D models with **sculpture-level geometry**, sharp edges, and PBR materials — in under 90 seconds.

**10 free generations included. No API key, no signup, no credit card.**

## Features

- **Text-to-3D**: Describe any object in natural language → get a production-ready 3D model
- **Image-to-3D**: Upload a single photo → AI reconstructs it in full 3D with accurate geometry
- **Multiview-to-3D**: Provide multiple angle photos → reconstruct with higher accuracy
- **Sculpture-Level Geometry**: Industry-leading mesh quality with sharp edges, clean topology, and precise surface detail
- **PBR Materials**: Physically-based rendering textures (albedo, normal, roughness, metallic) out of the box
- **Auto-Rigging**: AI-powered automatic skeleton binding — turn any humanoid model into an animatable character in seconds
- **10 Animation Presets**: Walk, run, jump, climb, slash, shoot, idle, hurt, fall, turn — applied directly through the skill
- **Stylization**: Transform models into LEGO, Voxel, Voronoi, or Minecraft styles
- **Format Conversion**: Convert to GLTF, USDZ, FBX, OBJ, STL, 3MF — ready for any pipeline
- **Re-Texturing**: Apply new textures with standard or detailed quality
- **Quad Mesh Output**: Clean quad topology for subdivision workflows (Maya, Blender, ZBrush)
- **Auto Real-World Scale**: Automatically sizes models to real-world dimensions (meters)

## All Actions

| Action | Description | Credit Cost |
|--------|-------------|-------------|
| `generate` | Create a 3D model from text, image, or multiview | 1 free credit |
| `status` | Check task progress (0-100%) | Free |
| `download` | Get model download URLs | Free |
| `credits` | Check remaining free credits | Free |
| `prerigcheck` | Check if model can be rigged | Free |
| `rig` | Auto-rig with skeleton (Tripo or Mixamo spec) | Free |
| `animate` | Apply animation preset to rigged model | Free |
| `stylize` | Transform to LEGO/Voxel/Voronoi/Minecraft | Free |
| `convert` | Convert to GLTF/USDZ/FBX/OBJ/STL/3MF | Free |
| `texture` | Re-texture a model | Free |
| `refine` | Refine draft model (v1.x models only) | Free |

## Quick Start

### Text-to-3D

```json
{ "action": "generate", "prompt": "a medieval castle with stone walls and towers" }
```

### Image-to-3D

```json
{ "action": "generate", "image_url": "https://example.com/photo.jpg" }
```

### Check Progress & Download

```json
{ "action": "status", "task_id": "your-task-id" }
{ "action": "download", "task_id": "your-task-id" }
```

## Full Animation Pipeline

Create animated characters in 4 steps — all through this skill:

```
1. generate(prompt="knight in plate armor, T-pose") → model_task_id
2. prerigcheck(task_id=model_task_id)              → riggable? ✓
3. rig(task_id=model_task_id)                      → rig_task_id
4. animate(task_id=rig_task_id, animation="preset:walk") → animated model!
```

### Animation Presets

| Animation | Description |
|-----------|-------------|
| `preset:idle` | Standing idle loop |
| `preset:walk` | Walking cycle |
| `preset:run` | Running cycle |
| `preset:jump` | Jump animation |
| `preset:climb` | Climbing motion |
| `preset:slash` | Melee attack swing |
| `preset:shoot` | Ranged attack |
| `preset:hurt` | Hit reaction |
| `preset:fall` | Falling animation |
| `preset:turn` | Turning in place |

### Rigging Options

| Spec | Description |
|------|-------------|
| `tripo` (default) | Tripo skeleton — optimized for quality |
| `mixamo` | Mixamo-compatible skeleton — works with Adobe Mixamo library |

## Stylization

Transform any model into artistic styles:

```json
{ "action": "stylize", "task_id": "model-task-id", "style": "lego" }
```

| Style | Description |
|-------|-------------|
| `lego` | Brick-built appearance |
| `voxel` | Blocky, voxelized aesthetic |
| `voronoi` | Organic cellular pattern |
| `minecraft` | Minecraft-style blocky look |

Adjust `block_size` (default 80) — larger values = coarser blocks.

## Format Conversion

Convert models to any format for your pipeline:

```json
{ "action": "convert", "task_id": "model-task-id", "convert_format": "STL" }
```

| Format | Extension | Best For |
|--------|-----------|----------|
| GLTF | .gltf | Web, three.js, Babylon.js |
| USDZ | .usdz | Apple AR Quick Look, Vision Pro |
| FBX | .fbx | Animation, Maya, 3ds Max, Unity, Unreal |
| OBJ | .obj | Universal exchange, Blender, ZBrush |
| STL | .stl | 3D printing (FDM, SLA, resin) |
| 3MF | .3mf | Advanced 3D printing with color/material data |

Optional: `face_limit` (default 10000), `quad` (bool), `force_symmetry` (bool), `texture_size` (default 4096)

## Model Versions

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `Turbo-v1.0-20250506` | ~5-10s | ★★★☆☆ | Fastest prototyping, concept exploration |
| `v3.0-20250812` **(default)** | ~90s | ★★★★★ | Production assets, sculpture-level precision, sharp edges |
| `v2.5-20250123` | ~25-30s | ★★★★☆ | Fast + balanced, good for quick iterations |
| `v2.0-20240919` | ~20s | ★★★★☆ | Accurate geometry with PBR materials |
| `v1.4-20240625` | ~10s | ★★★☆☆ | Legacy, realistic textures |

## Use Case Examples

### Game Character with Animation

```json
{ "action": "generate", "prompt": "a stylized warrior character in T-pose, suitable for rigging", "model_version": "v3.0-20250812" }
```
→ then `rig` → then `animate` with `preset:slash` for a melee attack!

### E-Commerce Product in USDZ for Apple AR

```json
{ "action": "generate", "prompt": "premium wireless headphone, matte black with rose gold accents" }
```
→ then `convert` with `convert_format: "USDZ"` for Apple AR Quick Look

### 3D Printing Miniature

```json
{ "action": "generate", "prompt": "tabletop miniature of a dwarf warrior, high detail", "format": "stl" }
```
→ or generate as GLB, then `convert` to `STL` with custom `face_limit: 50000`

### LEGO-Style Art

```json
{ "action": "generate", "prompt": "a cute penguin" }
```
→ then `stylize` with `style: "lego"` for a LEGO brick version

## Prompt Tips for Best Results

### Be Specific About Shape & Material
- **Good**: "a weathered wooden rocking chair with curved armrests and woven seat"
- **Bad**: "a chair"

### For Animatable Characters
- Use "T-pose" or "A-pose" in the prompt
- Human/humanoid shapes work best for rigging

### Include Material Details
- "matte black finish", "brushed aluminum", "rough stone texture"

## Credit System

| Tier | Credits | Setup |
|------|---------|-------|
| **Free Trial** | 10 generations | Nothing — works instantly |
| **Own API Key** | Unlimited (2,000 free credits on new Tripo accounts) | Sign up at [platform.tripo3d.ai](https://platform.tripo3d.ai/) |

Post-processing (rig, animate, stylize, convert, texture) is **always free** and does not consume credits.

### Getting Your Own Key

1. Visit [platform.tripo3d.ai](https://platform.tripo3d.ai/) → Sign Up (free)
2. Go to [API Keys page](https://platform.tripo3d.ai/api-keys)
3. Generate a new key (starts with `tsk_`) — **copy immediately, shown only once!**
4. Configure: `openclaw config set skill.tripo-3d-generation.TRIPO_API_KEY <your-key>`

## Why Tripo?

| Feature | Tripo | Others |
|---------|-------|--------|
| Geometry Quality | Sculpture-level, sharp edges | Often blobby or low-detail |
| Auto-Rigging + Animation | Built-in skeleton + 10 animation presets | Usually requires manual work |
| Stylization | LEGO/Voxel/Voronoi/Minecraft built-in | Not available |
| Speed | 5s (Turbo) to 90s (v3.0) | Often 3-10+ minutes |
| Export Formats | 6 formats (GLB/FBX/OBJ/STL/USDZ/3MF) | Usually 1-2 formats |
| PBR Materials | Albedo + Normal + Roughness + Metallic | Often diffuse-only |
| Free Credits | 10 free, no signup needed | Most require API key upfront |
| Post-Processing | Rig/Animate/Stylize/Convert all free | Extra charges per operation |

## About Tripo

[Tripo](https://www.tripo3d.ai/) is the most advanced AI 3D generation platform by VAST AI Research. Supports the full 3D creation pipeline: generation → rigging → animation → stylization → format conversion → export.
