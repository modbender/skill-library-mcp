---
name: zenmux-image-generation
description: Generate images via ZenMux API (Pro/Elite). Supports Text-to-Image, Image-to-Image, and Multi-Image reference fusion.
---

# ZenMux Image Generation Skill (Gemini 3 Pro)

This skill uses the ZenMux API to generate high-fidelity images using the **Gemini 3 Pro Image (Nano Banana Pro)** model.

## Features

*   **Text-to-Image**: Generate visuals from descriptive prompts.
*   **Image-to-Image**: Modify an existing image based on a prompt.
*   **Multi-Image Fusion**: Combine elements or styles from multiple reference images (e.g., character from one image, costume/style from another).

## Usage

To generate an image, execute the `scripts/generate.py` script.

**IMPORTANT:**
*   You must set the `ZENMUX_API_KEY` environment variable.
*   **Model**: Defaults to `google/gemini-3-pro-image-preview`.
*   **Provider**: ZenMux (Requires **Pro** or higher plan).

### 1. Text-to-Image
```bash
ZENMUX_API_KEY="YOUR_KEY" python3 scripts/generate.py --prompt "a cybernetic lobster in space"
```

### 2. Image-to-Image
```bash
ZENMUX_API_KEY="YOUR_KEY" python3 scripts/generate.py --prompt "make it winter" --images "summer.png"
```

### 3. Multi-Image Fusion (Advanced)
```bash
ZENMUX_API_KEY="YOUR_KEY" python3 scripts/generate.py --prompt "put this child in this costume" --images "child.png" "costume.jpg"
```

### Arguments

*   `--prompt` (required): Text description of the task.
*   `--images` (optional): Path(s) to one or more reference image files.
*   `--model` (optional): Defaults to `google/gemini-3-pro-image-preview`.
*   `--output` (optional): Defaults to `generated_image.png`.
