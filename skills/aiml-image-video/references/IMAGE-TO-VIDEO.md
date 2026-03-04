# Image-to-Video (I2V) Generation

Generate dynamic videos from a starting image and a prompt.

## Models

- `alibaba/wan-2-6-i2v` (Recommended)
- `kling-ai/kling-v1.5`

## Usage

```bash
python3 {baseDir}/scripts/gen_video.py \
  --model "alibaba/wan-2-6-i2v" \
  --prompt "A person drinking coffee while walking in the rain" \
  --image-url "https://path.to/starting-image.jpg"
```
