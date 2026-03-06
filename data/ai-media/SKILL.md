---
name: ai-media - AI Media Generation
description: Full-stack AI media generation powered by GPU server (RTX 3090/3080/2070S).
---

# ai-media - AI Media Generation

Full-stack AI media generation powered by GPU server (RTX 3090/3080/2070S).

## Capabilities

1. **Image Generation** — Photorealistic images via ComfyUI (z-image, Juggernaut XL)
2. **Video Generation** — Video synthesis via ComfyUI (AnimateDiff, LTX-2)
3. **Talking Heads** — Animated talking faces via SadTalker
4. **Voice Synthesis** — Natural TTS via Voxtral (whisper.cpp)

## GPU Server

- **Host:** `${GPU_USER}@${GPU_HOST}`
- **SSH Key:** `~/.ssh/id_ed25519_gpu`
- **ComfyUI:** `/data/ai-stack/comfyui/ComfyUI/` (port 8188)
- **SadTalker:** `/data/ai-stack/sadtalker/`
- **Voxtral:** `/data/ai-stack/whisper/`
- **Output:** `/data/ai-stack/output/`

## Usage

### Generate Image

```bash
./scripts/image.sh "lady on beach at sunset" realistic
./scripts/image.sh "cyberpunk cityscape" artistic
```

**Arguments:**
- `$1`: Prompt text
- `$2`: Style (realistic|artistic) — optional, default: realistic

**Output:** Path to generated image (e.g., `/data/ai-stack/output/image_001.png`)

### Generate Video

```bash
./scripts/video.sh "waves crashing on shore" animatediff 4
./scripts/video.sh "city traffic timelapse" ltx2 8
```

**Arguments:**
- `$1`: Prompt text
- `$2`: Model (animatediff|ltx2) — optional, default: animatediff
- `$3`: Duration in seconds — optional, default: 4

**Output:** Path to generated video (e.g., `/data/ai-stack/output/video_001.mp4`)

### Generate Talking Head

```bash
./scripts/talking-head.sh "Hello, I'm Agent" gentle input.jpg
./scripts/talking-head.sh "Welcome to the future" neutral photo.png
```

**Arguments:**
- `$1`: Speech text
- `$2`: Voice style (gentle|neutral|energetic) — optional, default: gentle
- `$3`: Avatar image path — optional, generates default if not provided

**Output:** Path to talking head video (e.g., `/data/ai-stack/output/talking_001.mp4`)

### Generate Audio

```bash
./scripts/audio.sh "This is a test message" en male
./scripts/audio.sh "Bonjour le monde" fr female
```

**Arguments:**
- `$1`: Text to speak
- `$2`: Language code (en|fr|es|etc) — optional, default: en
- `$3`: Voice gender (male|female) — optional, default: male

**Output:** Path to audio file (e.g., `/data/ai-stack/output/audio_001.wav`)

## Models Available

### Image Models
- **z-image** — 6B params, S3-DiT, photorealistic (downloading, 43% complete)
- **Juggernaut XL v9** — SDXL-based, versatile (7.1GB, ready)

### Video Models
- **AnimateDiff** — SD 1.5 motion module (512x512, working ✅)
- **LTX-2** — 19B params, high quality (14GB checkpoint ready, Gemma encoder ready)

### Talking Head Models
- **SadTalker** — Audio-driven head animation (working ✅)

### Voice Models
- **Voxtral** — whisper.cpp-based TTS (installed)

## Dependencies

All dependencies are pre-installed on GPU server:
- ComfyUI with custom nodes (AnimateDiff-Evolved, VideoHelperSuite)
- SadTalker with face enhancer
- Voxtral with whisper.cpp
- FFmpeg for video encoding

## Error Handling

Scripts will:
- Check SSH connectivity before execution
- Validate GPU server is running
- Return meaningful error messages
- Clean up failed generations automatically

## Performance

- **Image:** ~10-20s for 1024x1024
- **Video (AnimateDiff):** ~20-30s for 512x512, 16 frames
- **Video (LTX-2):** ~60-90s for 768x512, 4s @ 24fps
- **Talking Head:** ~30-40s for 10s video
- **Audio:** ~2-5s for 30s speech

## Future Enhancements

- [ ] Batch generation support
- [ ] Style transfer capabilities
- [ ] Video upscaling (spatial + temporal)
- [ ] Multi-language voice cloning
- [ ] Real-time preview streaming

---

**Status:** Active development
**Maintainer:** Agent
**GPU Server:** ${GPU_USER}@${GPU_HOST}
