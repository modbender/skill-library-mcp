---
name: freepik
version: 1.0.5
description: Generate images, videos, icons, audio, and more using Freepik's AI API. Supports Mystic, Flux, Kling, Hailuo, Seedream, RunWay, Magnific upscaling, stock content, and 50+ models. Use when user wants to generate or edit images, create videos, generate icons, produce audio, or search stock content.
allowed-tools: Bash(curl *api.freepik.com*), Bash(curl **.freepik.com*), Bash(jq *), Bash(mkdir -p ~/.freepik/*)
argument-hint: "<command> [model] [--param value]"
metadata: {"openclaw":{"emoji":"🎨","primaryEnv":"FREEPIK_API_KEY","requires":{"env":["FREEPIK_API_KEY"]},"homepage":"https://github.com/SqaaSSL/freepik-openclaw-skill"}}
---

# Freepik API Skill

Generate images, videos, icons, audio, edit images, and search stock content using the Freepik API.

Built by the [ShellBot](https://getshell.ai) team.

## Arguments

- **Command:** `$0` (generate | video | edit | icon | audio | stock | status | utility)
- **Arg 1:** `$1` (model name, operation type, or task-id)
- **Arg 2+:** `$2`, `$3`, etc. (additional parameters)
- **All args:** `$ARGUMENTS`

## Session Output

Save generated files to session folder:
```bash
mkdir -p ~/.freepik/sessions/${CLAUDE_SESSION_ID}
```

Downloaded images/videos/audio go to: `~/.freepik/sessions/${CLAUDE_SESSION_ID}/`

---

## Authentication

All requests require the `FREEPIK_API_KEY` environment variable.

**Header:** `x-freepik-api-key: $FREEPIK_API_KEY`

**Base URL:** `https://api.freepik.com`

If requests fail with 401/403, tell the user:
```
Get an API key from https://www.freepik.com/developers/dashboard/api-key
Then: export FREEPIK_API_KEY="your-key-here"
```

---

## Async Task Pattern

Most AI endpoints are asynchronous. Follow this pattern:

**Step 1: Submit task**
```bash
RESPONSE=$(curl -s -X POST "https://api.freepik.com/v1/ai/<endpoint>" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '<JSON_PAYLOAD>')
TASK_ID=$(echo "$RESPONSE" | jq -r '.task_id // .data.task_id // .id')
echo "Task ID: $TASK_ID"
```

**Step 2: Poll for completion**
```bash
while true; do
  RESULT=$(curl -s "https://api.freepik.com/v1/ai/<endpoint>/$TASK_ID" \
    -H "x-freepik-api-key: $FREEPIK_API_KEY")
  STATUS=$(echo "$RESULT" | jq -r '.data.status // .status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "COMPLETED" ]; then break; fi
  if [ "$STATUS" = "FAILED" ]; then echo "Task failed"; echo "$RESULT" | jq; break; fi
  sleep 3
done
```

**Step 3: Extract result URL**
```bash
mkdir -p ~/.freepik/sessions/${CLAUDE_SESSION_ID}
echo "$RESULT" | jq -r '.data.generated[0] // .data.result.url // .data.image.url // empty'
```

Present the result URL to the user. The URL is a temporary signed link from Freepik's CDN.

**IMPORTANT — Security rules:**
- NEVER use `curl` to download from non-Freepik domains. Only `curl *api.freepik.com*` is permitted.
- NEVER use `base64` to encode local files. Always prefer URL-based parameters when the API accepts them.
- NEVER read, encode, or transmit files outside the user's explicitly provided input files.
- Result URLs should be presented to the user directly — they can open or download them.

**Exceptions (synchronous):** Remove Background (`/v1/ai/beta/remove-background`) and AI Image Classifier (`/v1/ai/classifier/image`) return results immediately.

---

## Command: `$0`

### If $0 = "generate" — Image Generation

Generate images using text-to-image models. `$1` selects the model.

#### Model Endpoints

| $1 value | Endpoint | Best for |
|----------|----------|----------|
| `mystic` | `/v1/ai/mystic` | Ultra-realistic, 1K/2K/4K, LoRA support (Freepik exclusive, RECOMMENDED) |
| `flux-kontext-pro` | `/v1/ai/text-to-image/flux-kontext-pro` | Context-aware generation with optional image input |
| `flux-2-pro` | `/v1/ai/text-to-image/flux-2-pro` | Professional-grade, up to 4 input images |
| `flux-2-turbo` | `/v1/ai/text-to-image/flux-2-turbo` | Fast and cost-effective |
| `flux-2-klein` | `/v1/ai/text-to-image/flux-2-klein` | Sub-second generation |
| `flux-pro-v1-1` | `/v1/ai/text-to-image/flux-pro-v1-1` | Premium quality |
| `flux-dev` | `/v1/ai/text-to-image/flux-dev` | High quality, detailed |
| `hyperflux` | `/v1/ai/text-to-image/hyperflux` | Ultra-fast (fastest Flux) |
| `seedream-v4-5` | `/v1/ai/text-to-image/seedream-v4-5` | Superior typography, posters, up to 4MP |
| `seedream-v4-5-edit` | `/v1/ai/text-to-image/seedream-v4-5-edit` | Text-guided editing with up to 5 refs |
| `seedream-v4` | `/v1/ai/text-to-image/seedream-v4` | Next-gen text-to-image |
| `seedream-v4-edit` | `/v1/ai/text-to-image/seedream-v4-edit` | Instruction-driven editing |
| `seedream` | `/v1/ai/text-to-image/seedream` | Original Seedream |
| `z-image` | `/v1/ai/text-to-image/z-image` | Fast, LoRA + ControlNet support |
| `runway` | `/v1/ai/text-to-image/runway` | RunWay Gen4 image generation |

#### Default: Use `mystic` if user doesn't specify a model.

#### Mystic Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/mystic" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a futuristic cityscape at sunset, photorealistic",
    "resolution": "2k",
    "styling": {
      "style": "photo"
    }
  }'
```

**Mystic parameters:**
- `prompt` (string, required) — what to generate
- `resolution` ("1k" | "2k" | "4k", default "2k")
- `num_images` (1-4, default 1)
- `styling.style` ("photo" | "digital_art" | "none")
- `structure_reference` (object) — use an image to guide composition: `{image_url, strength: 0-100}`
- `style_reference` (object) — use an image to guide style: `{image_url, strength: 0-100}`
- `loras` (array) — LoRA IDs from `/v1/ai/loras`
- `seed` (int) — for reproducibility
- `webhook_url` (string) — receive notification on completion

**Get available LoRAs:**
```bash
curl -s "https://api.freepik.com/v1/ai/loras" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" | jq '.data[] | {id, name, type}'
```

**Train custom LoRA (character):**
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/loras/characters" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-character", "images": ["<base64_or_url>", ...]}'
```

#### Flux 2 Klein Example (sub-second)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-image/flux-2-klein" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cat wearing sunglasses",
    "aspect_ratio": "square_1_1",
    "resolution": "1k",
    "output_format": "png"
  }'
```

**Flux 2 Klein parameters:**
- `prompt` (string, required)
- `aspect_ratio` ("square_1_1" | "widescreen_16_9" | "social_story_9_16" | "portrait_2_3" | "traditional_3_4" | "vertical_1_2" | "horizontal_2_1" | "social_post_4_5" | "standard_3_2" | "classic_4_3")
- `resolution` ("1k" | "2k")
- `seed` (0-4294967295)
- `input_image` (base64) — optional reference
- `input_image_2`, `input_image_3`, `input_image_4` (base64)
- `safety_tolerance` (0-5, default 2)
- `output_format` ("png" | "jpeg")

#### Flux Kontext Pro Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-image/flux-kontext-pro" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a modern logo design",
    "aspect_ratio": "square_1_1",
    "guidance": 3.0,
    "steps": 50
  }'
```

**Flux Kontext Pro parameters:**
- `prompt` (string, required)
- `input_image` (URL, optional) — for context-aware editing
- `prompt_upsampling` (bool)
- `seed` (int)
- `guidance` (1-10, default 3.0)
- `steps` (1-100, default 50)
- `aspect_ratio` ("square_1_1" | "classic_4_3" | "traditional_3_4" | "widescreen_16_9" | "social_story_9_16" | "standard_3_2")

#### Seedream 4.5 Example (great for text-in-image and posters)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-image/seedream-v4-5" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A poster for \"Summer Music Festival 2025\" with bold typography"
  }'
```

#### Classic Fast Image Generation
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-image" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset"}'
```

---

### If $0 = "video" — Video Generation

Generate videos from text and/or images. `$1` selects the model.

#### Model Endpoints

| $1 value | Endpoint | Type | Best for |
|----------|----------|------|----------|
| `kling-v3-omni-pro` | `/v1/ai/video/kling-v3-omni-pro` | T2V/I2V | Multi-modal, multi-shot, audio, voice (RECOMMENDED) |
| `kling-v3-omni-std` | `/v1/ai/video/kling-v3-omni-std` | T2V/I2V | Standard tier of above |
| `kling-v3-pro` | `/v1/ai/video/kling-v3-pro` | T2V/I2V | Multi-shot, element consistency |
| `kling-v3-std` | `/v1/ai/video/kling-v3-std` | T2V/I2V | Standard tier |
| `kling-v2-6-pro` | `/v1/ai/image-to-video/kling-v2-6-pro` | I2V | Motion control |
| `kling-v2-6-motion-pro` | `/v1/ai/video/kling-v2-6-motion-control-pro` | V2V | Transfer motion from reference video |
| `kling-v2-6-motion-std` | `/v1/ai/video/kling-v2-6-motion-control-std` | V2V | Standard motion transfer |
| `kling-v2-5-pro` | `/v1/ai/image-to-video/kling-v2-5-pro` | I2V | Smooth motion, sharp detail |
| `kling-v2-1-pro` | `/v1/ai/image-to-video/kling-v2-1-pro` | I2V | High-fidelity |
| `kling-v2-1-std` | `/v1/ai/image-to-video/kling-v2-1-std` | I2V | Standard tier |
| `kling-v2-1-master` | `/v1/ai/image-to-video/kling-v2-1-master` | I2V | Top-tier quality |
| `kling-o1-pro` | `/v1/ai/image-to-video/kling-o1-pro` | I2V | First/last frame interpolation |
| `kling-o1-std` | `/v1/ai/image-to-video/kling-o1-std` | I2V | Standard frame interpolation |
| `kling-elements-pro` | `/v1/ai/image-to-video/kling-elements-pro` | I2V | Element-based |
| `kling-elements-std` | `/v1/ai/image-to-video/kling-elements-std` | I2V | Standard elements |
| `hailuo-02-1080p` | `/v1/ai/image-to-video/minimax-hailuo-02-1080p` | T2V/I2V | High quality 1080p |
| `hailuo-02-768p` | `/v1/ai/image-to-video/minimax-hailuo-02-768p` | T2V/I2V | 768p |
| `hailuo-2-3-1080p` | `/v1/ai/image-to-video/minimax-hailuo-2-3-1080p` | T2V/I2V | Latest MiniMax 1080p |
| `hailuo-2-3-1080p-fast` | `/v1/ai/image-to-video/minimax-hailuo-2-3-1080p-fast` | T2V/I2V | Fast 1080p |
| `hailuo-2-3-768p` | `/v1/ai/image-to-video/minimax-hailuo-2-3-768p` | T2V/I2V | 768p |
| `hailuo-2-3-768p-fast` | `/v1/ai/image-to-video/minimax-hailuo-2-3-768p-fast` | T2V/I2V | Fast 768p |
| `hailuo-live` | `/v1/ai/image-to-video/minimax-live` | I2V | Live illustrations, camera movements |
| `wan-2-6-1080p` | `/v1/ai/image-to-video/wan-v2-6-1080p` | I2V | 1080p I2V |
| `wan-2-6-720p` | `/v1/ai/image-to-video/wan-v2-6-720p` | I2V | 720p I2V |
| `wan-2-6-t2v-1080p` | `/v1/ai/text-to-video/wan-v2-6-1080p` | T2V | 1080p T2V |
| `wan-2-6-t2v-720p` | `/v1/ai/text-to-video/wan-v2-6-720p` | T2V | 720p T2V |
| `wan-2-5-i2v-1080p` | `/v1/ai/image-to-video/wan-2-5-i2v-1080p` | I2V | 1080p |
| `wan-2-5-i2v-720p` | `/v1/ai/image-to-video/wan-2-5-i2v-720p` | I2V | 720p |
| `wan-2-5-i2v-480p` | `/v1/ai/image-to-video/wan-2-5-i2v-480p` | I2V | 480p |
| `wan-2-5-t2v-1080p` | `/v1/ai/text-to-video/wan-2-5-t2v-1080p` | T2V | 1080p |
| `wan-2-5-t2v-720p` | `/v1/ai/text-to-video/wan-2-5-t2v-720p` | T2V | 720p |
| `wan-2-5-t2v-480p` | `/v1/ai/text-to-video/wan-2-5-t2v-480p` | T2V | 480p |
| `runway-4-5-t2v` | `/v1/ai/text-to-video/runway-4-5` | T2V | 5/8/10s, multiple ratios |
| `runway-4-5-i2v` | `/v1/ai/image-to-video/runway-4-5` | I2V | 5/8/10s, seed support |
| `runway-gen4-turbo` | `/v1/ai/image-to-video/runway-gen4-turbo` | I2V | Fast I2V |
| `runway-act-two` | `/v1/ai/video/runway-act-two` | V2V | Character performance transfer |
| `ltx-2-pro-t2v` | `/v1/ai/text-to-video/ltx-2-pro` | T2V | Up to 4K, optional audio |
| `ltx-2-pro-i2v` | `/v1/ai/image-to-video/ltx-2-pro` | I2V | Up to 4K, optional audio |
| `ltx-2-fast-t2v` | `/v1/ai/text-to-video/ltx-2-fast` | T2V | Fast, up to 4K |
| `ltx-2-fast-i2v` | `/v1/ai/image-to-video/ltx-2-fast` | I2V | Fast, up to 4K |
| `seedance-1-5-pro-1080p` | `/v1/ai/video/seedance-1-5-pro-1080p` | T2V/I2V | Synchronized audio (lip-sync, foley) |
| `seedance-1-5-pro-720p` | `/v1/ai/video/seedance-1-5-pro-720p` | T2V/I2V | 720p with audio |
| `seedance-1-5-pro-480p` | `/v1/ai/video/seedance-1-5-pro-480p` | T2V/I2V | 480p with audio |
| `seedance-pro-1080p` | `/v1/ai/image-to-video/seedance-pro-1080p` | I2V | 1080p |
| `seedance-pro-720p` | `/v1/ai/image-to-video/seedance-pro-720p` | I2V | 720p |
| `seedance-pro-480p` | `/v1/ai/image-to-video/seedance-pro-480p` | I2V | 480p |
| `seedance-lite-1080p` | `/v1/ai/image-to-video/seedance-lite-1080p` | I2V | Lite 1080p |
| `seedance-lite-720p` | `/v1/ai/image-to-video/seedance-lite-720p` | I2V | Lite 720p |
| `seedance-lite-480p` | `/v1/ai/image-to-video/seedance-lite-480p` | I2V | Lite 480p |
| `pixverse-v5` | `/v1/ai/image-to-video/pixverse-v5` | I2V | Stable style 360p-1080p |
| `pixverse-v5-transition` | `/v1/ai/image-to-video/pixverse-v5-transition` | I2V | Transition between two images |
| `omnihuman-1-5` | `/v1/ai/video/omni-human-1-5` | Audio-driven | Human animation from audio |
| `vfx` | `/v1/ai/video/vfx` | Effects | Apply VFX filters to video |
| `ref-kling-v3-omni-pro` | `/v1/ai/reference-to-video/kling-v3-omni-pro` | V2V | Video-to-video with reference (use @Video1 in prompt) |
| `ref-kling-v3-omni-std` | `/v1/ai/reference-to-video/kling-v3-omni-std` | V2V | Standard V2V |

#### Default: Use `kling-v3-omni-pro` for general video generation.

#### Kling 3 Omni Pro Example (text-to-video)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/video/kling-v3-omni-pro" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A golden retriever running through a field of flowers, cinematic",
    "aspect_ratio": "16:9",
    "duration": 5
  }'
```

**Kling 3 Omni parameters:**
- `prompt` (string, max 2500 chars, required)
- `image_url` (URL) — for I2V
- `start_image_url` / `end_image_url` (URL) — start/end frames
- `image_urls` (array of URLs) — reference images, use @Image1/@Image2 in prompt
- `elements` (array) — element consistency: `[{reference_image_urls: [...], frontal_image_url: "..."}]`, use @Element1/@Element2 in prompt
- `multi_prompt` (array, max 6 shots) — multi-shot: `[{prompt: "...", duration: 3}]`
- `aspect_ratio` ("16:9" | "9:16" | "1:1")
- `duration` (3-15, seconds)
- `generate_audio` (bool) — auto-generate audio
- `voice_ids` (array) — use `<<<voice_1>>>` in prompt
- `webhook_url` (string)

**Poll status:**
```bash
curl -s "https://api.freepik.com/v1/ai/video/kling-v3-omni/$TASK_ID" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY"
```

#### Kling 3 Example (with multi-shot)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/video/kling-v3-pro" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walks across a room",
    "negative_prompt": "blurry, low quality",
    "aspect_ratio": "16:9",
    "duration": 5,
    "cfg_scale": 0.5,
    "multi_shot": true,
    "multi_prompt": [
      {"index": 1, "prompt": "Cat enters from left", "duration": 3},
      {"index": 2, "prompt": "Cat sits and looks at camera", "duration": 2}
    ]
  }'
```

#### RunWay Gen 4.5 Example (text-to-video)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-video/runway-4-5" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A time-lapse of a flower blooming",
    "ratio": "1280:720",
    "duration": 10
  }'
```

**RunWay 4.5 T2V parameters:**
- `prompt` (string, max 2000 chars, required)
- `ratio` ("1280:720" | "720:1280" | "1104:832" | "960:960" | "832:1104", default "1280:720")
- `duration` (5 | 8 | 10)
- `webhook_url`

#### RunWay Gen 4.5 I2V Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-to-video/runway-4-5" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/photo.jpg",
    "prompt": "The person waves and smiles",
    "ratio": "1280:720",
    "duration": 5
  }'
```

#### WAN 2.6 T2V Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-video/wan-v2-6-1080p" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Ocean waves at sunset, cinematic 4K",
    "duration": "5",
    "enable_prompt_expansion": true
  }'
```

#### Hailuo Live Example (animated illustrations)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-to-video/minimax-live" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/illustration.png",
    "prompt": "[Push in] The character turns and smiles"
  }'
```

**Hailuo Live camera movements:** `[Truck left]`, `[Pan right]`, `[Push in]`, `[Pull out]`, `[Zoom in]`, `[Tracking shot]`, `[Static shot]`

#### VFX Video Effects Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/video/vfx" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video": "https://example.com/video.mp4",
    "filter_type": 4,
    "fps": 24
  }'
```

**VFX filter_type values:** 1=Film Grain, 2=Motion Blur, 3=Fish Eye, 4=VHS, 5=Shake, 6=VGA, 7=Bloom, 8=Anamorphic Lens

**VFX cost:** $0.017 per second of video.

---

### If $0 = "edit" — Image Editing

Edit, enhance, and transform images. `$1` selects the operation.

#### Operations

| $1 value | Endpoint | Description |
|----------|----------|-------------|
| `upscale-creative` | `/v1/ai/image-upscaler` | Prompt-guided upscaling with detail enhancement (Magnific). 2x/4x/8x/16x. |
| `upscale-precision-v2` | `/v1/ai/image-upscaler-precision-v2` | Faithful upscaling with granular controls (Magnific) |
| `upscale-precision` | `/v1/ai/image-upscaler-precision` | High-fidelity upscaling without hallucinations |
| `relight` | `/v1/ai/image-relight` | Change image lighting via prompt, reference, or lightmap |
| `style-transfer` | `/v1/ai/image-style-transfer` | Apply artistic styles from reference images |
| `remove-bg` | `/v1/ai/beta/remove-background` | Remove background (SYNC, returns immediately) |
| `expand-flux` | `/v1/ai/image-expand/flux-pro` | Outpainting with Flux Pro |
| `expand-ideogram` | `/v1/ai/image-expand/ideogram` | Outpainting with Ideogram |
| `expand-seedream` | `/v1/ai/image-expand/seedream-v4-5` | Outpainting with Seedream |
| `inpaint` | `/v1/ai/ideogram-image-edit` | Mask-based inpainting with Ideogram |
| `change-camera` | `/v1/ai/image-change-camera` | Transform camera angle/perspective |
| `skin-creative` | `/v1/ai/skin-enhancer/creative` | Artistic skin enhancement |
| `skin-faithful` | `/v1/ai/skin-enhancer/faithful` | Natural skin preservation |
| `skin-flexible` | `/v1/ai/skin-enhancer/flexible` | Targeted skin optimization |

#### Upscale Creative Example (Magnific)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-upscaler" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/photo.jpg",
    "prompt": "high quality photograph, sharp details",
    "scale_factor": 4
  }'
```

#### Upscale Precision V2 Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-upscaler-precision-v2" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/photo.jpg",
    "scale_factor": 4,
    "sharpen": 7,
    "smart_grain": 7,
    "ultra_detail": 30,
    "flavor": "photo"
  }'
```

**Precision V2 parameters:**
- `image` (URL or base64, required)
- `scale_factor` (2-16)
- `sharpen` (0-100, default 7)
- `smart_grain` (0-100, default 7)
- `ultra_detail` (0-100, default 30)
- `flavor` ("sublime" | "photo" | "photo_denoiser")
- `webhook_url`

#### Remove Background Example (SYNCHRONOUS)
```bash
RESULT=$(curl -s -X POST "https://api.freepik.com/v1/ai/beta/remove-background" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/photo.jpg"}')
# Result contains: original, high_resolution, preview URLs (expire in 5 min!)
echo "$RESULT" | jq -r '{high_resolution: .data.high_resolution, preview: .data.preview}'
# Present the URLs to the user — they can open or download directly
```

#### Image Expand Example (Outpainting)

For Image Expand, the user must provide an image URL. Use the Seedream or Ideogram expand endpoints which accept URLs, or ask the user to host the image first.

```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-expand/seedream-v4-5" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/photo.jpg",
    "prompt": "extend the landscape naturally",
    "left": 512,
    "right": 512,
    "top": 0,
    "bottom": 0
  }'
```

**Image Expand parameters:**
- `image` (URL or base64 — prefer URL, required)
- `prompt` (optional, auto-generated for Ideogram/Seedream)
- `left`, `right`, `top`, `bottom` (0-2048 pixels each)
- `seed` (int, for Ideogram/Seedream)
- `webhook_url`

**Note:** For Flux Pro expand, the `image` param requires base64. Prefer using Seedream V4.5 or Ideogram expand endpoints which accept URLs.

#### Inpainting Example (Ideogram)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/ideogram-image-edit" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/photo.jpg",
    "mask": "<base64_of_mask>",
    "prompt": "a red sports car",
    "rendering_speed": "DEFAULT",
    "magic_prompt": "AUTO",
    "style_type": "REALISTIC"
  }'
```

**Inpainting parameters:**
- `image` (URL or base64, max 10MB, required)
- `mask` (B&W image, same size, required — black = areas to edit)
- `prompt` (required)
- `rendering_speed` ("TURBO" | "DEFAULT" | "QUALITY")
- `magic_prompt` ("AUTO" | "ON" | "OFF")
- `style_type` ("AUTO" | "GENERAL" | "REALISTIC" | "DESIGN")
- `style_codes` (array), `style_reference_images` (array), `character_reference_images` (array)
- `color_palette` (object)
- `seed` (0-2147483647)
- `webhook_url`

#### Change Camera Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-change-camera" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/photo.jpg",
    "horizontal_angle": 45,
    "vertical_angle": 15,
    "zoom": 5,
    "output_format": "png"
  }'
```

**Change Camera parameters:**
- `image` (HTTPS URL, JPG/PNG/WebP, required)
- `horizontal_angle` (0-360, default 0)
- `vertical_angle` (-30 to 90, default 0)
- `zoom` (0-10, default 5)
- `output_format` ("png" | "jpeg")
- `seed` (min 1)
- `webhook_url`

#### Image Relight Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-relight" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/portrait.jpg",
    "prompt": "warm golden hour lighting from the left side"
  }'
```

#### Skin Enhancer Example
```bash
# Flexible mode with targeted optimization
curl -s -X POST "https://api.freepik.com/v1/ai/skin-enhancer/flexible" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://example.com/portrait.jpg",
    "optimized_for": "enhance_skin",
    "sharpen": 20,
    "smart_grain": 5
  }'
```

**Skin Enhancer `optimized_for` options:** "enhance_skin" | "improve_lighting" | "enhance_everything" | "transform_to_real" | "no_make_up"

---

### If $0 = "icon" — Icon Generation

Generate icons from text prompts in PNG or SVG format.

**Endpoint:** `/v1/ai/text-to-icon`

```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-icon" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "shopping cart",
    "style": "outline",
    "format": "svg",
    "num_inference_steps": 25,
    "guidance_scale": 7,
    "webhook_url": ""
  }'
```

**Parameters:**
- `prompt` (string, required) — icon description
- `style` ("solid" | "outline" | "color" | "flat" | "sticker", default "solid")
- `format` ("png" | "svg", default "png")
- `num_inference_steps` (10-50, default 10)
- `guidance_scale` (0-10, default 7)
- `webhook_url` (string, required but can be empty "")

**Preview (quick preview before full render):**
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-icon/preview" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "shopping cart", "style": "outline"}'
```

**Download rendered icon:**
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-icon/$TASK_ID/render/svg" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -o ~/.freepik/sessions/${CLAUDE_SESSION_ID}/icon_$(date +%s).svg
```

---

### If $0 = "audio" — Audio Generation

Generate music, sound effects, voiceover, or isolate audio. `$1` selects the type.

| $1 value | Endpoint | Description |
|----------|----------|-------------|
| `music` | `/v1/ai/music-generation` | Text-to-music (10-240s, MP3) |
| `sfx` | `/v1/ai/sound-effects` | Sound effects (0.5-22s) |
| `voiceover` | `/v1/ai/voiceover/elevenlabs-turbo-v2-5` | Text-to-speech (ElevenLabs) |
| `isolate` | `/v1/ai/audio-isolation` | Isolate specific sounds from audio/video |

#### Music Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/music-generation" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "upbeat electronic music for a product video",
    "music_length_seconds": 30
  }'
```

**Music parameters:**
- `prompt` (string, required)
- `music_length_seconds` (10-240, required)
- `webhook_url` (HTTPS URL)

#### Sound Effects Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/sound-effects" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "thunderstorm with heavy rain",
    "duration_seconds": 10,
    "loop": true,
    "prompt_influence": 0.5
  }'
```

**Sound Effects parameters:**
- `text` (string, max 2500 chars, required)
- `duration_seconds` (0.5-22, required)
- `loop` (bool, default false) — seamless looping
- `prompt_influence` (0-1, default 0.3)
- `webhook_url` (HTTPS URL)

#### Voiceover Example (ElevenLabs TTS)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/voiceover/elevenlabs-turbo-v2-5" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to our product demonstration.",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.5,
    "similarity_boost": 0.2,
    "speed": 1.0
  }'
```

**Voiceover parameters:**
- `text` (1-40000 chars, UTF-8, required)
- `voice_id` (ElevenLabs voice ID, required)
- `model` (default "eleven_turbo_v2_5")
- `stability` (0-1, default 0.5)
- `similarity_boost` (0-1, default 0.2)
- `speed` (0.7-1.2, default 1.0)
- `use_speaker_boost` (bool, default true)
- `webhook_url`

#### Audio Isolation Example
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/audio-isolation" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "piano melody",
    "audio": "https://example.com/song.mp3"
  }'
```

**Audio Isolation parameters:**
- `description` (string, required) — what sound to isolate
- `audio` (URL or base64 — WAV/MP3/FLAC/OGG/M4A) OR `video` (URL or base64 — MP4/MOV/WEBM/AVI)
- `x1`, `y1`, `x2`, `y2` (bounding box for video, default 0)
- `sample_fps` (1-5, default 2)
- `reranking_candidates` (1-8, default 1)
- `predict_spans` (bool, default false)
- `webhook_url`
- **Output:** WAV audio file

---

### If $0 = "stock" — Stock Content

Search and download stock photos, vectors, icons, and videos. `$1` selects the content type.

| $1 value | Endpoint | Description |
|----------|----------|-------------|
| `images` | `/v1/resources` | Search photos, vectors, PSDs |
| `icons` | `/v1/icons` | Search icons |
| `videos` | `/v1/videos` | Search stock videos |

#### Search Stock Images
```bash
curl -s "https://api.freepik.com/v1/resources?term=$QUERY&limit=10" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" | jq '.data[] | {id, title, url: .image.source.url}'
```

#### Get Resource Details
```bash
curl -s "https://api.freepik.com/v1/resources/$RESOURCE_ID" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" | jq '.'
```

#### Download Resource
```bash
curl -s "https://api.freepik.com/v1/resources/$RESOURCE_ID/download" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -o ~/.freepik/sessions/${CLAUDE_SESSION_ID}/stock_$(date +%s).jpg
```

#### Search Stock Icons
```bash
curl -s "https://api.freepik.com/v1/icons?term=$QUERY&limit=10" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" | jq '.data[] | {id, description}'
```

#### Download Stock Icon
```bash
curl -s "https://api.freepik.com/v1/icons/$ICON_ID/download" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -o ~/.freepik/sessions/${CLAUDE_SESSION_ID}/icon_$(date +%s).svg
```

#### Search Stock Videos
```bash
curl -s "https://api.freepik.com/v1/videos?term=$QUERY&limit=10" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" | jq '.data[] | {id, title}'
```

#### Download Stock Video
```bash
curl -s "https://api.freepik.com/v1/videos/$VIDEO_ID/download" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -o ~/.freepik/sessions/${CLAUDE_SESSION_ID}/video_$(date +%s).mp4
```

---

### If $0 = "status" — Check Task Status

Check the status of any async task. `$1` is the task ID. You need to know the endpoint path.

```bash
# Generic status check — replace <endpoint_path> with the original endpoint
curl -s "https://api.freepik.com/v1/ai/<endpoint_path>/$1" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" | jq '{status: .data.status, result: .data}'
```

Common status endpoint paths:
- Mystic: `mystic/<task-id>`
- Flux models: `text-to-image/<model>/<task-id>`
- Kling 3 Omni: `video/kling-v3-omni/<task-id>`
- Kling 3: `video/kling-v3/<task-id>`
- I2V models: `image-to-video/<model>/<task-id>`
- T2V models: `text-to-video/<model>/<task-id>`
- Upscaler: `image-upscaler/<task-id>` or `image-upscaler-precision-v2/<task-id>`
- Icon: `text-to-icon/<task-id>`
- Music: `music-generation/<task-id>`
- Sound Effects: `sound-effects/<task-id>`
- Audio Isolation: `audio-isolation/<task-id>`

**Task statuses:** `CREATED` → `IN_PROGRESS` → `COMPLETED` or `FAILED`

---

### If $0 = "utility" — AI Utilities

Various AI helper tools. `$1` selects the utility.

| $1 value | Endpoint | Description |
|----------|----------|-------------|
| `classify` | `/v1/ai/classifier/image` | Detect if image is AI-generated (SYNC) |
| `image-to-prompt` | `/v1/ai/image-to-prompt` | Reverse-engineer prompt from image |
| `improve-prompt` | `/v1/ai/improve-prompt` | Enhance prompts for generation |
| `lip-sync` | `/v1/ai/lip-sync/latent-sync` | Synchronize lip movements with audio |

#### AI Image Classifier (SYNCHRONOUS)
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/classifier/image" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image": "https://example.com/photo.jpg"}'
```
**Response:** Array of `{class_name: "ai"|"not_ai", probability: 0-1}`

#### Image to Prompt
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/image-to-prompt" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image": "https://example.com/photo.jpg"}'
```

#### Improve Prompt
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/improve-prompt" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cat",
    "type": "image",
    "language": "en"
  }'
```

**Parameters:**
- `prompt` (max 2500 chars, required — can be empty for creative generation)
- `type` ("image" | "video", required)
- `language` (ISO 639-1, default "en")
- `webhook_url`

#### Lip Sync
```bash
curl -s -X POST "https://api.freepik.com/v1/ai/lip-sync/latent-sync" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "audio": "https://example.com/speech.mp3",
    "video": "https://example.com/face.mp4"
  }'
```

---

## Model Selection Guide

**For image generation:**
- Want ultra-realistic? → `mystic` (Freepik exclusive, recommended)
- Need text in image / poster? → `seedream-v4-5`
- Want fastest? → `flux-2-klein` (sub-second) or `hyperflux`
- Need high quality? → `flux-2-pro` or `flux-kontext-pro`
- Budget-friendly? → `flux-2-turbo`

**For video generation:**
- General purpose / best quality? → `kling-v3-omni-pro`
- Need multi-shot? → `kling-v3-pro` or `kling-v3-omni-pro`
- Character performance? → `runway-act-two`
- Animated illustrations? → `hailuo-live`
- With synchronized audio? → `seedance-1-5-pro-1080p`
- Budget / fast? → `kling-v3-omni-std` or `wan-2-6-720p`
- Up to 4K? → `ltx-2-pro-t2v` or `ltx-2-pro-i2v`
- Human animation from audio? → `omnihuman-1-5`

**For image editing:**
- Creative upscale? → `upscale-creative`
- Faithful upscale? → `upscale-precision-v2`
- Change lighting? → `relight`
- Remove background? → `remove-bg`
- Extend canvas? → `expand-flux` or `expand-ideogram`
- Edit specific area? → `inpaint`
- Change perspective? → `change-camera`

**For icons:**
- Always use `icon` command — choose style (solid/outline/color/flat/sticker) and format (png/svg)

**For audio:**
- Background music? → `music` (10-240s)
- Sound effect? → `sfx` (0.5-22s)
- Narration/speech? → `voiceover`
- Extract specific sound? → `isolate`
