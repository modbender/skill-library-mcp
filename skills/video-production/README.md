# Video Production Skill

Multi-platform cinematic video generation with modular assembly for professional post-production.

## Quick Start

**For a new video project:**
1. Write storyboard using `references/storyboard-template.md`
2. Choose platform: Veo 3 (video) / DALL-E (images) / Stable Diffusion (budget)
3. Generate frames/videos
4. Record voice-over (VO must be final)
5. Create `timing.json` from `assets/timing_template.json`
6. Run assembly script
7. Export raw to Premiere Pro
8. Color grade + VFX

## Folder Structure

```
├── SKILL.md                           ← Start here
├── README.md                          ← This file
├── references/
│   ├── storyboard-template.md         ← Scene planning template
│   ├── platform-guide-veo3.md         ← Veo 3 detailed setup
│   ├── platform-guide-dalle.md        ← DALL-E guide [TODO]
│   ├── platform-guide-stable-diffusion.md ← SD guide [TODO]
│   ├── timing-sync.md                 ← Audio synchronization
│   ├── premiere-export.md             ← Pro export settings
│   ├── assembly-patterns.md           ← Ken Burns, composition [TODO]
│   └── video-production-framework.md  ← Complete philosophy [TODO]
├── scripts/
│   ├── veo3_generator.py              ← Google Veo 3 batch generation
│   ├── dalle_generator.py             ← OpenAI DALL-E batch [TODO]
│   ├── sd_generator.py                ← Stable Diffusion batch [TODO]
│   ├── ffmpeg_assembler.py            ← Static frame assembly [TODO]
│   └── video_compositor.py            ← Video clip stitching [TODO]
└── assets/
    └── timing_template.json           ← Copy for new projects
```

## When to Use This Skill

✅ **Use when:**
- Creating video narratives from storyboards
- Generating cinematic frames/videos from AI
- Assembling frames with voice-over + music
- Comparing outputs across multiple platforms
- Exporting raw video for Premiere Pro professional editing

❌ **Don't use when:**
- Simple image generation (use image tool directly)
- Quick video editing (use Premiere Pro directly)
- Social media clips (use TikTok/Instagram native tools)

## Core Workflow

```
Write Storyboard
       ↓
Generate Frames/Videos (Platform A/B/C)
       ↓
Record Voice-Over (VO drives timing)
       ↓
Create timing.json (Frame durations + sync)
       ↓
Run Assembly (ffmpeg/video_compositor)
       ↓
Export Raw (ProRes for Premiere Pro)
       ↓
Color Grade + VFX (Premiere Pro)
       ↓
Export Final Deliverable
```

## API Keys & Setup

### Veo 3 (Google)
```bash
export GOOGLE_API_KEY="AIza..."
# Get key at: https://console.cloud.google.com/apis/credentials
# Requires: Billing enabled, Generative AI API activated
```

### DALL-E (OpenAI)
```bash
export OPENAI_API_KEY="sk-..."
# Get key at: https://platform.openai.com/api/keys
```

### Stable Diffusion (Local)
```bash
# Install: https://github.com/comfyanonymous/ComfyUI
# Run: python main.py (opens http://localhost:8188)
```

## Platform Comparison

| Platform | Output | Speed | Cost | Best For |
|----------|--------|-------|------|----------|
| Veo 3 | MP4 video | 2-10 min | $0.05 (6s) | Full cinematic videos |
| DALL-E | PNG images | 30-60 sec | $0.08 | Character consistency |
| SD (local) | PNG images | 2-5 min | Free (GPU) | Budget projects |

## Examples

### Example 1: Muffin Video (Veo 3)
- 12 scenes, 47 seconds total
- Platform: Veo 3 (generate videos)
- VO: 5 segments, each drives frame duration
- Music: Ambient track underneath
- Output: ProRes raw for Premiere Pro
- See: `SKILL.md` quick examples

### Example 2: Real Estate Tour (DALL-E + Ken Burns)
- 6 property shots, 30 seconds total
- Platform: DALL-E (generate consistent property images)
- VO: Narration describing each room
- Music: Upbeat real estate background music
- Output: Vertical video (9:16) for Instagram
- Assembly: ffmpeg with Ken Burns zoom effect

### Example 3: Multi-Platform Comparison
- Same 8-scene storyboard
- Generate on Veo 3 (videos)
- Generate on DALL-E (images)
- Generate on SD (images)
- Assemble all 3
- Review side-by-side
- Pick best for final edit

## Tools & Dependencies

### Required
- Python 3.9+
- ffmpeg (for assembly)

### Optional
- `google-genai` (for Veo 3)
- `openai` (for DALL-E)
- `pydub` (for audio timing)

## Next Steps

1. Read `SKILL.md` for workflow overview
2. Choose a reference guide based on your use case:
   - Storyboarding: `references/storyboard-template.md`
   - Veo 3: `references/platform-guide-veo3.md`
   - Audio: `references/timing-sync.md`
   - Premiere export: `references/premiere-export.md`
3. Copy `assets/timing_template.json` for your project
4. Run generator script (veo3/dalle/sd)
5. Run assembly script (ffmpeg_assembler or video_compositor)
6. Export raw and import to Premiere Pro

---

**Last updated:** 2026-02-21
**Status:** Core skill complete; scripts [TODO: dalle_generator, sd_generator, ffmpeg_assembler, video_compositor]
