---
name: local-ocr
description: >
  Local OCR (optical character recognition) on this Mac (localhost) via MLX.
  Default model: PaddleOCR-VL-1.5-6bit (fastest, lowest memory, best accuracy).
  Supports Chinese, English, mixed text, scene text, receipts, documents.
  Use when the user needs to extract text from images, do OCR on photos/screenshots/scans/PDFs,
  read text in pictures, digitize documents, or any image-to-text task that should run locally.
---

# Local OCR

Host IP: `localhost` | Port: `8787` | LAN accessible

## Default Model

| Item | Value |
|------|-------|
| Model | PaddleOCR-VL-1.5-6bit |
| Model ID | `paddleocr-vl-6bit` |
| HuggingFace path | `mlx-community/PaddleOCR-VL-1.5-6bit` |
| Speed | ~185 t/s |
| Memory | ~3.3 GB |
| Prompt | `OCR:` |

Also available: `paddleocr-vl-8bit` (same accuracy, slightly slower).

## Python (mlx-vlm direct)

```python
from mlx_vlm import generate, load
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

model, processor = load("mlx-community/PaddleOCR-VL-1.5-6bit")
config = load_config("mlx-community/PaddleOCR-VL-1.5-6bit")

prompt = apply_chat_template(processor, config, "OCR:", num_images=1)
out = generate(model, processor, prompt, "image.jpg",
               max_tokens=512, temperature=0.0, verbose=False)
print(out.text if hasattr(out, "text") else out)
```

## CLI

```bash
cd ~/.mlx-server/venv
python -m mlx_vlm.generate \
  --model mlx-community/PaddleOCR-VL-1.5-6bit \
  --image image.jpg \
  --prompt "OCR:" \
  --max-tokens 512 \
  --temp 0.0
```

## Batch OCR

```python
from pathlib import Path
from mlx_vlm import generate, load
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

model, processor = load("mlx-community/PaddleOCR-VL-1.5-6bit")
config = load_config("mlx-community/PaddleOCR-VL-1.5-6bit")

for img in sorted(Path("images/").glob("*.jpg")):
    prompt = apply_chat_template(processor, config, "OCR:", num_images=1)
    out = generate(model, processor, prompt, str(img),
                   max_tokens=512, temperature=0.0, verbose=False)
    text = out.text if hasattr(out, "text") else str(out)
    print(f"{img.name}: {text}")
```

## Notes

- Venv: `~/.mlx-server/venv` (activate or use full path to python)
- Prompt must be exactly `OCR:` for PaddleOCR-VL models
- `temperature=0.0` for deterministic output
- RGBA images (alpha-only content) must be converted to RGB first:
  ```python
  from PIL import Image
  img = Image.open("rgba.png").convert("RGB")
  img.save("rgb.jpg")
  ```
- High-res images (>3MB) may take longer; resize if speed matters

## Service Management

```bash
launchctl kickstart -k gui/$(id -u)/com.mlx-server
```
