---
name: ugc-manual
description: |
  Generate lip-sync video from image + user's own audio recording.
  
  ✅ USE WHEN:
  - User provides their OWN audio file (voice recording)
  - Want to sync image to specific audio/voice
  - User recorded the script themselves
  - Need exact audio timing preserved
  
  ❌ DON'T USE WHEN:
  - User provides text script (not audio) → use veed-ugc
  - Need AI to generate the voice → use veed-ugc
  - Don't have audio file yet → use veed-ugc with script
  
  INPUT: Image + audio file (user's recording)
  OUTPUT: MP4 video with lip-sync to provided audio
  
  KEY DIFFERENCE: veed-ugc = script → AI voice → video
                  ugc-manual = user audio → video (no voice generation)
---

# UGC-Manual

Generate lip-sync videos by combining an image with a custom audio file using ComfyDeploy's UGC-MANUAL workflow.

## Overview

UGC-Manual takes:
1. An image (person/character with visible face)
2. An audio file (user's voice recording)

And produces a video where the person in the image lip-syncs to the audio.

## API Details

**Endpoint:** `https://api.comfydeploy.com/api/run/deployment/queue`
**Deployment ID:** `075ce7d3-81a6-4e3e-ab0e-7a25edf601b5`

## Required Inputs

| Input | Description | Formats |
|-------|-------------|---------|
| `image` | Image with a visible face | JPG, PNG |
| `input_audio` | Audio file to lip-sync | MP3, WAV, OGG |

## Usage

```bash
uv run ~/.clawdbot/skills/ugc-manual/scripts/generate.py \
  --image "path/to/image.jpg" \
  --audio "path/to/audio.mp3" \
  --output "output-video.mp4"
```

### With URLs:
```bash
uv run ~/.clawdbot/skills/ugc-manual/scripts/generate.py \
  --image "https://example.com/image.jpg" \
  --audio "https://example.com/audio.mp3" \
  --output "result.mp4"
```

## Workflow Integration

### Typical Use Cases

1. **Custom voice recordings** - User records their own audio via Telegram/WhatsApp
2. **Pre-generated TTS** - Audio generated externally (ElevenLabs, etc.)
3. **Music/sound sync** - Sync mouth movements to any audio

### Example Pipeline

```bash
# 1. Convert Telegram voice message to MP3 (if needed)
ffmpeg -i voice.ogg -acodec libmp3lame -q:a 2 voice.mp3

# 2. Generate lip-sync video
uv run ugc-manual... --image face.jpg --audio voice.mp3 --output video.mp4
```

## Difference from VEED-UGC

| Feature | UGC-Manual | VEED-UGC |
|---------|------------|----------|
| Audio source | User provides | Generated from brief |
| Script | N/A | Auto-generated |
| Voice | User's recording | ElevenLabs TTS |
| Use case | Custom audio | Automated content |

## Notes

- Image should have a clearly visible face (frontal or 3/4 view)
- Audio quality affects output quality
- Processing time: ~2-5 minutes depending on audio length
- **Audio auto-conversion**: The script automatically converts any audio format (MP3, OGG, M4A, etc.) to WAV PCM 16-bit mono 48kHz before sending to FabricLipsync
- Requires `ffmpeg` installed on the system
