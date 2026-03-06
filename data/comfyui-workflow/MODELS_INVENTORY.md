# ComfyUI Models Inventory

> Example model inventory — update with your local paths
> Models are stored in the `models/` subdirectory
>
> **⚠️ AGENTS: DO NOT REFERENCE THIS FILE until you have updated it with the user's actual model inventory.** The content below describes example models and paths that may not exist in the user's setup. Using outdated data will cause "model not found" errors.

Model root: `<ComfyUI>/models/`

---

## Availability Status Legend

- ✅ **Installed + Workflow** — Model installed and has a workflow JSON
- 📦 **Installed, No Workflow** — Model installed but no workflow JSON yet (usable if you build a workflow)
- ❌ **Missing** — Referenced in a workflow but NOT installed (needs download)

---

## diffusion_models/ (508 GB)

### Image Models

| File | Status | Family | Notes |
|------|--------|--------|-------|
| `qwen_image_2512_fp8_e4m3fn.safetensors` | ✅ | Qwen Image | t2i, workflows #1–2 |
| `qwen_image_edit_2509_fp8_e4m3fn.safetensors` | ✅ | Qwen Edit | edit, workflows #3, #11–14 |
| `qwen_image_edit_2511_bf16.safetensors` | ✅ | Qwen Edit | edit, workflow #4 |
| `qwen_image_fp8_e4m3fn.safetensors` | 📦 | Qwen Image | Older Qwen Image (pre-2512) |
| `qwen_image_edit_fp8_e4m3fn.safetensors` | 📦 | Qwen Edit | Older Qwen Edit (pre-2509) |
| `flux2_dev_fp8mixed.safetensors` | ✅ | Flux 2 | t2i/edit, workflow #6 |
| `flux-2-klein-base-4b-fp8.safetensors` | ✅ | Flux 2 Klein | edit, workflow #7 |
| `kandinsky5lite_t2i.safetensors` | ✅ | Kandinsky 5 | t2i, workflow #10 |
| `ovis_image_bf16.safetensors` | 📦 | Ovis | Multimodal image generation (ovis_2.5 text encoder) |
| `z_image_turbo_bf16.safetensors` | 📦 | Z-Image | Turbo image generation; has pixel art style LoRA |
| `lotus-depth-d-v1-1.safetensors` | ✅ | Lotus | Depth estimation for LTX-2 depth workflow #24 |

### Video Models — Wan 2.2 Family

| File | Status | Notes |
|------|--------|-------|
| `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | ✅ | I2V high noise UNET, workflow #15 (6-keyframes) |
| `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | ✅ | I2V low noise UNET, workflows #15, #19 |
| `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` | ✅ | T2V high noise UNET |
| `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` | ✅ | T2V low noise UNET, workflow #20 |
| `wan2.2_fun_control_5B_bf16.safetensors` | 📦 | Fun Control 5B — video editing with ControlNet-like guidance |
| `wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors` | 📦 | Fun Control 14B high noise — structural video control |
| `wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors` | 📦 | Fun Control 14B low noise — structural video control |
| `wan2.2_s2v_14B_fp8_scaled.safetensors` | 📦 | Subject-to-Video 14B — generate video of a specific subject |
| `wan2.2_ti2v_5B_fp16.safetensors` | 📦 | Text+Image-to-Video 5B — lightweight I2V variant |
| `Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors` | 📦 | Animate 14B — character animation from image |
| `smoothMixWan22I2VT2V_i2vHigh.safetensors` | 📦 | SmoothMix merge — smoother I2V high noise |
| `smoothMixWan22I2VT2V_i2vLow.safetensors` | 📦 | SmoothMix merge — smoother I2V low noise |
| `smoothMixWan22I2VT2V_t2vHighV20.safetensors` | 📦 | SmoothMix merge — smoother T2V high noise |
| `smoothMixWan22I2VT2V_t2vLowV20.safetensors` | 📦 | SmoothMix merge — smoother T2V low noise |
| `wan22RemixT2VI2V_i2vHighV20.safetensors` | 📦 | Remix merge — alternative I2V high noise |
| `wan22RemixT2VI2V_i2vLowV20.safetensors` | 📦 | Remix merge — alternative I2V low noise |
| `wan22RemixT2VI2V_t2vHighV20.safetensors` | 📦 | Remix merge — alternative T2V high noise |
| `wan22RemixT2VI2V_t2vLowV20.safetensors` | 📦 | Remix merge — alternative T2V low noise |

### Video Models — Other Families

| File | Status | Notes |
|------|--------|-------|
| `hunyuanvideo1.5_720p_i2v_fp16.safetensors` | ✅ | HunyuanVideo 1.5 I2V, workflow #16 |
| `hunyuanvideo1.5_720p_t2v_fp16.safetensors` | ✅ | HunyuanVideo 1.5 T2V, workflow #17 |
| `hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors` | 📦 | HunyuanVideo 1.5 1080p SuperRes (distilled, CFG=1) — can replace current SR step |
| `kandinsky5lite_i2v_5s.safetensors` | ✅ | Kandinsky 5 Lite I2V, workflow #18 |
| `kandinsky5lite_t2v_sft_5s.safetensors` | 📦 | Kandinsky 5 Lite T2V (5 sec) — same arch as I2V, no workflow yet |

---

## checkpoints/ (98 GB)

| File | Status | Family | Notes |
|------|--------|--------|-------|
| `ltx-2-19b-dev-fp8.safetensors` | ✅ | LTX-2 | I2V/T2V, workflows #21–22 |
| `ltx-2-19b-distilled.safetensors` | ✅ | LTX-2 | Distilled variant for canny/depth, workflows #23–24 |
| `ace_step_v1_3.5b.safetensors` | 📦 | ACE-Step | **Music generation** — text-to-music, 3.5B params |
| `hunyuan3d-dit-v2-mv-turbo_fp16.safetensors` | 📦 | Hunyuan3D | **3D generation** — multi-view turbo |
| `hunyuan3d-dit-v2-mv_fp16.safetensors` | 📦 | Hunyuan3D | 3D generation — multi-view standard |
| `hunyuan_3d_v2.1.safetensors` | 📦 | Hunyuan3D | 3D generation — V2.1 |
| `stable-audio-open-1.0.safetensors` | 📦 | Stable Audio | **Audio/sound generation** — text-to-audio effects |

---

## text_encoders/ (78 GB)

| File | Status | Used By |
|------|--------|---------|
| `qwen_2.5_vl_7b_fp8_scaled.safetensors` | ✅ | Qwen Image/Edit, Kandinsky 5, HunyuanVideo (DualCLIP primary) |
| `mistral_3_small_flux2_fp8.safetensors` | ✅ | Flux 2 Dev |
| `qwen_3_4b.safetensors` | ✅ | Flux 2 Klein 4B |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | ✅ | Wan 2.2 |
| `clip_l.safetensors` | ✅ | Kandinsky 5 (DualCLIP secondary) |
| `byt5_small_glyphxl_fp16.safetensors` | ✅ | HunyuanVideo 1.5 (DualCLIP secondary) |
| `gemma_3_12B_it.safetensors` | ✅ | LTX-2 (full precision) |
| `gemma_3_12B_it_fp4_mixed.safetensors` | ✅ | LTX-2 canny/depth (quantized, saves VRAM) |
| `t5-base.safetensors` | 📦 | Generic T5 — possibly for audio/music/TTS |
| `ovis_2.5.safetensors` | 📦 | Ovis image model text encoder |
| `qwen_3_8b_fp8mixed.safetensors` | ❌ **MISSING** | Flux 2 Klein 9B Base/Distilled (#8, #9) |

---

## vae/ (5.6 GB)

| File | Status | Used By |
|------|--------|---------|
| `qwen_image_vae.safetensors` | ✅ | All Qwen Image/Edit workflows |
| `flux2-vae.safetensors` | ✅ | All Flux 2 workflows |
| `ae.safetensors` | ✅ | Kandinsky 5 Image |
| `hunyuan_video_vae_bf16.safetensors` | ✅ | Kandinsky 5 Video |
| `hunyuanvideo15_vae_fp16.safetensors` | ✅ | HunyuanVideo 1.5 |
| `wan_2.1_vae.safetensors` | ✅ | Wan 2.2 (standard) |
| `wan2.2_vae.safetensors` | 📦 | Wan 2.2 (newer VAE, not used by current workflows) |
| `vae-ft-mse-840000-ema-pruned.safetensors` | ✅ | LTX-2 depth (Lotus estimation) |
| `qwen_image_layered_vae.safetensors` | ❌ **MISSING** | Qwen Layered Control (#5) |

---

## clip_vision/ 

| File | Status | Used By |
|------|--------|---------|
| `sigclip_vision_patch14_384.safetensors` | ✅ | HunyuanVideo 1.5 I2V |
| `clip_vision_h.safetensors` | 📦 | General-purpose CLIP vision (IPAdapter, etc.) |

---

## loras/ (32 GB)

### Qwen LoRAs

| File | Status | Notes |
|------|--------|-------|
| `Qwen-Image-Lightning-4steps-V1.0.safetensors` | ✅ | Qwen 2512 speed (4 steps) |
| `Qwen-Image-Lightning-8steps-V1.0.safetensors` | 📦 | Qwen 2512 speed (8 steps) — higher quality than 4-step |
| `Wuli-Qwen-Image-2512-Turbo-LoRA-2steps-V1.0-bf16.safetensors` | ✅ | Qwen 2512 turbo (2 steps) |
| `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` | ✅ | Edit 2509 speed (4 steps) |
| `Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors` | ✅ | Edit 2509 speed (8 steps) |
| `Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` | ✅ | Edit 2511 speed (4 steps) |
| `Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors` | 📦 | Older Qwen Edit Lightning (pre-2509) |
| `Qwen-Edit-2509-Multiple-angles.safetensors` | ✅ | Multi-angle generation |
| `Qwen-Image-Edit-2509-Anything2RealAlpha.safetensors` | ✅ | Image-to-realistic-photo |
| `Qwen-Image-Edit-2509-Light-Migration.safetensors` | ✅ | Lighting transfer |
| `qwen_image_union_diffsynth_lora.safetensors` | 📦 | DiffSynth union — enhanced inpainting/editing |

### Flux 2 LoRAs

| File | Status | Notes |
|------|--------|-------|
| `Flux2TurboComfyv2.safetensors` | ✅ | Flux 2 turbo (8 steps) |
| `Flux_2-Turbo-LoRA_comfyui.safetensors` | 📦 | Alternative Flux 2 turbo LoRA |
| `flux2_berthe_morisot.safetensors` | 📦 | Berthe Morisot art style for Flux 2 |

### Wan 2.2 LoRAs

| File | Status | Notes |
|------|--------|-------|
| `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | ✅ | I2V high noise acceleration |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | ✅ | I2V low noise acceleration |
| `wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors` | ✅ | T2V high noise acceleration |
| `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` | ✅ | T2V low noise acceleration |
| `lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors` | 📦 | I2V 480p CFG+step distillation — 480p-optimized acceleration |
| `WanAnimate_relight_lora_fp16.safetensors` | 📦 | Relighting LoRA for Wan Animate |
| `next-scene_lora-v2-3000.safetensors` | 📦 | Scene transition LoRA (next scene prediction) |

### LTX-2 LoRAs

| File | Status | Notes |
|------|--------|-------|
| `ltx-2-19b-distilled-lora-384.safetensors` | ✅ | Distilled acceleration |
| `ltx-2-19b-ic-lora-canny-control.safetensors` | ✅ | Canny structural control |
| `ltx-2-19b-ic-lora-depth-control.safetensors` | ✅ | Depth structural control |
| `ltx-2-19b-lora-camera-control-dolly-left.safetensors` | ✅ | Camera dolly motion |

### Other LoRAs

| File | Status | Notes |
|------|--------|-------|
| `pixel_art_style_z_image_turbo.safetensors` | 📦 | Pixel art style for Z-Image Turbo |

---

## controlnet/

| File | Status | Notes |
|------|--------|-------|
| `Qwen-Image-InstantX-ControlNet-Inpainting.safetensors` | 📦 | Inpainting for Qwen Image — fill/repair regions |
| `Qwen-Image-InstantX-ControlNet-Union.safetensors` | 📦 | Union ControlNet for Qwen Image — multi-condition control |

## model_patches/

| File | Status | Notes |
|------|--------|-------|
| `qwen_image_canny_diffsynth_controlnet.safetensors` | 📦 | Canny edge ControlNet for Qwen Image (DiffSynth) |
| `Z-Image-Turbo-Fun-Controlnet-Union.safetensors` | 📦 | Union ControlNet for Z-Image Turbo |

## latent_upscale_models/

| File | Status | Notes |
|------|--------|-------|
| `hunyuanvideo15_latent_upsampler_1080p.safetensors` | ✅ | HunyuanVideo 720→1080p upscaler |
| `ltx-2-spatial-upscaler-x2-1.0.safetensors` | ✅ | LTX-2 2× spatial upscaler |

## audio_encoders/

| File | Status | Notes |
|------|--------|-------|
| `wav2vec2_large_english_fp16.safetensors` | ✅ | LTX-2 audio encoder (English speech) |

---

## TTS/ (Text-to-Speech)

| Directory | Status | Notes |
|-----------|--------|-------|
| `IndexTTS/` | 📦 | Chinese+English TTS (GPT-based, BigVGAN vocoder) |
| `IndexTTS-2/` | 📦 | Updated TTS with Qwen 0.6B emotion model + wav2vec2-BERT |
| `MaskGCT/` | 📦 | MaskGCT speech generation model |
| `campplus/` | 📦 | Speaker verification (campplus_cn_common.bin) |
| `speakers/` | 📦 | Speaker embedding files |
| `bigvgan_v2_22khz_80band_256x/` | 📦 | BigVGAN V2 vocoder (22kHz, shared by TTS models) |
| `w2v-bert-2.0/` | 📦 | Wav2Vec2-BERT 2.0 speech encoder |

---

## Missing Models (need download for existing workflows)

### Critical — Blocks entire workflow:

| Model | Needed By | HuggingFace Source | Download Command |
|-------|-----------|-------------------|-----------------|
| `flux-2-klein-base-9b-fp8.safetensors` | Workflow #8 (Klein 9B Base) | `black-forest-labs/FLUX.2-Klein-9B` | See below |
| `flux-2-klein-9b-fp8.safetensors` | Workflow #9 (Klein 9B Distilled) | `black-forest-labs/FLUX.2-Klein-9B` | See below |
| `qwen_3_8b_fp8mixed.safetensors` | Workflows #8, #9 (Klein 9B text encoder) | `Qwen/Qwen3-8B` | See below |
| `qwen_image_layered_control_bf16.safetensors` | Workflow #5 (Layered Control) | `Qwen/Qwen-Image-Layered-Control` | See below |
| `qwen_image_layered_vae.safetensors` | Workflow #5 (Layered Control) | `Qwen/Qwen-Image-Layered-Control` | See below |

### Optional — LoRA enhancement:

| Model | Needed By | Notes |
|-------|-----------|-------|
| `Qwen-Image-Edit-2509-Turbo-LoRA-2steps-V1.0-bf16.safetensors` | Workflow #3 (optional ultra-fast variant) | Not critical — 4-step Lightning LoRA is installed |

### Download Commands (huggingface-cli):

```bash
# Install huggingface-cli if needed
pip install -U huggingface-hub

# Flux 2 Klein 9B models → models/diffusion_models/
# (Check exact filenames on HuggingFace, may need conversion to fp8)
# huggingface-cli download black-forest-labs/FLUX.2-Klein-9B --local-dir ./models/diffusion_models/

# Qwen 3 8B text encoder → models/text_encoders/
# huggingface-cli download comfyanonymous/flux_text_encoders qwen_3_8b_fp8mixed.safetensors --local-dir ./models/text_encoders/

# Qwen Layered Control → models/diffusion_models/ + vae\
# huggingface-cli download Qwen/Qwen-Image-Layered-Control --local-dir /tmp/qwen-layered
# Then copy the safetensors to the right directories
```

---

## Additional Capabilities (installed but no workflow JSON)

These models are installed and functional but don't have corresponding workflow JSON files in `comfyui_example/`. You can build workflows for them in the ComfyUI web UI.

### 🎬 Wan 2.2 Extended Variants

| Model | Capability |
|-------|-----------|
| **Fun Control 14B** (high+low noise) | ControlNet-like guidance for video — edge/pose/depth-guided video generation |
| **Fun Control 5B** | Lightweight version of above |
| **Subject-to-Video (S2V) 14B** | Generate video of a specific subject from image — identity-preserving |
| **Text+Image-to-Video (TI2V) 5B** | Lightweight 5B I2V model (vs 14B in workflows) |
| **Animate 14B** (KJ) | Character animation from single image — LivePortrait-like |
| **SmoothMix** (4 variants) | Community-merged models for smoother, more aesthetic video |
| **Remix** (4 variants) | Community-merged models — alternative video aesthetic |

### 🖼️ Additional Image Models

| Model | Capability |
|-------|-----------|
| **Z-Image Turbo** | Fast image generation turbo model; has pixel art LoRA + Fun ControlNet Union |
| **Ovis Image** | Multimodal image generator with Ovis 2.5 text encoder |
| **ControlNets** | Qwen inpainting ControlNet + Union ControlNet + canny DiffSynth ControlNet |

### 🎵 Audio & Music

| Model | Capability |
|-------|-----------|
| **ACE-Step V1** (3.5B) | Text-to-music generation with lyrics+tags |
| **Stable Audio Open 1.0** | Text-to-audio effects (sound design, ambient sounds) |

### 🗣️ Text-to-Speech

| Model | Capability |
|-------|-----------|
| **IndexTTS** | GPT-based TTS with BigVGAN vocoder; Chinese+English |
| **IndexTTS-2** | Enhanced TTS with Qwen 0.6B emotion model + better voice quality |
| **MaskGCT** | Masked generative speech model — zero-shot voice cloning |

### 🧊 3D Generation

| Model | Capability |
|-------|-----------|
| **Hunyuan3D DiT V2** | Image-to-3D — multi-view generation from single image |
| **Hunyuan3D DiT V2 Turbo** | Fast 3D generation variant |
| **Hunyuan3D V2.1** | Latest 3D generation model |

### 📹 HunyuanVideo 1.5 Enhancement

| Model | Capability |
|-------|-----------|
| **1080p SR Distilled** | Distilled super-resolution model — faster than standard SR at CFG=1 |
| **Kandinsky 5 T2V** | Text-to-video 5-second clips (same architecture as I2V) |
