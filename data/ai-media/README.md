# ai-media - Quick Start

AI media generation skill for OpenClaw/EvoClaw agents.

## Installation

```bash
# Clone/copy to your skills directory
cp -r skills/ai-media ~/.openclaw/skills/

# Or for EvoClaw
cp -r skills/ai-media ~/.evoclaw-hub/skills/
```

## Quick Examples

### Generate an Image
```bash
cd ~/.openclaw/skills/ai-media
./scripts/image.sh "lady on beach at sunset" realistic
```

### Generate a Video
```bash
./scripts/video.sh "waves crashing on shore" animatediff 4
```

### Create Talking Head
```bash
./scripts/talking-head.sh "Hello world!" gentle
```

### Generate Voice Audio
```bash
./scripts/audio.sh "This is a test" en male
```

## Status

✅ **Talking heads** — SadTalker fully working  
⏳ **Video (AnimateDiff)** — Working, automation pending  
⏳ **Video (LTX-2)** — Models ready, workflow integration pending  
⏳ **Image** — Models downloading (z-image 43%, Juggernaut ready)  
⏳ **Audio** — Using gTTS, Voxtral integration pending  

## GPU Server

All generation happens on GPU server `peter@10.0.0.44`:
- **RTX 3090** (primary)
- **RTX 3080** (secondary)  
- **RTX 2070 Super** (tertiary)

SSH key required: `~/.ssh/id_ed25519_alexchen`

## Next Steps

1. ✅ Complete z-image download (9/21 files, ~57% remaining)
2. ✅ Set up LTX-2 ComfyUI workflow
3. Implement ComfyUI API automation (HTTP calls instead of manual)
4. Integrate Voxtral for higher quality TTS
5. Add batch generation support
6. Publish to ClawHub

---

**Maintainer:** Alex Chen  
**Version:** 1.0.0  
**GPU Server:** peter@10.0.0.44
