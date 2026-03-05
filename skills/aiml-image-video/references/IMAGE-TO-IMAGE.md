# Image-to-Image (I2I) Generation

Modify existing images based on professional prompts.

## Models

- `alibaba/qwen-image-edit`
- `stability-ai/sdxl-edit` (v1 standard)

## Usage

```bash
python3 {baseDir}/scripts/gen_image.py \
  --model "alibaba/qwen-image-edit" \
  --prompt "Make the house look like it's made of gingerbread" \
  --image-url "https://path.to/original-house.jpg"
```
