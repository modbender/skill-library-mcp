# Video Color Grading

Color correct and grade video with AI assistance.

## Concepts

**Color Correction:** Fix technical issues
- White balance
- Exposure
- Contrast normalization

**Color Grading:** Creative look
- Mood/atmosphere
- Style consistency
- Cinematic looks

## Tools

### DaVinci Resolve (Free)

**Color Correction:**
1. Switch to Color page
2. Use Color Wheels for lift/gamma/gain
3. Adjust curves for precise control
4. Use qualifier for selective correction

**AI Features:**
- Magic Mask — AI-based selection
- Face refinement — auto skin tone
- Shot matching — match clips automatically

**LUT Application:**
```
Right-click clip > Apply LUT > Select .cube file
```

### Runway Color Grade

```python
import requests

response = requests.post(
    "https://api.dev.runwayml.com/v1/color-grade",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "video_url": "https://...",
        "style": "cinematic",
        "intensity": 0.7
    }
)
```

### FFmpeg Color Filters

```bash
# Apply LUT
ffmpeg -i input.mp4 -vf "lut3d=cinematic.cube" output.mp4

# Basic color correction
ffmpeg -i input.mp4 -vf "eq=brightness=0.1:contrast=1.2:saturation=1.1" output.mp4

# Color curves
ffmpeg -i input.mp4 -vf "curves=preset=lighter" output.mp4
```

### Premiere Pro + Lumetri

1. Apply Lumetri Color effect
2. Basic Correction for technical fixes
3. Creative panel for looks
4. HSL Secondary for selective color
5. Vignette for cinematic feel

## LUTs (Look-Up Tables)

**Popular Free LUTs:**
- FilmConvert — film emulation
- OSIRIS — cinematic looks
- Lutify.me — various styles

**Applying LUTs:**
```bash
# FFmpeg
ffmpeg -i input.mp4 -vf "lut3d=look.cube" output.mp4
```

**Creating Custom LUTs:**
1. Grade reference frame in DaVinci/Photoshop
2. Export as .cube file
3. Apply to full video

## Scene-to-Scene Matching

**DaVinci Resolve:**
1. Grade hero shot first
2. Right-click other clips
3. "Shot Match to This Clip"
4. Fine-tune manually

**Manual Matching:**
1. Use waveform/vectorscope
2. Match blacks, whites, mids
3. Adjust saturation last

## Common Looks

| Look | Characteristics |
|------|-----------------|
| Cinematic | Teal shadows, orange highlights |
| Vintage | Lifted blacks, faded, warm |
| Horror | Desaturated, blue-green, high contrast |
| Summer | Warm, high saturation, bright |
| Nordic | Cool, desaturated, low contrast |

## Best Practices

- **Start neutral** — correct before grading
- **Use scopes** — waveform, vectorscope, histogram
- **Consistency** — match across scenes
- **Skin tones** — protect during grading
- **Don't over-process** — subtle usually wins
