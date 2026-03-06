# Video Editing Tools

Provider setup and software reference.

## Free Software

### DaVinci Resolve

**The free professional standard:**
- Full color grading suite
- Fusion for compositing
- Fairlight for audio
- Cut page for fast editing

Download: https://www.blackmagicdesign.com/products/davinciresolve

### FFmpeg

```bash
# Install
brew install ffmpeg  # macOS
apt install ffmpeg   # Ubuntu
```

**Essential commands:**
```bash
# Convert format
ffmpeg -i input.mov -c:v libx264 -crf 20 output.mp4

# Trim video
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 -c copy output.mp4

# Extract audio
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# Merge audio + video
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
```

### Kdenlive

Open-source NLE:
- Multi-track editing
- Effects and transitions
- Keyframe animation

### OpenShot

Simple, beginner-friendly:
- Drag-and-drop editing
- Basic effects
- Cross-platform

## Commercial Software

### Adobe Premiere Pro

- Industry standard
- Creative Cloud integration
- $22/month

### Final Cut Pro

- Mac only
- Fast, optimized
- $299 one-time

### Topaz Video AI

- Best upscaling
- Frame interpolation
- Stabilization
- $299 one-time

## Cloud/API Services

### Runway

```python
import requests

# Example: Remove background
response = requests.post(
    "https://api.dev.runwayml.com/v1/green-screen",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"video_url": "https://..."}
)
```

**Features:**
- Green screen
- Color grade
- Style transfer
- Gen-3 video

### Descript

- Transcription-based editing
- "Edit like a doc"
- Voice cloning
- Screen recording

### Kapwing

- Web-based editor
- AI features
- Team collaboration
- Free tier available

## AI Tools by Task

| Task | Best Free | Best Paid |
|------|-----------|-----------|
| Edit | DaVinci Resolve | Premiere Pro |
| Upscale | Video2X | Topaz Video AI |
| Stabilize | FFmpeg vidstab | Premiere/DaVinci |
| Denoise | DaVinci | Topaz |
| Slow-mo | RIFE | Topaz Chronos |
| Audio | Audacity | Adobe Podcast |
| Captions | YouTube auto | Descript |

## Hardware Requirements

**Minimum:**
- CPU: 6+ cores
- RAM: 16GB
- GPU: 4GB VRAM
- Storage: SSD

**Recommended:**
- CPU: 8+ cores
- RAM: 32GB+
- GPU: 8GB+ VRAM (NVIDIA for AI)
- Storage: NVMe SSD

## Workflow Integration

**Project-based:**
```
project/
├── source/        # Original footage
├── proxy/         # Low-res for editing
├── exports/       # Final renders
├── audio/         # Music, SFX
└── project.drp    # Project file
```

**Proxy workflow:**
1. Create low-res proxies
2. Edit with proxies
3. Relink to originals
4. Export full resolution
