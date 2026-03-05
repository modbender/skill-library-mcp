## Recommended Models for DrawThings

DrawThings supports Stable Diffusion 1.5, SDXL, and custom fine-tuned models.

### Stable Diffusion 1.5 Models

**Base Models:**
- **sd-v1-5.safetensors** - Original SD 1.5, good all-rounder
- **realisticVision** - Photorealistic images
- **dreamshaper** - Artistic/creative style
- **deliberate** - Balanced realism and creativity

**Resolution:** 512x512 native (can upscale)

### SDXL Models

**Base Models:**
- **sd_xl_base_1.0.safetensors** - Base SDXL model
- **juggernautXL** - Photorealistic SDXL variant
- **dreamshaper-xl** - Artistic SDXL variant

**Resolution:** 1024x1024 native (better quality at higher res)

### Specialized Models

**Art Styles:**
- **midjourney-v6** - Midjourney-like aesthetic
- **stable-diffusion-v2-aesthetic** - Aesthetic scoring

**Anime/Illustration:**
- **anything-v5** - Anime style
- **waifu-diffusion** - Anime characters

**Architecture/Design:**
- **openjourney** - Architectural visualization
- **redshift-diffusion** - 3D rendered look

### LoRA Models

DrawThings supports LoRA (Low-Rank Adaptation) models for style transfer and fine-tuning:

- Place LoRA files in DrawThings LoRA directory
- Select via UI before generation
- Typically use weight 0.5-1.0

**Popular LoRAs:**
- **detail-tweaker** - Enhance details
- **add-more-details** - Increase image complexity
- **film-grain** - Analog photography look

### Model Downloads

**CivitAI:** https://civitai.com
- Largest community model repository
- Rating system and examples
- Download `.safetensors` format

**Hugging Face:** https://huggingface.co/models
- Official model hub
- Stable Diffusion 1.5: `runwayml/stable-diffusion-v1-5`
- SDXL: `stabilityai/stable-diffusion-xl-base-1.0`

### Installation

1. Download model file (`.safetensors` or `.ckpt`)
2. Open DrawThings app
3. Go to Model Manager
4. Import model file
5. Select model from dropdown

### Model Selection Tips

**For speed:** SD 1.5 models (512x512)
**For quality:** SDXL models (1024x1024)
**For photorealism:** realisticVision, juggernautXL
**For art/illustration:** dreamshaper, anything-v5
**For specific styles:** Use LoRAs on base models

### Memory Usage

| Model Type | VRAM/RAM | Generation Time (M2) |
|------------|----------|---------------------|
| SD 1.5 (512x512) | ~4GB | 10-15s @ 20 steps |
| SDXL (1024x1024) | ~8GB | 30-45s @ 20 steps |
| SD 1.5 + LoRA | ~4.5GB | 12-18s @ 20 steps |

DrawThings uses MLX/CoreML on Mac, so RAM is shared with GPU.
