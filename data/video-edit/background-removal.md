# Video Background Removal

Remove or replace video backgrounds with AI.

## Tools

### Runway (Web/API)

**Web UI:**
1. Upload video
2. Select "Green Screen" tool
3. AI auto-mattes subject
4. Export with alpha or replace background

**API:**
```python
import requests

response = requests.post(
    "https://api.dev.runwayml.com/v1/video-to-video",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "gen3a_turbo",
        "video_url": "https://...",
        "mask_type": "subject"
    }
)
```

### Unscreen

```bash
# Web-based tool
# Upload at https://www.unscreen.com/
# Download with transparent background
```

**API:**
```python
response = requests.post(
    "https://api.unscreen.com/v1.0/videos",
    headers={"X-Api-Key": API_KEY},
    files={"video": open("video.mp4", "rb")}
)
```

**Pricing:** ~$5/video minute

### DaVinci Resolve (Magic Mask)

1. Open Fusion page
2. Add "Magic Mask" node
3. Draw strokes on subject
4. AI tracks through video
5. Connect to merge node for composite

### After Effects (Rotobrush 2)

1. Double-click layer to enter Layer panel
2. Select Rotobrush tool
3. Paint over subject in frame 1
4. Propagate forward
5. Refine edges as needed

### FFmpeg + rembg (Local)

```bash
# Extract frames
ffmpeg -i input.mp4 -vf fps=30 frames/%04d.png

# Remove backgrounds (batch)
for f in frames/*.png; do
    rembg i "$f" "output/$f"
done

# Reassemble with alpha
ffmpeg -framerate 30 -i output/%04d.png -c:v prores_ks -profile:v 4444 output.mov
```

## Export Formats

**With Alpha Channel:**
- ProRes 4444 (.mov) — best quality
- WebM VP9 — web compatible
- PNG sequence — maximum flexibility

**Green Screen:**
- Standard H.264
- Neon green (#00FF00) background
- Key in editing software

## Best Practices

- **Good lighting** — even lighting on subject helps AI
- **Contrast** — subject should differ from background
- **Stable camera** — movement adds complexity
- **Clean edges** — hair/fur needs extra attention
- **Preview first** — check problematic frames before full render

## Common Issues

- **Hair fringing** — add edge blur, use matting refinement
- **Flickering edges** — temporal consistency filters
- **Shadows lost** — capture shadow separately if possible
- **Motion blur** — can confuse AI matting
