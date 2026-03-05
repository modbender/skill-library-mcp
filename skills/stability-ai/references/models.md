# Stability AI API Reference

## API Versions

### V1 API (Legacy)
Endpoint: `/v1/generation/{model}/text-to-image`
- JSON-based request/response
- Supports SDXL and SD3 models
- Full control over parameters

### V2 API (Stable Image Core)
Endpoint: `/v2beta/stable-image/generate/core`
- Multipart form-data request
- Native aspect ratio support
- Optimized for Stable Image models

## Models

### V1 API Models
- **SDXL 1.0**: `stable-diffusion-xl-1024-v1-0` (Reliable, fast, default)
- **SD3 Medium**: `stable-diffusion-3-medium` (Newest, balanced)
- **SD3 Large**: `stable-diffusion-3-large` (Highest quality)

### V2 API Models
- Uses Stable Image Core engine (model specified via API configuration)

## Parameters

### Common Parameters
- **Steps**: 30-50 (Tradeoff quality vs speed)
- **CFG Scale**: 4-7 for V1, 1-35 for V2 (Prompt adherence)
- **Aspect Ratios**: 1:1, 16:9, 9:16, 21:9, 4:3, 3:4
- **Seed**: Integer for reproducible results (omit for random)

### Style Presets (V1 API)
Available styles: enhance, anime, photographic, digital-art, comic-book, fantasy-art, line-art, analog-film, neon-punk, isometric, low-poly, origami, modeling-compound, cinematic, 3d-model, pixel-art, tile-texture

### Output Formats
- PNG (default, lossless)
- JPEG/JPG (lossy, smaller file size)
- WebP (modern, efficient compression)

## Costs
- SDXL: ~0.2 credits/image
- SD3 Medium: ~4 credits/image
- SD3 Large: ~6 credits/image
- Stable Image Core (V2): Varies by resolution and settings
