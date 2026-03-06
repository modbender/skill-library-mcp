---
name: civitai-ai-art
description: Generate AI artwork using CivitAI's JavaScript SDK. Use when the user wants to create AI-generated images using Stable Diffusion models from CivitAI, including anime-style illustrations, character art, or custom generations with specific prompts, negative prompts, seeds, and sampling settings.
---

# CivitAI AI Art Generation

Generate AI artwork using CivitAI's official JavaScript SDK.

## Prerequisites

- Node.js 18+ environment
- CivitAI API access token (stored in environment variable `CIVITAI_API_TOKEN`)
- `civitai` npm package installed

## Installation

```bash
npm install civitai
```

## Usage

```bash
node scripts/get_illust.js [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--prompt` | Main generation prompt (required) | - |
| `--negative` | Negative prompt | "bad quality,worst quality,worst detail,sketch,censor" |
| `--width` | Image width | 832 |
| `--height` | Image height | 1216 |
| `--seed` | Random seed | random |
| `--steps` | Sampling steps | 20 |
| `--cfg-scale` | CFG scale | 5 |
| `--model` | Model URN identifier | "urn:air:sdxl:checkpoint:civitai:827184@2514310" |
| `--sampler` | Sampler algorithm | "Euler a" |
| `--clip-skip` | CLIP skip layers | 2 |
| `--output` | Output file path | "./output.png" |
| `--lora` | LoRA network URN with optional strength (format: `urn,strength`) | - |

### Example Usage

```bash
# 基础生成
node scripts/get_illust.js --prompt "1girl, red hair, blue eyes, maid outfit, smile" --output maid.png

# 高级设置
node scripts/get_illust.js \
  --prompt "1girl, long silver hair, purple eyes, magical girl, cityscape at night" \
  --negative "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet" \
  --width 1024 \
  --height 1536 \
  --steps 28 \
  --cfg-scale 6 \
  --seed 42 \
  --output magical_girl.png

# 使用不同模型
node scripts/get_illust.js \
  --prompt "fantasy landscape, floating islands, waterfalls" \
  --model "urn:air:sdxl:checkpoint:civitai:101055@128641" \
  --output landscape.png

# 使用 LoRA
node scripts/get_illust.js \
  --prompt "1girl, red hair, blue eyes, maid outfit, smile" \
  --lora "urn:air:sdxl:lora:civitai:162141@182559,0.8" \
  --output maid_with_lora.png

# 使用多个 LoRA
node scripts/get_illust.js \
  --prompt "1girl, cat ears, cute smile, IncrsAhri, multiple tails" \
  --lora "urn:air:sd1:lora:civitai:162141@182559,1.0" \
  --lora "urn:air:sd1:lora:civitai:176425@198856,0.6" \
  --output multi_lora.png
```

### Markdown 链接示例

生成图片后，使用 markdown 格式包裹链接：

```markdown
[生成的图片](https://blobs-temp.s3.us-west-004.backblazeb2.com/...)
```

## Scheduler Options

Available sampler values:

| Sampler Name | Enum Value |
|--------------|------------|
| Euler a | EULER_A |
| Euler | EULER |
| LMS | LMS |
| Heun | HEUN |
| DPM2 | DPM2 |
| DPM2 a | DPM2_A |
| DPM++ 2S a | DPM2_SA |
| DPM++ 2M | DPM2_M |
| DPM++ SDE | DPM_SDE |
| DPM fast | DPM_FAST |
| DPM adaptive | DPM_ADAPTIVE |
| LMS Karras | LMS_KARRAS |
| DPM2 Karras | DPM2_KARRAS |
| DPM2 a Karras | DPM2_A_KARRAS |
| DPM++ 2S a Karras | DPM2_SA_KARRAS |
| DPM++ 2M Karras | DPM2_M_KARRAS |
| DPM++ SDE Karras | DPM_SDE_KARRAS |
| DDIM | DDIM |
| PLMS | PLMS |
| UniPC | UNIPC |
| LCM | LCM |
| DDPM | DDPM |
| DEIS | DEIS |

## Notes

- Requires Node.js 18+ for native fetch support
- Store API tokens securely using environment variables
- Generated images are subject to CivitAI's terms of service
- Some models may require specific permissions or subscriptions
- The script always waits for job completion by default
