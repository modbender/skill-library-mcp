# Video Upscaling

Increase video resolution with AI enhancement.

## Tools

### Topaz Video AI

**Best commercial option:**
```bash
# CLI (after install)
tvai_cli -i input.mp4 -o output.mp4 --model proteus --scale 2
```

**Models:**
- Proteus — best quality, slow
- Artemis — fast, good quality
- Gaia — high quality, balanced
- Theia — fine detail recovery

**Pricing:** $299 perpetual license

### Real-ESRGAN Video

```bash
# Extract frames
ffmpeg -i input.mp4 -qscale:v 2 frames/%04d.jpg

# Upscale frames
realesrgan-ncnn-vulkan -i frames -o upscaled -n realesrgan-x4plus-anime

# Reassemble
ffmpeg -framerate 30 -i upscaled/%04d.jpg -c:v libx264 -crf 18 output.mp4
```

### Video2X (GUI Wrapper)

```bash
# Install
pip install video2x

# Upscale
video2x -i input.mp4 -o output.mp4 -p3 --scale 2
```

**Engines:**
- waifu2x
- srmd
- realsr
- anime4k

### FFmpeg Filters

```bash
# Basic scaling (not AI)
ffmpeg -i input.mp4 -vf "scale=3840:2160:flags=lanczos" output.mp4

# With sharpening
ffmpeg -i input.mp4 -vf "scale=3840:2160:flags=lanczos,unsharp=5:5:1.0" output.mp4
```

### Replicate

```python
import replicate

output = replicate.run(
    "nightmareai/real-esrgan-video:...",
    input={
        "video": open("input.mp4", "rb"),
        "scale": 4,
        "model": "realesrgan-x4plus"
    }
)
```

## Resolution Targets

| Source | 2x | 4x |
|--------|-----|-----|
| 480p | 960p | 1920p (1080p) |
| 720p | 1440p | 2880p |
| 1080p | 4K | 8K |

## Processing Order

1. **Stabilize** — if needed
2. **Denoise** — before upscaling
3. **Upscale** — main enhancement
4. **Sharpen** — light post-sharpening
5. **Encode** — final compression

## Best Practices

- **Denoise first** — upscaling amplifies noise
- **Match content type** — anime models for anime
- **Don't over-upscale** — 2x usually sufficient
- **Test segment** — render 10s before full video
- **Storage** — upscaled video files are large

## Quality vs Speed

| Model | Quality | Speed | Use Case |
|-------|---------|-------|----------|
| Real-ESRGAN | Good | Slow | Archival |
| Topaz Proteus | Excellent | Very slow | Professional |
| Topaz Artemis | Good | Fast | Batch work |
| Anime4K | Good (anime) | Fast | Anime content |

## Encoding Output

**Master (archival):**
```bash
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 3 output.mov
```

**Delivery (web):**
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow output.mp4
```

**H.265 (smaller files):**
```bash
ffmpeg -i input.mp4 -c:v libx265 -crf 20 -preset medium output.mp4
```
