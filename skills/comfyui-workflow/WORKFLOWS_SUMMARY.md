# ComfyUI Workflows — Complete Reference

> **⚠️ IMPORTANT**: The workflow JSON files in this repository are **EXAMPLES ONLY** — prompts, notes, and model paths have been sanitized. They will NOT work out of the box. For functional workflows, obtain complete versions from the original authors on Civitai, HuggingFace, or their official repositories. Respect intellectual property.
>
> **⚠️ AGENTS: DO NOT REFERENCE THIS FILE until you have updated it with the user's actual workflows.** The content below describes sanitized examples and will lead to incorrect model names, missing files, and failed executions. Update this file first, then use it as a knowledge cache.

All 24 workflow JSON files in `comfyui_example/` documented. Covers **8 model families**: Qwen Image, Flux 2 Dev, Flux 2 Klein, Kandinsky 5, HunyuanVideo 1.5, Wan 2.2, LTX-2 Video, and specialty templates.

---

## Master Model Matrix

### Image Generation (12 workflows)

| # | Workflow File | Type | UNET/Checkpoint | CLIP (type) | VAE | Pipeline | CFG | Steps | Key Extras |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `image_qwen_Image_2512.json` | t2i | `qwen_image_2512_fp8_e4m3fn` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_vae` | KSampler | 4 (std) / 1 (LoRA) | 50 (std) / 4 (LoRA) | Lightning LoRA variant |
| 2 | `image_qwen_image_2512_with_2steps_lora.json` | t2i | `qwen_image_2512_fp8_e4m3fn` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_vae` | KSampler | 1 | 2 | Turbo LoRA, ConditioningZeroOut |
| 3 | `image_qwen_image_edit_2509.json` | edit | `qwen_image_edit_2509_fp8_e4m3fn` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_vae` | KSampler | 1 (w/LoRA) | 4 (w/LoRA) | CFGNorm, TextEncodeQwenImageEditPlus |
| 4 | `image_qwen_image_edit_2511.json` | edit | `qwen_image_edit_2511_bf16` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_vae` | KSampler | 4 (std) / 1 (LoRA) | 40 (std) / 4 (LoRA) | FluxKontextMultiRefLatent |
| 5 | `image_qwen_image_layered_control.json` | layered | `qwen_image_layered_control_bf16` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_layered_vae` | KSampler | 2.5 | 20 | EmptyQwenImageLayeredLatentImage, LatentCutToBatch |
| 6 | `image_flux2_fp8.json` | t2i/edit | `flux2_dev_fp8mixed` | `mistral_3_small_flux2_fp8` (flux2) | `flux2-vae` | SamplerCustomAdvanced | guidance=4 | 20/8 | BasicGuider, FluxGuidance, Flux2Scheduler |
| 7 | `image_flux2_klein_image_edit_4b_base.json` | edit | `flux-2-klein-base-4b-fp8` | `qwen_3_4b` (flux2) | `flux2-vae` | SamplerCustomAdvanced | 5 | 20 | CFGGuider, Reference Conditioning |
| 8 | `image_flux2_klein_image_edit_9b_base.json` | edit | `flux-2-klein-base-9b-fp8` | `qwen_3_8b_fp8mixed` (flux2) | `flux2-vae` | SamplerCustomAdvanced | 5 | 20 | CFGGuider, chained Reference Conditioning |
| 9 | `image_flux2_klein_image_edit_9b_distilled.json` | edit | `flux-2-klein-9b-fp8` | `qwen_3_8b_fp8mixed` (flux2) | `flux2-vae` | SamplerCustomAdvanced | 1 | 4 | CFGGuider, ConditioningZeroOut, fast inference |
| 10 | `image_kandinsky5_t2i.json` | t2i | `kandinsky5lite_t2i` | DualCLIP: `qwen_2.5_vl_7b_fp8_scaled` + `clip_l` (kandinsky5_image) | `ae` | KSampler | 3.5 | 50 | ModelSamplingSD3(shift=3), DualCLIPLoader |
| 11 | `templates-1_click_multiple_character_angles-v1.0.json` | multi-edit | `qwen_image_edit_2509_fp8_e4m3fn` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_vae` | KSampler ×8 | 1 | 4 | Multi-angles LoRA, 8 camera angles |
| 12 | `templates-1_click_multiple_scene_angles-v1.0.json` | multi-edit | `qwen_image_edit_2509_fp8_e4m3fn` | `qwen_2.5_vl_7b_fp8_scaled` (qwen_image) | `qwen_image_vae` | KSampler ×8 | 1 | 4 | Multi-angles LoRA, 8 camera angles |

### Specialty Templates (3 workflows)

| # | Workflow File | Type | Base Model | LoRAs | Steps | Key Feature |
|---|---|---|---|---|---|---|
| 13 | `templates-image_to_real.json` | edit | Qwen Edit 2509 fp8 | Anything2Real + Lightning 8steps | 8 | Converts any image to realistic photo; `beta` scheduler |
| 14 | `templates-portrait_light_migration.json` | edit | Qwen Edit 2509 fp8 | Light-Migration + Lightning 8steps | 8 | Transfers lighting/color tones from reference |
| 15 | `templates-6-key-frames.json` | video | Wan 2.2 I2V (dual UNET: high+low noise) | LightX2V 4steps (dual: high+low noise) | 4 | 6-keyframe interpolation, 5 chained subgraphs |

### Video Generation (9 workflows)

| # | Workflow File | Type | Model Family | Resolution | Frames | Steps | Key Feature |
|---|---|---|---|---|---|---|---|
| 16 | `video_hunyuan_video_1.5_720p_i2v.json` | i2v | HunyuanVideo 1.5 | 1280×720→1920×1080 | 121 | 8 | CLIPVision + latent upscaler + SuperRes |
| 17 | `video_hunyuan_video_1.5_720p_t2v.json` | t2v | HunyuanVideo 1.5 | 1280×720→1920×1080 | 121 | 8 | DualCLIP (Qwen+ByT5) + latent upscaler |
| 18 | `video_kandinsky5_i2v.json` | i2v | Kandinsky 5 Lite | 768×512 | 121 | 50 | euler_ancestral + beta scheduler; 5-second video |
| 19 | `video_wan2_2_14B_i2v.json` | i2v | Wan 2.2 14B | 640×640 | 81 | 20 | Low-noise UNET + LightX2V LoRA; shift=5 |
| 20 | `video_wan2_2_14B_t2v.json` | t2v | Wan 2.2 14B | 640×640 | 81 | 20 | Low-noise UNET + LightX2V LoRA; shift=8 |
| 21 | `video_ltx2_i2v.json` | i2v | LTX-2 19B | 768×512→upscale | 97 | 20 | 2-pass (gen+upscale), camera-control LoRA |
| 22 | `video_ltx2_t2v.json` | t2v | LTX-2 19B | 768×512→upscale | 97 | 20 | 2-pass (gen+upscale), audio generation |
| 23 | `video_ltx2_canny_to_video.json` | canny2v | LTX-2 19B | 768×512→upscale ×2 | 97 | 20 | Canny edge guidance + audio; dev/distilled variants |
| 24 | `video_ltx2_depth_to_video.json` | depth2v | LTX-2 19B | 768×512→upscale ×2 | 97 | 20 | Lotus depth estimation + audio; 3 subgraphs |

---

## Detailed Workflow Documentation

### 1. Qwen-Image-2512 (Text-to-Image)

**File:** `image_qwen_Image_2512.json`

Two subgraph variants in one file:

| Variant | Steps | CFG | LoRA | Status |
|---------|-------|-----|------|--------|
| Standard | 50 | 4 | None | Active |
| Lightning | 4 | 1 | `Qwen-Image-Lightning-4steps-V1.0.safetensors` | Disabled |

**Node Chain:**
```
UNETLoader → [LoraLoaderModelOnly →] ModelSamplingAuraFlow(shift=3.1) → KSampler
CLIPLoader(qwen_image) → CLIPTextEncode → KSampler
VAELoader → VAEDecode
EmptySD3LatentImage(1328×1328) → KSampler
```

**Resolution Presets:**
- 1:1 → 1328×1328, 16:9 → 1664×928, 9:16 → 928×1664
- 4:3 → 1472×1104, 3:4 → 1104×1472, 3:2 → 1584×1056, 2:3 → 1056×1584

**Key Details:**
- Uses `EmptySD3LatentImage` for latent creation
- Negative prompt in Chinese: "低分辨率，低画质，肢体畸形..." (low resolution, low quality, deformed limbs)
- Example: "Urban alleyway at dusk. Tall, statuesque high-fashion model striding elegantly..."

---

### 2. Qwen-Image-2512 + Turbo LoRA (Ultra-Fast 2-Step)

**File:** `image_qwen_image_2512_with_2steps_lora.json`

**Node Chain:**
```
UNETLoader → LoraLoaderModelOnly(Turbo) → ModelSamplingAuraFlow(shift=3.0) → KSampler
CLIPLoader(qwen_2.5_vl_7b_fp8_scaled) → CLIPTextEncode → KSampler (positive)
                                                         → ConditioningZeroOut → KSampler (negative)
```

**Critical Differences from Standard 2512:**
- Uses `ConditioningZeroOut` on positive prompt as negative conditioning (no explicit negative text)
- LoRA: `Wuli-Qwen-Image-2512-Turbo-LoRA-2steps-V1.0-bf16.safetensors`
- Steps: **2**, CFG: **1.0**, shift: **3.0** (not 3.1)

---

### 3. Qwen-Image-Edit-2509 (Image Editing)

**File:** `image_qwen_image_edit_2509.json`

Two main variants (standard + raw latent with ReferenceLatent):

| Variant | UNET | Steps | CFG | LoRA |
|---------|------|-------|-----|------|
| fp8+LoRA (active) | `qwen_image_edit_2509_fp8_e4m3fn` | 4 | 1.0 | Lightning 4steps |
| fp8 standard | `qwen_image_edit_2509_fp8_e4m3fn` | 20 | 2.5 | None |

**Node Chain (editing):**
```
LoadImage → FluxKontextImageScale → TextEncodeQwenImageEditPlus(image1,image2,image3,prompt)
UNETLoader → [LoraLoader →] ModelSamplingAuraFlow(shift=3) → CFGNorm(strength=1) → KSampler
VAEEncode(input image) → KSampler (latent_image)
```

**Key Nodes:**
- `TextEncodeQwenImageEditPlus` — accepts 3 image inputs + text prompt (CLIP + VAE required)
- `FluxKontextImageScale` — preprocesses input image for Kontext format
- `CFGNorm(strength=1)` — normalizes CFG signal (required for all Qwen edit models)
- `ModelSamplingAuraFlow(shift=3)` — AuraFlow noise schedule

**LoRA Files:**
- `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` (speed)
- `Qwen-Image-Edit-2509-Turbo-LoRA-2steps-V1.0-bf16.safetensors` (ultra-fast)

---

### 4. Qwen-Image-Edit-2511 (Advanced Editing)

**File:** `image_qwen_image_edit_2511.json`

Upgraded from 2509 with better multi-person consistency and editing quality.

| Variant | Steps | CFG | LoRA |
|---------|-------|-----|------|
| Standard | 40 | 4.0 | None |
| Lightning | 4 | 1.0 | `Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` |

**Same node pattern as 2509** but uses `qwen_image_edit_2511_bf16.safetensors` and adds:
- `FluxKontextMultiReferenceLatentMethod(reference_latents_method="index_timestep_zero")` — enables multi-reference image conditioning
- `ModelSamplingAuraFlow(shift=3.1)` — slightly higher shift than 2509

**Example Prompts:**
- "Remove the background completely, make it pure white"
- "Change the furniture material to leather"
- "Replace the background with a beach sunset"

---

### 5. Qwen-Image-Layered-Control

**File:** `image_qwen_image_layered_control.json`

Unique workflow for layer-decomposed image generation with structured positional control.

**Node Chain:**
```
UNETLoader(layered_control_bf16, loaded as fp8_e4m3fn) → ModelSamplingAuraFlow(shift=1) → KSampler
CLIPLoader → CLIPTextEncode → KSampler
VAELoader(qwen_image_layered_vae) → VAEDecode
EmptyQwenImageLayeredLatentImage(640×640, 2 layers) → LatentCutToBatch → KSampler
```

**Key Differences:**
- Uses **special VAE**: `qwen_image_layered_vae.safetensors` (not the standard one!)
- `ModelSamplingAuraFlow(shift=1)` — lower shift than editing workflows (shift=3)
- CFG: **2.5**, Steps: **20**
- `EmptyQwenImageLayeredLatentImage` — creates multi-layer latent representation
- `LatentCutToBatch` — splits layers into batch for parallel processing
- `ReferenceLatent` — injects reference conditioning at specific layers

**Use Case:** Compositional generation where foreground/background/layers need separate control.

---

### 6. Flux 2 Dev (Text-to-Image / Image Edit)

**File:** `image_flux2_fp8.json`

Uses Mistral 3 Small as text encoder — fundamentally different architecture from Qwen.

**Two subgraphs:**

| Subgraph | Purpose | Steps | Guidance | LoRA |
|----------|---------|-------|----------|------|
| Standard t2i/edit | Generate from text / edit with reference | 20 | FluxGuidance=4, BasicGuider | None |
| Turbo variant | Fast generation | 8 | FluxGuidance=4, BasicGuider | `Flux2TurboComfyv2.safetensors` |

**Node Chain (SamplerCustomAdvanced pipeline):**
```
UNETLoader(flux2_dev_fp8mixed) → BasicGuider ← FluxGuidance(guidance=4)
CLIPLoader(mistral_3_small_flux2_fp8, type=flux2) → CLIPTextEncode → BasicGuider
VAELoader(flux2-vae) → VAEDecode
Flux2Scheduler(steps=20, shift=1) → SamplerCustomAdvanced
RandomNoise → SamplerCustomAdvanced
EmptyFlux2LatentImage OR GetImageSize → SamplerCustomAdvanced
```

**Key Architectural Differences from Qwen:**
- Uses `SamplerCustomAdvanced` pipeline (not KSampler)
- Uses `BasicGuider` with `FluxGuidance(guidance=4)` instead of CFG parameter
- Uses `Flux2Scheduler` instead of simple/normal schedulers
- `RandomNoise` node creates noise (vs seed parameter in KSampler)
- CLIP type is `flux2`, text encoder is Mistral 3 Small (not Qwen VL)
- `ReferenceLatent` node for image edit (encode reference image into latent → inject)

**Image Edit Pattern:**
```
LoadImage → ImageScaleToTotalPixels(1MP) → VAEEncode → ReferenceLatent(index=0)
ReferenceLatent connects to: positive conditioning AND negative conditioning
```

---

### 7. Flux 2 Klein 4B Base (Image Edit)

**File:** `image_flux2_klein_image_edit_4b_base.json`

Smaller Klein variant using Qwen 3 4B as text encoder.

**Node Chain:**
```
UNETLoader(flux-2-klein-base-4b-fp8) → CFGGuider(cfg=5)
CLIPLoader(qwen_3_4b, type=flux2) → CLIPTextEncode → CFGGuider (positive & negative)
VAELoader(flux2-vae) → VAEDecode
Flux2Scheduler(steps=20) → SamplerCustomAdvanced
RandomNoise → SamplerCustomAdvanced
```

**Reference Conditioning Subgraph Pattern:**
```
LoadImage → ImageScaleToTotalPixels(1MP) → VAEEncode → ReferenceLatent(index=0)
→ applied to BOTH positive and negative conditioning paths
```

**Key Details:**
- Uses `CFGGuider` (not BasicGuider) — supports true CFG with separate positive/negative
- Two subgraph variants: single-image (disabled) and multi-image (active)
- Multi-image variant chains two Reference Conditioning subgraphs

---

### 8. Flux 2 Klein 9B Base (Image Edit)

**File:** `image_flux2_klein_image_edit_9b_base.json`

Same architecture as 4B but larger model with Qwen 3 8B text encoder.

| Setting | Klein 4B | Klein 9B Base |
|---------|----------|---------------|
| UNET | `flux-2-klein-base-4b-fp8` | `flux-2-klein-base-9b-fp8` |
| CLIP | `qwen_3_4b` | `qwen_3_8b_fp8mixed` |
| CFG | 5 | 5 |
| Steps | 20 | 20 |

**Example:** "Apply the yellow C logo to the center hub of the steering wheel"

---

### 9. Flux 2 Klein 9B Distilled (Fast Image Edit)

**File:** `image_flux2_klein_image_edit_9b_distilled.json`

Distilled version — dramatically faster than base with different sampling strategy.

| Setting | 9B Base | 9B Distilled |
|---------|---------|--------------|
| UNET | `flux-2-klein-base-9b-fp8` | `flux-2-klein-9b-fp8` |
| CFG | 5 | **1** |
| Steps | 20 | **4** |
| Negative Prompt | Explicit text | **ConditioningZeroOut** (zeroed) |

**Critical Pattern — ConditioningZeroOut for Distilled Models:**
```
CLIPTextEncode(positive_prompt) → CFGGuider (positive)
CLIPTextEncode(positive_prompt) → ConditioningZeroOut → CFGGuider (negative)
```
The distilled model uses zeroed-out conditioning as the negative signal. Explicit negative prompt text is generally not recommended here.

---

### 10. Kandinsky 5 Lite (Text-to-Image) — NEW

**File:** `image_kandinsky5_t2i.json`

Kandinsky 5.0 Lite is a 6B-parameter image generation model from Sber AI (kandinskylab). It uses a unique **DualCLIPLoader** architecture combining Qwen 2.5 VL and CLIP-L text encoders, and uses **ModelSamplingSD3** (not AuraFlow like Qwen models).

**Node Chain:**
```
UNETLoader(kandinsky5lite_t2i) → ModelSamplingSD3(shift=3) → KSampler
DualCLIPLoader(qwen_2.5_vl_7b_fp8_scaled + clip_l, type=kandinsky5_image) → CLIPTextEncode → KSampler
VAELoader(ae.safetensors) → VAEDecode
EmptyLatentImage(1024×1024) → KSampler
```

**Key Architecture:**
- **DualCLIPLoader** — only image workflow using this (combines Qwen VL + OpenAI CLIP-L)
- **ModelSamplingSD3(shift=3)** — SD3-style noise schedule, NOT AuraFlow
- **VAE: `ae.safetensors`** — unique VAE, not shared with other families
- CFG: **3.5**, Steps: **50**, Sampler: `euler`, Scheduler: `simple`
- Resolution: **1024×1024** (supports up to 1280×768 and other ratios)

**Strengths (per official benchmarks):**
- Strong text-writing capability (renders text in images well)
- Russian concepts understanding
- Competitive with FLUX.1 dev and Qwen-Image in evaluations
- Supports English and Russian prompts

---

### 11–12. Multi-Angle Templates (Character & Scene)

**Files:**
- `templates-1_click_multiple_character_angles-v1.0.json`
- `templates-1_click_multiple_scene_angles-v1.0.json`

Both are structurally identical — 8 parallel KSampler instances generating different camera angles from a single input image.

**Model Stack:**
```
UNETLoader(qwen_image_edit_2509_fp8) → LoRA(Multi-angles) → LoRA(Lightning 4steps)
→ ModelSamplingAuraFlow(shift=3) → CFGNorm(strength=1) → KSampler ×8
```

**LoRAs (both applied):**
1. `Qwen-Edit-2509-Multiple-angles.safetensors` — multi-angle generation capability
2. `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` — speed acceleration

**The 8 Camera Angle Prompts:**
1. "Turn the camera to a close-up."
2. "Turn the camera to a wide-angle lens."
3. "Rotate the camera 45 degrees to the right."
4. "Rotate the camera 90 degrees to the right."
5. "Turn the camera to an aerial view."
6. "Turn the camera to a low-angle view."
7. "Rotate the camera 45 degrees to the left."
8. "Rotate the camera 90 degrees to the left."

**Settings:** steps=4, CFG=1, euler, simple, 1MP resolution via ImageScaleToTotalPixels

---

### 13. Image-to-Realistic Photo Template

**File:** `templates-image_to_real.json`

Converts any image (illustration, sketch, etc.) to a realistic photograph.

**Model Stack:**
```
UNETLoader(qwen_image_edit_2509_fp8) → LoRA(Anything2Real) → LoRA(Lightning 8steps)
→ ModelSamplingAuraFlow(shift=3) → CFGNorm(strength=1) → KSampler
```

**LoRAs (both applied):**
1. `Qwen-Image-Edit-2509-Anything2RealAlpha.safetensors` — realistic photo conversion
2. `Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors` — speed (8-step)

**Settings:** steps=8, CFG=1, euler, scheduler=**beta** (unique — only workflow using beta scheduler)

**Prompt:** "change image 1 to realistic photograph"

---

### 14. Portrait Light Migration Template

**File:** `templates-portrait_light_migration.json`

Transfers lighting/color tones from a reference image onto a portrait or scene. Uses two input images.

**Model Stack:**
```
UNETLoader(qwen_image_edit_2509_fp8) → LoRA(Light-Migration) → LoRA(Lightning 8steps)
→ ModelSamplingAuraFlow(shift=3) → CFGNorm(strength=1) → KSampler
```

**LoRAs (both applied):**
1. `Qwen-Image-Edit-2509-Light-Migration.safetensors` — lighting transfer
2. `Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors` — speed (8-step)

**Settings:** steps=8, CFG=1, euler, simple, 1MP resolution
**Key Node:** `RepeatLatentBatch` — duplicates latent for multi-image conditioning
**Prompt:** "参考色调，移除图1原有的光照并参考图2的光照和色调对图1重新照明" (Reference tone, remove original lighting from image 1 and re-light using image 2's lighting and color tone)

---

### 15. 6-Key-Frames Video Template — NEW

**File:** `templates-6-key-frames.json`

A sophisticated keyframe interpolation workflow that chains **5 identical subgraphs** of Wan 2.2 I2V to generate smooth transitions between 6 keyframe images. Uses a dual-UNET, dual-LoRA architecture.

**Dual UNET Architecture:**
```
UNETLoader(wan2.2_i2v_high_noise_14B_fp8_scaled) → LoRA(lightx2v_4steps_high_noise) → Pass 1 (high noise)
UNETLoader(wan2.2_i2v_low_noise_14B_fp8_scaled) → LoRA(lightx2v_4steps_low_noise) → Pass 2 (low noise)
```

**Node Chain (per subgraph):**
```
WanFirstLastFrameToVideo(first_frame, last_frame) → KSamplerAdvanced (2-pass: high→low noise)
CLIPLoader(umt5_xxl_fp8_e4m3fn_scaled, type=wan) → CLIPTextEncode
ModelSamplingSD3(shift=5) → KSamplerAdvanced
VAEDecode(wan_2.1_vae) → ImageBatch → CreateVideo → SaveVideo
```

**Key Details:**
- 5 subgraphs chained: keyframe 1→2, 2→3, 3→4, 4→5, 5→6
- Each segment: 720×720, 25 frames
- Two-pass KSamplerAdvanced: steps 0→2 (high noise), steps 2→4 (low noise)
- Chinese negative prompt: "色情，裸体，低画质..." (NSFW filter + quality)
- **WanFirstLastFrameToVideo** — specialized node for first+last frame video interpolation

---

### 16. HunyuanVideo 1.5 — Image-to-Video (720p) — NEW

**File:** `video_hunyuan_video_1.5_720p_i2v.json`

HunyuanVideo 1.5 is an 8.3B-parameter video generation model from Tencent. Features a unique pipeline with latent upscaling and super-resolution.

**Node Chain:**
```
DualCLIPLoader(qwen_2.5_vl_7b_fp8_scaled + byt5_small_glyphxl_fp16, type=hunyuan_video_15)
    → CLIPTextEncode → CFGGuider(cfg=1)
CheckpointLoaderSimple(hunyuanvideo1.5_720p_i2v_fp16) → CFGGuider
    → ModelSamplingSD3(shift=2) → SamplerCustomAdvanced (euler, 8 steps)
CLIPVisionLoader(sigclip_vision_patch14_384) → CLIPVisionEncode → image conditioning
HunyuanVideo15ImageToVideo(frames=121) → latent input
```

**Post-Processing Pipeline:**
```
HunyuanVideo15LatentUpscaleWithModel(hunyuanvideo15_latent_upsampler_1080p)
    → upscale to 1920×1080
HunyuanVideo15SuperResolution(strength=0.7) → final quality enhancement
EasyCache → inference acceleration
VAEDecodeTiled → memory-efficient decoding
```

**Key Architecture:**
- **DualCLIPLoader** — Qwen 2.5 VL 7B + ByT5 Small (glyph-aware text encoding for in-video text rendering)
- **CLIPVisionLoader** — SigCLIP Vision for image conditioning (i2v only)
- **Latent upscaler** — 720p→1080p upscale in latent space
- **SuperResolution(0.7)** — post-processing enhancement
- **EasyCache** — training-free inference acceleration
- **SplitSigmas** — noise schedule splitting for multi-pass
- CFG: **1** (cfg-distilled model), Steps: **8** (reduced from official 50)
- 121 frames at 24fps ≈ 5 seconds of video

**Official Optimal Settings (from Tencent research):**
| Config | CFG | Shift | Steps | Notes |
|--------|-----|-------|-------|-------|
| 720p I2V standard | 6 | 7 | 50 | Best quality |
| 720p I2V CFG-distilled | 1 | 7 | 50 | 2× speedup |
| 720p→1080p SR | 1 | 2 | 8 | Upscale pass |

---

### 17. HunyuanVideo 1.5 — Text-to-Video (720p) — NEW

**File:** `video_hunyuan_video_1.5_720p_t2v.json`

Same architecture as i2v but generates video from text only (no input image).

**Differences from i2v:**
- Uses `hunyuanvideo1.5_720p_t2v_fp16.safetensors` (t2v checkpoint)
- No CLIPVisionLoader or CLIPVisionEncode nodes
- Uses `EmptyHunyuanVideo15Latent(frames=121)` instead of HunyuanVideo15ImageToVideo
- Same DualCLIP, upscaler, and SuperResolution pipeline

**Official Optimal Settings:**
| Config | CFG | Shift | Steps |
|--------|-----|-------|-------|
| 720p T2V standard | 6 | 9 | 50 |
| 720p T2V CFG-distilled | 1 | 9 | 50 |

**Prompt Tips (from HunyuanVideo Prompt Handbook):**
- Write detailed, descriptive prompts for best results
- Describe composition, lighting, camera movement explicitly
- Supports both English and Chinese prompts

---

### 18. Kandinsky 5 Lite — Image-to-Video (5s) — NEW

**File:** `video_kandinsky5_i2v.json`

Kandinsky 5.0 Video Lite is a lightweight 2B-parameter video model. Ranked #1 among open-source models in its class, outperforming larger Wan 5B/14B models.

**Node Chain:**
```
UNETLoader(kandinsky5lite_i2v_5s) → ModelSamplingSD3(shift=5) → KSampler
DualCLIPLoader(qwen_2.5_vl_7b_fp8_scaled + clip_l, type=kandinsky5) → CLIPTextEncode
VAELoader(hunyuan_video_vae_bf16) → VAEDecode
Kandinsky5ImageToVideo → latent input
```

**Unique Settings:**
- Sampler: **`euler_ancestral`** + **`beta`** scheduler (unique combination, no other workflow uses this)
- CFG: **5**, Steps: **50**
- ModelSamplingSD3(shift=5) — higher shift for video
- Resolution: 768×512, 121 frames (5-second video)
- **NormalizeVideoLatentStart** — normalizes starting video latent
- **ReplaceVideoLatentFrames** — replaces specific latent frames for I2V conditioning
- Reuses **HunyuanVideo VAE** (`hunyuan_video_vae_bf16.safetensors`)

**Strengths:** Russian concepts understanding, compact model, fast inference (~139s on H100)

---

### 19. Wan 2.2 14B — Image-to-Video — NEW

**File:** `video_wan2_2_14B_i2v.json`

Wan 2.2 is a 14B-parameter video model. This workflow uses the low-noise UNET variant with LightX2V LoRA acceleration.

**Node Chain:**
```
UNETLoader(wan2.2_i2v_low_noise_14B_fp8_scaled) → LoRA(lightx2v_4steps_low_noise)
    → ModelSamplingSD3(shift=5) → KSamplerAdvanced (2-pass: steps 0→10, 10→end)
CLIPLoader(umt5_xxl_fp8_e4m3fn_scaled, type=wan) → CLIPTextEncode
WanImageToVideo(LoadImage) → latent input
VAELoader(wan_2.1_vae) → VAEDecode → CreateVideo → SaveVideo
```

**Key Details:**
- **KSamplerAdvanced with 2-pass**: steps 0→10 (return with leftover noise), then 10→20 (denoise)
- LoRA: `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` — 4-step acceleration
- CFG: **3.5**, Steps: **20**, euler, simple
- Resolution: 640×640, 81 frames
- Chinese negative prompt: "色情，裸体，低画质，低分辨率..." (NSFW + quality filter)

---

### 20. Wan 2.2 14B — Text-to-Video — NEW

**File:** `video_wan2_2_14B_t2v.json`

T2V counterpart of the Wan 2.2 i2v workflow.

**Differences from i2v:**
- UNET: `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` (t2v checkpoint)
- LoRA: `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` (t2v-specific LoRA)
- **ModelSamplingSD3(shift=8)** — significantly higher shift than I2V's shift=5
- Uses `EmptyHunyuanLatentVideo` (reused from HunyuanVideo) instead of WanImageToVideo
- Same resolution (640×640), frames (81), CFG (3.5), steps (20)

---

### 21. LTX-2 Image-to-Video (+ Audio)

**File:** `video_ltx2_i2v.json`

Full image-to-video pipeline with audio generation using Lightricks LTX-2 19B.

**Two-Pass Pipeline:**
```
Pass 1 (Generate): CheckpointLoader → CFGGuider(cfg=1) → euler → SamplerCustomAdvanced
Pass 2 (Upscale): LTXVLatentUpsampler → CFGGuider(cfg=4) → gradient_estimation → SamplerCustomAdvanced
```

**Model Stack:**
- Checkpoint: `ltx-2-19b-dev-fp8.safetensors` (MODEL + VAE built-in)
- Text Encoder: **Gemma 3 12B** via `LTXAVTextEncoderLoader` (gemma_3_12B_it.safetensors)
- Audio VAE: `LTXVAudioVAELoader`
- LoRAs (disabled): `ltx-2-19b-lora-camera-control-dolly-left`, `ltx-2-19b-distilled-lora-384`

**Video Settings:**
- Initial latent: 768×512, 97 frames
- Input image resize: longer edge 1536 or 1280×720
- Upscale pass uses `ManualSigmas: [0.909375, 0.725, 0.421875, 0.0]`
- 25 fps output

**Scheduler:** `LTXVScheduler(steps=20, max_shift=2.05, base_shift=0.95, stretch=true, terminal=0.1)`

**Key Nodes:**
- `LTXVImgToVideoInplace` — injects first frame from input image
- `LTXVAddGuide` — adds image guidance to video generation
- `LTXVPreprocess` — preprocesses 33 frames for conditioning
- `LTXVConcatAVLatent` / `LTXVSeparateAVLatent` — combine/split audio+video latents
- `MultimodalGuider` / `GuiderParameters` — multimodal guidance (text+image+audio)
- `VHS_VideoCombine` — output H264 MP4

---

### 22. LTX-2 Text-to-Video (+ Audio)

**File:** `video_ltx2_t2v.json`

Same as i2v but generates video from pure text (no input image).

**Differences from i2v:**
- No `LTXVImgToVideoInplace`, `LTXVPreprocess`, `LoadImage` nodes
- Uses `euler_ancestral` for both passes (i2v uses `euler` + `gradient_estimation`)
- Everything else identical (same model, scheduler, frames, resolution)

---

### 23. LTX-2 Canny-to-Video (+ Audio) — NEW

**File:** `video_ltx2_canny_to_video.json`

Structural video generation guided by Canny edge detection. Two subgraph variants (dev + distilled).

**Node Chain (dev variant):**
```
CheckpointLoaderSimple(ltx-2-19b-dev-fp8) + LoRA(ltx-2-19b-ic-lora-canny-control)
LTXAVTextEncoderLoader(gemma_3_12B_it_fp4_mixed)
LoadImage → Canny(low=100, high=200) → LTXVAddGuide → conditioning
SamplerCustomAdvanced: Pass 1 (euler, 20 steps), Pass 2 (gradient_estimation, upscale)
```

**Distilled Variant:**
- Uses `ltx-2-19b-distilled.safetensors` checkpoint
- LoRA: `ltx-2-19b-distilled-lora-384.safetensors`
- `euler_ancestral` sampler, CFG=1 → faster inference

**Unique Nodes:**
- **Canny** — Canny edge detection for structural guidance
- **LTXVCropGuides** — crops guide images to match latent dimensions
- Spatial upscaler: `ltx-2-spatial-upscaler-x2-1.0.safetensors` (×2 upscale)

**Use Case:** Generate videos that follow the structural outline of a reference image/video (edges, shapes).

---

### 24. LTX-2 Depth-to-Video (+ Audio) — NEW

**File:** `video_ltx2_depth_to_video.json`

Structural video generation guided by depth estimation. Three subgraphs: dev pipeline, distilled pipeline, and depth estimation subgraph.

**Depth Estimation Subgraph:**
```
UNETLoader(lotus-depth-d-v1-1) → BasicGuider → SamplerCustomAdvanced
VAELoader(vae-ft-mse-840000-ema-pruned) → encode/decode
LotusConditioning → conditioning
LoadImage → depth estimation → LTXVAddGuide
```

**Main Pipeline (same as canny variant but with depth guidance):**
```
LoRA: ltx-2-19b-ic-lora-depth-control.safetensors
Spatial upscaler: ltx-2-spatial-upscaler-x2-1.0.safetensors
```

**Unique Nodes:**
- **LotusConditioning** — Lotus depth estimation model conditioning
- **ImageInvert** — inverts depth map for proper guidance
- **SetFirstSigma** — sets initial sigma for depth refinement

**Use Case:** Generate videos that follow the depth structure of a reference image/video (3D structure, perspective).

---

## Complete LoRA Inventory

| LoRA File | Base Model | Effect | Steps | Used In |
|-----------|-----------|--------|-------|---------|
| `Qwen-Image-Lightning-4steps-V1.0.safetensors` | Qwen 2512 | Speed (4 steps) | 4 | image_qwen_Image_2512 |
| `Wuli-Qwen-Image-2512-Turbo-LoRA-2steps-V1.0-bf16.safetensors` | Qwen 2512 | Ultra-speed (2 steps) | 2 | image_qwen_image_2512_with_2steps_lora |
| `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` | Qwen Edit 2509 | Speed (4 steps) | 4 | 2509 edit, multi-angle templates |
| `Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors` | Qwen Edit 2509 | Speed (8 steps) | 8 | image_to_real, light_migration |
| `Qwen-Image-Edit-2509-Turbo-LoRA-2steps-V1.0-bf16.safetensors` | Qwen Edit 2509 | Ultra-speed (2 steps) | 2 | 2509 edit variant |
| `Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` | Qwen Edit 2511 | Speed (4 steps) | 4 | 2511 edit |
| `Qwen-Edit-2509-Multiple-angles.safetensors` | Qwen Edit 2509 | Multi-angle generation | 4 | character/scene angle templates |
| `Qwen-Image-Edit-2509-Anything2RealAlpha.safetensors` | Qwen Edit 2509 | Realistic photo conversion | 8 | image_to_real template |
| `Qwen-Image-Edit-2509-Light-Migration.safetensors` | Qwen Edit 2509 | Lighting transfer | 8 | portrait light migration |
| `Flux2TurboComfyv2.safetensors` | Flux 2 Dev | Turbo (8 steps) | 8 | image_flux2_fp8 |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | Wan 2.2 I2V | 4-step acceleration | 4 | wan2.2 i2v, 6-keyframes |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | Wan 2.2 I2V | 4-step high noise pass | 4 | 6-keyframes |
| `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` | Wan 2.2 T2V | 4-step acceleration | 4 | wan2.2 t2v |
| `ltx-2-19b-distilled-lora-384.safetensors` | LTX-2 | Distilled acceleration | — | LTX2 all variants |
| `ltx-2-19b-ic-lora-canny-control.safetensors` | LTX-2 | Canny structural guidance | — | LTX2 Canny |
| `ltx-2-19b-ic-lora-depth-control.safetensors` | LTX-2 | Depth structural guidance | — | LTX2 Depth |
| `ltx-2-19b-lora-camera-control-dolly-left.safetensors` | LTX-2 | Camera dolly motion | — | LTX2 I2V/T2V |

---

## Architecture Patterns

### Pattern A: Qwen KSampler Pipeline
Used by all Qwen workflows + Kandinsky 5 (with DualCLIP variant).
```
UNETLoader → [LoraLoader →] ModelSamplingAuraFlow(shift) → [CFGNorm(1) →] KSampler
CLIPLoader(type=qwen_image) → [CLIPTextEncode | TextEncodeQwenImageEditPlus] → KSampler
VAELoader → VAEDecode
[EmptySD3LatentImage | VAEEncode(input_image)] → KSampler
```

### Pattern B: Flux 2 SamplerCustomAdvanced Pipeline
Used by Flux 2 Dev and all Klein variants.
```
UNETLoader → [BasicGuider+FluxGuidance | CFGGuider]
CLIPLoader(type=flux2) → CLIPTextEncode → Guider
VAELoader(flux2-vae) → VAEDecode
[EmptyFlux2LatentImage | GetImageSize] → noise latent
Flux2Scheduler → SamplerCustomAdvanced
RandomNoise → SamplerCustomAdvanced
```

### Pattern C: LTX-2 Two-Pass Video Pipeline
Used by all LTX-2 workflows (i2v, t2v, canny, depth).
```
Pass 1: CheckpointLoader → CFGGuider(cfg=1) → euler → SamplerCustomAdvanced
Pass 2: LTXVLatentUpsampler → CFGGuider(cfg=4) → gradient_estimation → SamplerCustomAdvanced
Audio:  LTXVEmptyLatentAudio → LTXVConcatAVLatent → MultimodalGuider
Output: LTXVSeparateAVLatent → VAEDecode → VHS_VideoCombine (MP4+audio)
```

### Pattern D: Reference Conditioning (Flux/Klein Image Edit)
```
LoadImage → ImageScaleToTotalPixels(1MP) → VAEEncode → ReferenceLatent(index=0)
ReferenceLatent applied to BOTH positive AND negative conditioning
For multi-image: chain multiple ReferenceLatent with incrementing index
```

### Pattern E: Wan 2.2 Dual-Noise Video Pipeline — NEW
Used by Wan 2.2 workflows and 6-keyframes template.
```
UNETLoader(high_noise) → LoRA(high_noise) → KSamplerAdvanced (first pass)
UNETLoader(low_noise) → LoRA(low_noise) → KSamplerAdvanced (second pass)
CLIPLoader(umt5_xxl, type=wan) → CLIPTextEncode
ModelSamplingSD3(shift=5/8) → sampling
VAEDecode(wan_2.1_vae) → CreateVideo → SaveVideo
```

### Pattern F: HunyuanVideo 1.5 Pipeline — NEW
```
DualCLIPLoader(qwen_2.5_vl + byt5_small, type=hunyuan_video_15) → CLIPTextEncode
[CLIPVisionLoader(sigclip) → CLIPVisionEncode] (i2v only)
CheckpointLoader → ModelSamplingSD3(shift=2) → CFGGuider(cfg=1) → SamplerCustomAdvanced
HunyuanVideo15LatentUpscaleWithModel → upscale to 1080p
HunyuanVideo15SuperResolution(0.7) → final enhancement
EasyCache → acceleration
VAEDecodeTiled → output
```

### Pattern G: Kandinsky 5 Pipeline — NEW
```
UNETLoader → ModelSamplingSD3(shift=3-5) → KSampler | KSamplerAdvanced
DualCLIPLoader(qwen_2.5_vl + clip_l, type=kandinsky5[_image]) → CLIPTextEncode
VAELoader(ae | hunyuan_video_vae) → VAEDecode
[Kandinsky5ImageToVideo | EmptyLatentImage] → latent
```

---

## Model Family Summary

### Text Encoder Matrix

| Family | CLIP/Text Encoder | Loader Type | CLIP Type |
|---|---|---|---|
| **Qwen Image** | `qwen_2.5_vl_7b_fp8_scaled` | CLIPLoader | `qwen_image` |
| **Flux.2 Dev** | `mistral_3_small_flux2_fp8` | CLIPLoader | `flux2` |
| **Flux.2 Klein 4B** | `qwen_3_4b` | CLIPLoader | `flux2` |
| **Flux.2 Klein 9B** | `qwen_3_8b_fp8mixed` | CLIPLoader | `flux2` |
| **Kandinsky 5 (image)** | `qwen_2.5_vl_7b` + `clip_l` | DualCLIPLoader | `kandinsky5_image` |
| **Kandinsky 5 (video)** | `qwen_2.5_vl_7b` + `clip_l` | DualCLIPLoader | `kandinsky5` |
| **HunyuanVideo 1.5** | `qwen_2.5_vl_7b` + `byt5_small_glyphxl_fp16` | DualCLIPLoader | `hunyuan_video_15` |
| **Wan 2.2** | `umt5_xxl_fp8_e4m3fn_scaled` | CLIPLoader | `wan` |
| **LTX-2** | `gemma_3_12B_it` (or `fp4_mixed`) | LTXAVTextEncoderLoader | (built-in) |

### VAE Matrix

| VAE | Families |
|---|---|
| `qwen_image_vae.safetensors` | All Qwen Image/Edit/Templates |
| `qwen_image_layered_vae.safetensors` | Qwen Layered Control only |
| `flux2-vae.safetensors` | Flux 2 Dev, Flux 2 Klein |
| `ae.safetensors` | Kandinsky 5 Image |
| `hunyuan_video_vae_bf16.safetensors` | Kandinsky 5 Video |
| `hunyuanvideo15_vae_fp16.safetensors` | HunyuanVideo 1.5 |
| `wan_2.1_vae.safetensors` | Wan 2.2, 6-keyframes |
| `vae-ft-mse-840000-ema-pruned.safetensors` | LTX-2 Depth (Lotus estimation) |
| LTX-2 built-in VAE | LTX-2 (via CheckpointLoaderSimple) |

### Noise Schedule Matrix

| Model Family | Noise Schedule | Shift Value |
|---|---|---|
| Qwen Image t2i | ModelSamplingAuraFlow | 3.0–3.1 |
| Qwen Image Edit | ModelSamplingAuraFlow | 3.0–3.1 |
| Qwen Layered Control | ModelSamplingAuraFlow | 1.0 |
| Flux 2 | Flux2Scheduler | shift=1 |
| Kandinsky 5 Image | ModelSamplingSD3 | 3 |
| Kandinsky 5 Video | ModelSamplingSD3 | 5 |
| HunyuanVideo 1.5 | ModelSamplingSD3 | 2 (ComfyUI) / 7-9 (official) |
| Wan 2.2 I2V | ModelSamplingSD3 | 5 |
| Wan 2.2 T2V | ModelSamplingSD3 | 8 |
| LTX-2 | LTXVScheduler | max_shift=2.05, base_shift=0.95 |

---

## API Usage

### Server Configuration
- **URL:** http://127.0.0.1:8188 (default)
- **Token:** Get from your ComfyUI settings
- **API Script:** `scripts/comfy_api.py`
- **Control Script:** `scripts/comfy_control.sh`

### Upload Image
```bash
curl -X POST "http://127.0.0.1:8000/upload/image?token=TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "overwrite=true"
```

### Submit Workflow
```python
from comfy_api import run_workflow
files = run_workflow("127.0.0.1:8000", token, workflow_json)
```

---

## Quick Reference: Task → Workflow

### Image Tasks

| Task | Best Workflow | Settings | Speed |
|------|--------------|----------|-------|
| Text-to-image (fast) | image_qwen_image_2512_with_2steps_lora | 2 steps, CFG 1 | ~10s |
| Text-to-image (quality) | image_qwen_Image_2512 | 50 steps, CFG 4 | ~90s |
| Text-to-image (alt, good text) | image_kandinsky5_t2i | 50 steps, CFG 3.5 | ~60s |
| Background removal | image_qwen_image_edit_2511 (Lightning) | 4 steps, CFG 1 | ~15s |
| Style/material transfer | image_qwen_image_edit_2511 | 40 steps, CFG 4 | ~120s |
| Image to realistic photo | templates-image_to_real | 8 steps, CFG 1 | ~20s |
| Light/color transfer | templates-portrait_light_migration | 8 steps, CFG 1 | ~20s |
| 8 camera angles | templates-1_click_multiple_*_angles | 4 steps × 8, CFG 1 | ~60s |
| Image edit (fast, Flux) | image_flux2_klein_image_edit_9b_distilled | 4 steps, CFG 1 | ~15s |
| Image edit (quality, Flux) | image_flux2_klein_image_edit_9b_base | 20 steps, CFG 5 | ~60s |
| Layered composition | image_qwen_image_layered_control | 20 steps, CFG 2.5 | ~45s |

### Video Tasks

| Task | Best Workflow | Settings | Speed |
|------|--------------|----------|-------|
| Image to video (quality, 1080p) | video_hunyuan_video_1.5_720p_i2v | 8 steps + upscale + SR | ~3min |
| Text to video (quality, 1080p) | video_hunyuan_video_1.5_720p_t2v | 8 steps + upscale + SR | ~3min |
| Image to video (Wan, 640px) | video_wan2_2_14B_i2v | 20 steps, CFG 3.5 | ~2min |
| Text to video (Wan, 640px) | video_wan2_2_14B_t2v | 20 steps, CFG 3.5 | ~2min |
| Image to video (Kandinsky, 5s) | video_kandinsky5_i2v | 50 steps, CFG 5 | ~3min |
| 6-keyframe interpolation | templates-6-key-frames | 4 steps × 5 segments | ~5min |
| Image to video (LTX, +audio) | video_ltx2_i2v | 20 steps × 2 passes | ~5min |
| Text to video (LTX, +audio) | video_ltx2_t2v | 20 steps × 2 passes | ~5min |
| Canny-guided video | video_ltx2_canny_to_video | 20 steps × 2 passes | ~5min |
| Depth-guided video | video_ltx2_depth_to_video | 20 steps × 2 passes | ~6min |

---

## Troubleshooting

### Common Issues
1. **"Model not found":** Check model paths match workflow node names exactly
2. **"Tensor size mismatch":** Ensure using correct model type (edit vs generation vs layered)
3. **Wrong VAE:** Layered control uses `qwen_image_layered_vae`, not `qwen_image_vae`
4. **Klein distilled poor quality:** Use CFG=1 and ConditioningZeroOut, NOT explicit negative prompt
5. **Video OOM:** Use multi-GPU patcher or reduce frame count/resolution
6. **Kandinsky 5 wrong CLIP type:** Must use `kandinsky5_image` for t2i, `kandinsky5` for video
7. **Wan 2.2 wrong shift:** I2V uses shift=5, T2V uses shift=8 — mixing causes poor quality
8. **HunyuanVideo poor quality at low steps:** Official recommends 50 steps for best quality; 8 steps is accelerated mode
9. **LTX-2 no audio:** Ensure LTXVAudioVAELoader and LTXVConcatAVLatent nodes are connected

### Performance Tips
- Lightning/Turbo LoRAs: 4-10x faster with minimal quality loss
- fp8 models for lower VRAM (all loaded workflows use fp8 by default)
- Klein 9B Distilled: 5x faster than base (4 vs 20 steps) with good quality
- LTX-2 video: initial 768×512 latent → upscale pass for quality
- HunyuanVideo: EasyCache node for training-free acceleration
- Wan 2.2: LightX2V LoRAs reduce steps from 20+ to 4
- Kandinsky 5: no-CFG checkpoint runs 2× faster (50→25 effective steps)
