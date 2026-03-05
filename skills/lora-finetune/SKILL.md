---
name: lora-finetune
description: LoRA fine-tuning pipeline for Stable Diffusion on Apple Silicon — dataset prep, training, evaluation with LLM-as-judge scoring. Use when fine-tuning image generation models for consistent style, custom characters, or domain-specific visuals. Requires Python with torch and diffusers.
version: 1.0.0
metadata:
  {
      "openclaw": {
            "emoji": "\ud83c\udfa8",
            "requires": {
                  "bins": [
                        "python3"
                  ],
                  "env": [
                        "HF_TOKEN"
                  ]
            },
            "primaryEnv": "HF_TOKEN",
            "network": {
                  "outbound": true,
                  "reason": "Downloads base models from Hugging Face Hub (huggingface.co). Training runs locally on-device."
            }
      }
}
---

# LoRA Fine-Tuning (Apple Silicon)

Train custom LoRA adapters for Stable Diffusion 1.5 on Mac hardware. Tested on M4 24GB — produces 3.1MB weight files in ~15 minutes at 500 steps.

## Hardware Requirements

| Config | Model | Resolution | VRAM |
|---|---|---|---|
| M4 24GB | SD 1.5 | 512×512 | ✅ Works |
| M4 24GB | SDXL | 512×512 | ⚠️ Tight, may OOM |
| M4 24GB | FLUX.1-schnell | Any | ❌ OOMs |
| M4 Pro 48GB | SDXL | 1024×1024 | ✅ Estimated |

## Training Pipeline

1. **Prepare dataset:** 15-25 images in consistent style, 512×512, with text captions
2. **Train LoRA:** 500 steps, learning rate 1e-4, rank 4
3. **Evaluate:** Generate test images, compare base vs LoRA vs reference (Gemini/DALL-E)
4. **Score:** LLM-as-judge rates each on style consistency, quality, prompt adherence

## Quick Start

```bash
# Prepare training images in a folder
ls training_data/
# image_001.png  image_001.txt  image_002.png  image_002.txt ...

# Train (see scripts/train_lora.py for full options)
python3 scripts/train_lora.py \
  --data_dir ./training_data \
  --output_dir ./lora_weights \
  --steps 500 \
  --lr 1e-4 \
  --rank 4
```

## Evaluation with LLM-as-Judge

```python
# Compare base model vs LoRA vs commercial (Gemini/DALL-E)
# Pixtral Large scores each image 1-10 on:
# - Style consistency with training data
# - Image quality and coherence
# - Prompt adherence

# Our results: Base 6.8 → LoRA 9.0 → Gemini 9.5
# Lesson: Gemini wins without training, but LoRA closes the gap significantly
```

## Key Lessons

- **float32 required on MPS** — float16 silently produces NaN on Apple Silicon for SD pipelines
- **mflux is faster than PyTorch MPS for FLUX** (~105s vs ~90min) but doesn't support LoRA training
- **SD 1.5 is the ceiling for 24GB** — FLUX LoRA OOMs even with gradient checkpointing
- **15-25 images is the sweet spot** — fewer undertrain, more doesn't help proportionally
- **Gemini (Imagen 4.0) beats fine-tuned SD 1.5** with zero training — use commercial APIs for production, LoRA for experimentation and offline use

## Files

- `scripts/train_lora.py` — Training script with Apple Silicon MPS support
- `scripts/compare_models.py` — LLM-as-judge evaluation comparing base vs LoRA vs reference
