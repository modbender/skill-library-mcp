## DrawThings API Reference

DrawThings exposes an Automatic1111-compatible REST API for programmatic image generation.

### Base URL

Default: `http://127.0.0.1:7860`

Configure via `$DRAWTHINGS_URL` environment variable.

### Text-to-Image Generation

**Endpoint:** `POST /sdapi/v1/txt2img`

**Request Body:**

```json
{
  "prompt": "a cute cat in a cyberpunk city",
  "negative_prompt": "blurry, low quality",
  "steps": 20,
  "sampler_name": "DPM++ 2M Karras",
  "cfg_scale": 7.0,
  "width": 512,
  "height": 512,
  "batch_size": 1,
  "seed": -1
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text description of the image to generate |
| `negative_prompt` | string | `""` | What to avoid in the image |
| `steps` | integer | `20` | Number of diffusion steps (8-150) |
| `sampler_name` | string | `"DPM++ 2M Karras"` | Sampling algorithm |
| `cfg_scale` | float | `7.0` | Classifier-free guidance scale (1.0-30.0) |
| `width` | integer | `512` | Image width (64-2048, multiples of 64) |
| `height` | integer | `512` | Image height (64-2048, multiples of 64) |
| `batch_size` | integer | `1` | Number of images to generate (1-8) |
| `seed` | integer | `-1` | Random seed (-1 for random) |

**Available Samplers:**

- `"DPM++ 2M Karras"` - High quality, balanced speed
- `"DPM++ 2M"` - Similar to Karras, slightly different noise schedule
- `"Euler A"` - Fast, good for drafts
- `"Euler"` - Deterministic version of Euler A
- `"UniPC Trailing"` - Very fast, 8-12 steps
- `"LCM"` - Ultra-fast, requires LCM models
- `"DDIM"` - Classic sampler
- `"PLMS"` - Classic sampler

**Response:**

```json
{
  "images": ["base64_encoded_png_1", "base64_encoded_png_2"],
  "parameters": {
    "prompt": "a cute cat in a cyberpunk city",
    "steps": 20,
    "sampler_name": "DPM++ 2M Karras",
    "cfg_scale": 7.0,
    "seed": 1234567890,
    "width": 512,
    "height": 512
  },
  "info": "{\"seed\": 1234567890, \"all_prompts\": [...], ...}"
}
```

The `images` array contains base64-encoded PNG data. The `info` field is a JSON string with detailed generation metadata.

### Get Options

**Endpoint:** `GET /sdapi/v1/options`

Returns current DrawThings configuration including available models, samplers, and settings.

### Set Options

**Endpoint:** `POST /sdapi/v1/options`

Update DrawThings configuration (e.g., change active model).

**Example:**
```json
{
  "sd_model_checkpoint": "model_name.safetensors"
}
```

### Get Models

**Endpoint:** `GET /sdapi/v1/sd-models`

Returns list of available Stable Diffusion models.

**Response:**
```json
[
  {
    "title": "sd_xl_base_1.0",
    "model_name": "sd_xl_base_1.0",
    "hash": "..."
  }
]
```

### Get Samplers

**Endpoint:** `GET /sdapi/v1/samplers`

Returns list of available sampling algorithms.

**Response:**
```json
[
  {"name": "DPM++ 2M Karras"},
  {"name": "Euler A"},
  {"name": "UniPC Trailing"}
]
```

### Progress Polling

**Endpoint:** `GET /sdapi/v1/progress`

Check generation progress for long-running operations.

**Response:**
```json
{
  "progress": 0.65,
  "eta_relative": 12.5,
  "state": {
    "sampling_step": 13,
    "sampling_steps": 20
  }
}
```

### Interrupt Generation

**Endpoint:** `POST /sdapi/v1/interrupt`

Stop the current generation.

## Tips

**CFG Scale Guidelines:**
- 1.0-3.0: Highly creative, may drift from prompt
- 5.0-8.0: Balanced (recommended)
- 10.0-15.0: Very literal interpretation
- 15.0+: Often over-saturated

**Steps Guidelines:**
- 8-12: Fast drafts (UniPC/Euler A)
- 20-30: Standard quality (DPM++ 2M Karras)
- 50+: Diminishing returns

**Dimension Guidelines:**
- Use multiples of 64 (512, 576, 640, 768, 1024)
- SD 1.5 models trained on 512x512
- SDXL models trained on 1024x1024
- Non-square ratios supported (e.g., 768x512 for landscape)

**Batch Size:**
- Generates variations with different seeds
- Uses same prompt/settings for all images
- Faster than multiple separate requests
