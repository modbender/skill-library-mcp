---
name: Video Editing
description: Edit videos with AI background removal, color grading, upscaling, stabilization, and enhancement tools.
metadata: {"clawdbot":{"emoji":"🎞️","os":["linux","darwin","win32"]}}
---

# AI Video Editing

Help users edit and enhance videos with AI tools.

**Rules:**
- Ask what edit they need: remove background, color grade, upscale, stabilize, enhance
- Check technique files: `background-removal.md`, `color-grading.md`, `upscaling.md`, `stabilization.md`, `audio.md`, `effects.md`
- Check `tools.md` for provider-specific setup
- Always work on copies, preserve originals

---

## Edit Type Selection

| Task | Technique | Best Tools |
|------|-----------|------------|
| Remove background | Video matting | Runway, Unscreen, rotobrush |
| Color correction | LUTs, grading | DaVinci Resolve, Runway |
| Increase resolution | Video upscaling | Topaz Video AI, Real-ESRGAN |
| Fix shaky footage | Stabilization | DaVinci, Premiere, ffmpeg |
| Clean up audio | Enhancement | Adobe Podcast, Descript |
| Add effects | AI effects | Runway, After Effects |
| Slow motion | Frame interpolation | RIFE, Topaz |

---

## Workflow Principles

- **Proxy workflow** — edit low-res, export high-res
- **Non-destructive** — preserve original files
- **Render in stages** — color before effects before upscale
- **Check key frames** — AI can flicker between cuts
- **Audio separately** — enhance audio track independently

---

## Common Workflows

### Background Replacement
1. Export with alpha (green screen or AI matte)
2. Place over new background
3. Match lighting/color
4. Add edge blur for realism
5. Composite shadows

### Enhancement Pipeline
1. Stabilize (if needed)
2. Color correct / grade
3. Denoise
4. Upscale to final resolution
5. Sharpen (light)

### Audio Cleanup
1. Remove background noise
2. Enhance voice clarity
3. Normalize levels
4. Add compression if needed

---

## Frame Rates

| Source | Interpolation | Output |
|--------|---------------|--------|
| 24fps | 2x | 48fps |
| 30fps | 2x | 60fps |
| 30fps | 4x | 120fps |
| 60fps | 2x | 120fps |

**Use cases:**
- Slow motion (need more frames)
- Gaming footage (smooth motion)
- Film to video conversion

---

## Export Settings

**YouTube/General:**
- H.264 codec
- 1080p or 4K
- 15-30 Mbps bitrate

**Archive/Master:**
- ProRes or DNxHD
- Original resolution
- Maximum quality

**Social Media:**
- Platform presets
- 9:16 for vertical
- Under file size limits

---

### Current Setup
<!-- Tool: status -->

### Projects
<!-- What they're editing -->

### Preferences
<!-- Preferred tools, codecs, settings -->

---
*Check technique files for detailed workflows.*
