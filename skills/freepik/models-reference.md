# Freepik API Models Reference

Complete catalog of all models and endpoints available through the Freepik API.

## Image Generation (Text-to-Image)

| Model | Endpoint | Key Features |
|-------|----------|--------------|
| Mystic | `/v1/ai/mystic` | Freepik exclusive, 1K/2K/4K, LoRA styles/characters, structure + style references |
| Flux Kontext Pro | `/v1/ai/text-to-image/flux-kontext-pro` | Context-aware, optional image input, guidance + steps control |
| Flux 2 Pro | `/v1/ai/text-to-image/flux-2-pro` | Professional-grade, up to 4 input images, 256-1440px |
| Flux 2 Turbo | `/v1/ai/text-to-image/flux-2-turbo` | Speed-optimized, lower cost, 512-2048px, PNG/JPEG |
| Flux 2 Klein | `/v1/ai/text-to-image/flux-2-klein` | Sub-second, up to 4 ref images, 10 aspect ratios, 1k/2k |
| Flux Pro 1.1 | `/v1/ai/text-to-image/flux-pro-v1-1` | Premium quality |
| Flux Dev | `/v1/ai/text-to-image/flux-dev` | High quality, detailed |
| HyperFlux | `/v1/ai/text-to-image/hyperflux` | Ultra-fast (fastest Flux model) |
| Seedream 4.5 | `/v1/ai/text-to-image/seedream-v4-5` | ByteDance, superior typography/posters, up to 4MP (4096x4096) |
| Seedream 4.5 Edit | `/v1/ai/text-to-image/seedream-v4-5-edit` | Text-guided editing, up to 5 reference images |
| Seedream 4 | `/v1/ai/text-to-image/seedream-v4` | Next-gen text-to-image |
| Seedream 4 Edit | `/v1/ai/text-to-image/seedream-v4-edit` | Instruction-driven editing (add/delete/modify/replace) |
| Seedream (original) | `/v1/ai/text-to-image/seedream` | Original Seedream model |
| Z-Image Turbo | `/v1/ai/text-to-image/z-image` | Fast, LoRA + ControlNet support |
| RunWay Gen4 | `/v1/ai/text-to-image/runway` | Photorealistic/artistic, @tag syntax for references |
| Flux Reimagine (Beta) | `/v1/ai/beta/text-to-image/reimagine-flux` | Transform images (synchronous, beta) |
| Classic Fast | `/v1/ai/text-to-image` | Classic fast generation |

### Common Aspect Ratios (Flux 2 Klein)

| Ratio | 1K Resolution | 2K Resolution |
|-------|---------------|---------------|
| square_1_1 | 1024x1024 | 2048x2048 |
| widescreen_16_9 | 1344x768 | 2688x1536 |
| social_story_9_16 | 768x1344 | 1536x2688 |
| portrait_2_3 | 832x1216 | 1664x2432 |
| traditional_3_4 | 960x1280 | 1920x2560 |
| vertical_1_2 | 704x1408 | 1408x2816 |
| horizontal_2_1 | 1408x704 | 2816x1408 |
| social_post_4_5 | 896x1152 | 1792x2304 |
| standard_3_2 | 1216x832 | 2432x1664 |
| classic_4_3 | 1280x960 | 2560x1920 |

---

## Video Generation

### Kling Models

| Model | Endpoint | Type | Duration | Features |
|-------|----------|------|----------|----------|
| Kling 3 Omni Pro | `/v1/ai/video/kling-v3-omni-pro` | T2V/I2V | 3-15s | Multi-modal, multi-shot (6), elements, audio, voice |
| Kling 3 Omni Std | `/v1/ai/video/kling-v3-omni-std` | T2V/I2V | 3-15s | Standard tier |
| Kling 3 Omni Pro (Ref) | `/v1/ai/reference-to-video/kling-v3-omni-pro` | V2V | 3-15s | Video-to-video with @Video1 |
| Kling 3 Omni Std (Ref) | `/v1/ai/reference-to-video/kling-v3-omni-std` | V2V | 3-15s | Standard V2V |
| Kling 3 Pro | `/v1/ai/video/kling-v3-pro` | T2V/I2V | 3-15s | Multi-shot, element control, negative prompts |
| Kling 3 Std | `/v1/ai/video/kling-v3-std` | T2V/I2V | 3-15s | Standard tier |
| Kling 2.6 Pro | `/v1/ai/image-to-video/kling-v2-6-pro` | I2V | - | Motion control |
| Kling 2.6 Motion Pro | `/v1/ai/video/kling-v2-6-motion-control-pro` | V2V | - | Transfer motion from reference video |
| Kling 2.6 Motion Std | `/v1/ai/video/kling-v2-6-motion-control-std` | V2V | - | Standard motion transfer |
| Kling 2.5 Turbo Pro | `/v1/ai/image-to-video/kling-v2-5-pro` | I2V | 5/10s | Smoother motion, sharper detail |
| Kling 2.1 Pro | `/v1/ai/image-to-video/kling-v2-1-pro` | I2V | - | High-fidelity |
| Kling 2.1 Std | `/v1/ai/image-to-video/kling-v2-1-std` | I2V | - | Standard tier |
| Kling 2.1 Master | `/v1/ai/image-to-video/kling-v2-1-master` | I2V | - | Top-tier quality |
| Kling O1 Pro | `/v1/ai/image-to-video/kling-o1-pro` | I2V | 5/10s | First/last frame interpolation |
| Kling O1 Std | `/v1/ai/image-to-video/kling-o1-std` | I2V | 5/10s | Standard interpolation |
| Kling O1 Pro (Ref) | `/v1/ai/image-to-video/kling-o1-pro-video-reference` | I2V | 5/10s | Pro with up to 7 reference images |
| Kling O1 Std (Ref) | `/v1/ai/image-to-video/kling-o1-std-video-reference` | I2V | 5/10s | Standard with references |
| Kling Elements Pro | `/v1/ai/image-to-video/kling-elements-pro` | I2V | - | Element-based video |
| Kling Elements Std | `/v1/ai/image-to-video/kling-elements-std` | I2V | - | Standard elements |
| Kling 2.0 | `/v1/ai/image-to-video/kling-v2` | I2V | - | I2V |
| Kling 1.6 Pro | `/v1/ai/image-to-video/kling-pro` | I2V | - | Legacy Pro |
| Kling 1.6 Std | `/v1/ai/image-to-video/kling-std` | I2V | - | Legacy Standard |

### MiniMax Hailuo Models

| Model | Endpoint | Type | Features |
|-------|----------|------|----------|
| Hailuo 02 1080p | `/v1/ai/image-to-video/minimax-hailuo-02-1080p` | T2V/I2V | 1080p |
| Hailuo 02 768p | `/v1/ai/image-to-video/minimax-hailuo-02-768p` | T2V/I2V | 768p |
| Hailuo 2.3 1080p | `/v1/ai/image-to-video/minimax-hailuo-2-3-1080p` | T2V/I2V | Latest MiniMax 1080p |
| Hailuo 2.3 1080p Fast | `/v1/ai/image-to-video/minimax-hailuo-2-3-1080p-fast` | T2V/I2V | Fast 1080p |
| Hailuo 2.3 768p | `/v1/ai/image-to-video/minimax-hailuo-2-3-768p` | T2V/I2V | 768p |
| Hailuo 2.3 768p Fast | `/v1/ai/image-to-video/minimax-hailuo-2-3-768p-fast` | T2V/I2V | Fast 768p |
| Video-01-Live | `/v1/ai/image-to-video/minimax-live` | I2V | Live illustrations, camera controls |

### WAN Models (Alibaba)

| Model | Endpoint | Type | Features |
|-------|----------|------|----------|
| WAN 2.6 I2V 1080p | `/v1/ai/image-to-video/wan-v2-6-1080p` | I2V | 5/10/15s, prompt expansion, multi-shot |
| WAN 2.6 I2V 720p | `/v1/ai/image-to-video/wan-v2-6-720p` | I2V | 720p |
| WAN 2.6 T2V 1080p | `/v1/ai/text-to-video/wan-v2-6-1080p` | T2V | 1080p |
| WAN 2.6 T2V 720p | `/v1/ai/text-to-video/wan-v2-6-720p` | T2V | 720p |
| WAN 2.5 I2V 1080p | `/v1/ai/image-to-video/wan-2-5-i2v-1080p` | I2V | 1080p |
| WAN 2.5 I2V 720p | `/v1/ai/image-to-video/wan-2-5-i2v-720p` | I2V | 720p |
| WAN 2.5 I2V 480p | `/v1/ai/image-to-video/wan-2-5-i2v-480p` | I2V | 480p |
| WAN 2.5 T2V 1080p | `/v1/ai/text-to-video/wan-2-5-t2v-1080p` | T2V | 5/10s, prompt expansion |
| WAN 2.5 T2V 720p | `/v1/ai/text-to-video/wan-2-5-t2v-720p` | T2V | 720p |
| WAN 2.5 T2V 480p | `/v1/ai/text-to-video/wan-2-5-t2v-480p` | T2V | 480p |
| WAN 2.2 480p | `/v1/ai/image-to-video/wan-v2-2-480p` | I2V | 480p |
| WAN 2.2 580p | `/v1/ai/image-to-video/wan-v2-2-580p` | I2V | 580p |
| WAN 2.2 720p | `/v1/ai/image-to-video/wan-v2-2-720p` | I2V | 720p |

### RunWay Models

| Model | Endpoint | Type | Features |
|-------|----------|------|----------|
| Gen 4.5 T2V | `/v1/ai/text-to-video/runway-4-5` | T2V | 5/8/10s, 5 aspect ratios |
| Gen 4.5 I2V | `/v1/ai/image-to-video/runway-4-5` | I2V | 5/8/10s, seed support |
| Gen4 Turbo | `/v1/ai/image-to-video/runway-gen4-turbo` | I2V | Fast |
| Act Two | `/v1/ai/video/runway-act-two` | V2V | Character performance transfer |

### LTX Video Models

| Model | Endpoint | Type | Features |
|-------|----------|------|----------|
| LTX 2.0 Pro T2V | `/v1/ai/text-to-video/ltx-2-pro` | T2V | Up to 4K (2160p), 6/8/10s, optional audio |
| LTX 2.0 Pro I2V | `/v1/ai/image-to-video/ltx-2-pro` | I2V | Up to 4K, 6/8/10s, optional audio |
| LTX 2.0 Fast T2V | `/v1/ai/text-to-video/ltx-2-fast` | T2V | Up to 4K, 6-20s (2s increments) |
| LTX 2.0 Fast I2V | `/v1/ai/image-to-video/ltx-2-fast` | I2V | Up to 4K, 6-20s |

### Seedance Models (ByteDance)

| Model | Endpoint | Type | Features |
|-------|----------|------|----------|
| Seedance 1.5 Pro 1080p | `/v1/ai/video/seedance-1-5-pro-1080p` | T2V/I2V | Synchronized audio (lip-sync, dialogue, foley, music) |
| Seedance 1.5 Pro 720p | `/v1/ai/video/seedance-1-5-pro-720p` | T2V/I2V | 720p with audio |
| Seedance 1.5 Pro 480p | `/v1/ai/video/seedance-1-5-pro-480p` | T2V/I2V | 480p with audio |
| Seedance Pro 1080p | `/v1/ai/image-to-video/seedance-pro-1080p` | I2V | 1080p |
| Seedance Pro 720p | `/v1/ai/image-to-video/seedance-pro-720p` | I2V | 720p |
| Seedance Pro 480p | `/v1/ai/image-to-video/seedance-pro-480p` | I2V | 480p |
| Seedance Lite 1080p | `/v1/ai/image-to-video/seedance-lite-1080p` | I2V | 1080p |
| Seedance Lite 720p | `/v1/ai/image-to-video/seedance-lite-720p` | I2V | 720p |
| Seedance Lite 480p | `/v1/ai/image-to-video/seedance-lite-480p` | I2V | 480p |

### Other Video Models

| Model | Endpoint | Type | Features |
|-------|----------|------|----------|
| PixVerse V5 | `/v1/ai/image-to-video/pixverse-v5` | I2V | 360p-1080p, stable style/color |
| PixVerse V5 Transition | `/v1/ai/image-to-video/pixverse-v5-transition` | I2V | Transition between two images |
| OmniHuman 1.5 | `/v1/ai/video/omni-human-1-5` | Audio-driven | Human animation from audio |
| VFX Effects | `/v1/ai/video/vfx` | Effects | 8 filters, $0.017/second |

### VFX Filter Types

| ID | Filter | Notes |
|----|--------|-------|
| 1 | Film Grain | Classic film look |
| 2 | Motion Blur | `motion_filter_kernel_size`, `motion_filter_decay_factor` params |
| 3 | Fish Eye | Barrel distortion |
| 4 | VHS | Retro video look |
| 5 | Shake | Camera shake effect |
| 6 | VGA | Low-res CRT look |
| 7 | Bloom | Glow effect, `bloom_filter_contrast` param |
| 8 | Anamorphic Lens | Cinematic wide lens flares |

---

## Image Editing

| Tool | Endpoint | Type | Features |
|------|----------|------|----------|
| Upscaler Creative | `/v1/ai/image-upscaler` | Async | Magnific. Prompt-guided, 2x/4x/8x/16x. Adds/infers detail. |
| Upscaler Precision V2 | `/v1/ai/image-upscaler-precision-v2` | Async | Magnific. Sharpen, smart grain, ultra detail, 3 flavors. |
| Upscaler Precision V1 | `/v1/ai/image-upscaler-precision` | Async | Magnific. Faithful upscaling, no hallucinations. |
| Image Relight | `/v1/ai/image-relight` | Async | Magnific. Prompt, reference image, or lightmap. EUR 0.10/op. |
| Style Transfer | `/v1/ai/image-style-transfer` | Async | Magnific. Artistic styles from references or presets. EUR 0.10/op. |
| Remove Background | `/v1/ai/beta/remove-background` | **Sync** | Transparent PNG. Up to 25 MP. URLs expire in 5 min. |
| Expand (Flux Pro) | `/v1/ai/image-expand/flux-pro` | Async | Outpainting, 0-2048px per side, optional prompt. |
| Expand (Ideogram) | `/v1/ai/image-expand/ideogram` | Async | Outpainting, auto-prompt if none. Seed support. |
| Expand (Seedream V4.5) | `/v1/ai/image-expand/seedream-v4-5` | Async | Outpainting, auto-prompt. URL or base64 input. |
| Inpainting (Ideogram) | `/v1/ai/ideogram-image-edit` | Async | Mask-based. MagicPrompt. Style/character refs. Color palette. |
| Change Camera | `/v1/ai/image-change-camera` | Async | Horizontal 0-360, vertical -30 to 90, zoom 0-10. |
| Skin Enhancer Creative | `/v1/ai/skin-enhancer/creative` | Async | Artistic skin enhancement. |
| Skin Enhancer Faithful | `/v1/ai/skin-enhancer/faithful` | Async | Natural preservation. `skin_detail` 0-100. |
| Skin Enhancer Flexible | `/v1/ai/skin-enhancer/flexible` | Async | Targeted optimization. 5 modes. |

### Upscaler Pricing (Creative/Precision)

| Output Size | Scale | Approx. Price |
|-------------|-------|---------------|
| 640x480 | 2x | EUR 0.10 |
| 640x480 | 4x | EUR 0.20 |
| 640x480 | 8x | EUR 0.50 |

---

## Icon Generation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/ai/text-to-icon` | POST | Generate icon from prompt |
| `/v1/ai/text-to-icon/preview` | POST | Quick preview |
| `/v1/ai/text-to-icon/{task-id}/render/{format}` | POST | Download in PNG or SVG |

### Icon Styles

| Style | Description |
|-------|-------------|
| solid | Filled icons (default) |
| outline | Line/stroke icons |
| color | Multi-color icons |
| flat | Flat design icons |
| sticker | Sticker-style icons |

---

## Audio

| Model | Endpoint | Type | Duration | Output |
|-------|----------|------|----------|--------|
| Music (ElevenLabs) | `/v1/ai/music-generation` | Text-to-music | 10-240s | MP3 |
| Sound Effects (ElevenLabs) | `/v1/ai/sound-effects` | Text-to-SFX | 0.5-22s | Audio |
| Audio Isolation (SAM) | `/v1/ai/audio-isolation` | Isolation | Source length | WAV |
| Voiceover (ElevenLabs) | `/v1/ai/voiceover/elevenlabs-turbo-v2-5` | TTS | Up to 40K chars | Audio |

---

## AI Utilities

| Tool | Endpoint | Type | Description |
|------|----------|------|-------------|
| Image Classifier | `/v1/ai/classifier/image` | **Sync** | Detect AI-generated images. Returns probability scores. |
| Image to Prompt | `/v1/ai/image-to-prompt` | Async | Reverse-engineer text prompt from image. |
| Improve Prompt | `/v1/ai/improve-prompt` | Async | Enhance prompts for image/video generation. |
| Lip Sync | `/v1/ai/lip-sync/latent-sync` | Async | Synchronize lip movements with audio. |

---

## Stock Content

| Content | Search Endpoint | Detail Endpoint | Download Endpoint |
|---------|-----------------|-----------------|-------------------|
| Images/Vectors/PSDs | `GET /v1/resources` | `GET /v1/resources/{id}` | `GET /v1/resources/{id}/download` |
| Icons | `GET /v1/icons` | `GET /v1/icons/{id}` | `GET /v1/icons/{id}/download` |
| Videos | `GET /v1/videos` | `GET /v1/videos/{id}` | `GET /v1/videos/{id}/download` |

---

## LoRA Support (Mystic Model)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/ai/loras` | GET | List available LoRAs (styles + characters) |
| `/v1/ai/loras/characters` | POST | Train custom character LoRA |
| `/v1/ai/loras/styles` | POST | Train custom style LoRA |

---

## Authentication

All requests require: `x-freepik-api-key: <YOUR_API_KEY>`

Base URL: `https://api.freepik.com`

Get your key: https://www.freepik.com/developers/dashboard/api-key

## Async Task Pattern

1. POST → returns `task_id`
2. GET `/{task-id}` → poll until `status: "COMPLETED"`
3. Or use `webhook_url` parameter for automatic notification
4. Statuses: `CREATED` → `IN_PROGRESS` → `COMPLETED` | `FAILED`

**Synchronous exceptions:** Remove Background, AI Image Classifier
