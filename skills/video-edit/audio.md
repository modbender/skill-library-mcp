# Video Audio Enhancement

Clean up and enhance video audio with AI.

## Tools

### Adobe Podcast (Free Web)

```
https://podcast.adobe.com/enhance
```

- Upload audio/video
- AI removes noise, enhances voice
- Free, excellent quality
- Max 1 hour per file

### Descript

```python
# Web-based with API
# Features:
# - Studio Sound (enhance)
# - Remove filler words
# - Transcription
```

### FFmpeg Audio Filters

```bash
# Remove background noise (basic)
ffmpeg -i input.mp4 -af "highpass=f=200,lowpass=f=3000,afftdn=nf=-25" output.mp4

# Normalize audio levels
ffmpeg -i input.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp4

# Compressor (even out levels)
ffmpeg -i input.mp4 -af "acompressor=threshold=-20dB:ratio=4:attack=5:release=50" output.mp4

# De-esser
ffmpeg -i input.mp4 -af "deesser=i=0.5:m=0.5:f=5500:s=o" output.mp4
```

### Audacity

1. Import audio
2. Effect > Noise Reduction
   - Get noise profile from silent section
   - Apply to full track
3. Effect > Compressor
4. Effect > Normalize
5. Export

### DaVinci Resolve (Fairlight)

1. Switch to Fairlight page
2. Select clip
3. Use built-in plugins:
   - Noise Reduction
   - De-Esser
   - Compressor
   - EQ

### AI Voice Enhancers

**Krisp:**
- Real-time noise cancellation
- Voice isolation
- Background voice removal

**NVIDIA Broadcast:**
- Free for NVIDIA GPU
- Noise removal
- Room echo removal

## Common Tasks

### Remove Background Noise

```bash
# FFmpeg
ffmpeg -i input.mp4 -af "afftdn=nf=-20" output.mp4

# Options:
# nf = noise floor (dB), lower = more aggressive
# nr = noise reduction amount
```

### Normalize Volume

```bash
# EBU R128 standard (streaming)
ffmpeg -i input.mp4 -af "loudnorm=I=-14:TP=-1:LRA=11" output.mp4

# Peak normalization
ffmpeg -i input.mp4 -af "volume=0dB" -c:v copy output.mp4
```

### Voice Isolation

```bash
# Using demucs (separate vocals)
pip install demucs
demucs --two-stems=vocals input.mp4
```

### Add Background Music

```bash
# Mix audio tracks
ffmpeg -i video.mp4 -i music.mp3 \
  -filter_complex "[1:a]volume=0.3[music];[0:a][music]amix=inputs=2:duration=first" \
  -c:v copy output.mp4
```

## Audio Repair Pipeline

1. **Remove noise** — AI or spectral denoise
2. **EQ** — cut mud (200-400Hz), add clarity (2-4kHz)
3. **Compress** — even out dynamics
4. **De-ess** — reduce sibilance if needed
5. **Normalize** — to target loudness

## Export Specs

| Platform | Loudness | Format |
|----------|----------|--------|
| YouTube | -14 LUFS | AAC 320kbps |
| Podcast | -16 LUFS | MP3 128kbps |
| Broadcast | -24 LUFS | PCM |
| Streaming | -14 LUFS | AAC 256kbps |

## Best Practices

- **Record clean** — easier than fixing
- **Room treatment** — reduces echo
- **Good mic** — garbage in, garbage out
- **Check on headphones** — and speakers
- **Leave headroom** — don't clip
