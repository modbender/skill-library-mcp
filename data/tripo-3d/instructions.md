# Tripo 3D — AI 3D Model Generation Skill

You have access to **Tripo AI**, the most advanced AI-powered 3D model generation platform. This skill lets you generate 3D models from text descriptions or images, rig them with skeletons, apply animations, stylize them, convert formats, and more.

Every user gets **10 free generations** with no setup required. Post-processing operations (rig, animate, stylize, convert, texture) do **not** consume free credits.

---

## When to Use This Skill

Use this skill when the user wants to:
- Create a 3D model from text or image
- Rig a character model with a skeleton for animation
- Apply preset animations (walk, run, jump, attack, etc.)
- Stylize a model (LEGO, Voxel, Voronoi, Minecraft)
- Convert a model to a different format (GLTF, USDZ, FBX, OBJ, STL, 3MF)
- Re-texture or refine a model
- Check task status or download results

## Available Actions

### Core Actions

#### `generate` — Create a 3D Model

**Text-to-3D**: Provide a `prompt`.

```json
{ "action": "generate", "prompt": "a medieval castle with stone walls and towers" }
```

**Image-to-3D**: Provide an `image_url`.

```json
{ "action": "generate", "image_url": "https://example.com/photo.jpg" }
```

**Multiview-to-3D**: Provide `files` (array of image URLs from multiple angles).

```json
{ "action": "generate", "files": ["https://example.com/front.jpg", "https://example.com/side.jpg"] }
```

Optional parameters: `model_version` (default `v3.0-20250812`), `format` (`glb`/`fbx`/`obj`/`stl`)

#### `status` — Check Task Progress

```json
{ "action": "status", "task_id": "task_abc123" }
```

Poll every 5-10 seconds until `SUCCESS` or failure.

#### `download` — Get Model URLs

```json
{ "action": "download", "task_id": "task_abc123" }
```

Returns `pbr_model_url`, `model_url`, `rendered_image_url`.

#### `credits` — Check Free Credits

```json
{ "action": "credits" }
```

### Animation Actions (Workflow: prerigcheck → rig → animate)

**IMPORTANT**: Animation requires a completed 3D model's task_id. The workflow is:

1. `generate` → get model task_id
2. `prerigcheck` → verify model can be rigged (check `output.riggable`)
3. `rig` → add skeleton (get rig task_id)
4. `animate` → apply animation preset using **rig task_id** (not the original!)

#### `prerigcheck` — Check if Model Can Be Rigged

```json
{ "action": "prerigcheck", "task_id": "model-task-id" }
```

After status is `SUCCESS`, check `output.riggable`. Only humanoid/biped models can be rigged.

#### `rig` — Auto-Rig a Model

```json
{ "action": "rig", "task_id": "model-task-id" }
```

Optional: `out_format` (`glb`/`fbx`), `spec` (`tripo`/`mixamo`)

- Use `spec: "mixamo"` if user needs Mixamo-compatible skeleton
- The rig task returns its own `task_id` — use THIS task_id for `animate`

#### `animate` — Apply Animation to Rigged Model

```json
{ "action": "animate", "task_id": "rig-task-id", "animation": "preset:walk" }
```

**CRITICAL**: `task_id` must be the RIG task's ID (from `rig` action), NOT the original model's task_id.

Available animations: `preset:idle`, `preset:walk`, `preset:run`, `preset:jump`, `preset:climb`, `preset:slash`, `preset:shoot`, `preset:hurt`, `preset:fall`, `preset:turn`

Optional: `out_format` (`glb`/`fbx`), `bake_animation` (default `true`)

### Post-Processing Actions

#### `stylize` — Stylize a Model

```json
{ "action": "stylize", "task_id": "model-task-id", "style": "lego" }
```

Available styles: `lego`, `voxel`, `voronoi`, `minecraft`

Optional: `block_size` (default 80, larger = coarser blocks)

#### `convert` — Convert Model Format

```json
{ "action": "convert", "task_id": "model-task-id", "convert_format": "FBX" }
```

Available formats: `GLTF`, `USDZ`, `FBX`, `OBJ`, `STL`, `3MF`

Optional: `face_limit` (default 10000), `quad` (bool), `force_symmetry` (bool), `texture_size` (default 4096)

#### `texture` — Re-Texture a Model

```json
{ "action": "texture", "task_id": "model-task-id" }
```

Optional: `texture_quality` (`standard`/`detailed`), `texture_alignment` (`original_image`/`geometry`)

#### `refine` — Refine a Draft Model

```json
{ "action": "refine", "task_id": "draft-model-task-id" }
```

Only works for models generated with versions < v2.0.

---

## Complete Workflow Examples

### Full Animation Pipeline

```
User: "Create an animated knight character"

1. generate(prompt="knight in full plate armor, T-pose") → model_task_id
2. Wait for status=SUCCESS
3. prerigcheck(task_id=model_task_id) → check riggable=true
4. rig(task_id=model_task_id, spec="tripo") → rig_task_id
5. Wait for rig status=SUCCESS
6. animate(task_id=rig_task_id, animation="preset:walk") → anim_task_id
7. Wait for status=SUCCESS → download animated model
```

### Stylization

```
User: "Make a LEGO version of my model"

1. stylize(task_id=existing_model_id, style="lego") → style_task_id
2. Wait for status=SUCCESS → download stylized model
```

### Format Conversion for 3D Printing

```
User: "Convert my model to STL for 3D printing"

1. convert(task_id=existing_model_id, convert_format="STL", face_limit=50000) → conv_task_id
2. Wait for status=SUCCESS → download STL file
```

---

## Model Versions

| Version | Speed | Best For |
|---------|-------|----------|
| `Turbo-v1.0-20250506` | ~5-10s | Fastest, rapid prototyping |
| `v3.1-20260211` | ~60-100s | Newest (may be unstable on some accounts) |
| `v3.0-20250812` (default) | ~90s | Best stable quality, sculpture-level precision |
| `v2.5-20250123` | ~25-30s | Fast + balanced, good for quick iterations |
| `v2.0-20240919` | ~20s | Accurate geometry with PBR materials |
| `v1.4-20240625` | ~10s | Legacy, realistic textures |

---

## Handling Quota Exceeded

When `quota_exceeded` is returned, the user has used all 10 free credits:

1. Acknowledge positively
2. Present setup steps clearly
3. Emphasize registration is **free** and takes 1-2 minutes
4. Highlight **2,000 free credits** on new Tripo accounts
5. Provide links: [Sign up](https://platform.tripo3d.ai/) · [API keys](https://platform.tripo3d.ai/api-keys)
6. Give config command: `openclaw config set skill.tripo-3d-generation.TRIPO_API_KEY <key>`
7. Remind: API key is only shown once!

---

## About Tripo

[Tripo](https://www.tripo3d.ai/) is the most advanced AI 3D generation platform by VAST AI Research. Supports the full 3D pipeline: generation → rigging → animation → stylization → format conversion → export.
