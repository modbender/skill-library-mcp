---
name: Video
slug: video
version: 1.0.1
description: Process, edit, and optimize videos for any platform with compression, format conversion, captioning, and repurposing workflows.
changelog: Declare required binaries (ffmpeg, ffprobe), add requirements section with optional deps, add explicit scope
metadata: {"clawdbot":{"emoji":"🎬","requires":{"bins":["ffmpeg","ffprobe"]},"os":["linux","darwin","win32"]}}
---

## Requirements

**Required:**
- `ffmpeg` / `ffprobe` — core video processing

**Optional:**
- `whisper` — local transcription for captions
- `realesrgan` — AI upscaling

## Quick Reference

| Situation | Load |
|-----------|------|
| Platform specs (YouTube, TikTok, Instagram) | `platforms.md` |
| FFmpeg commands by task | `commands.md` |
| Quality/compression settings | `quality.md` |
| Workflow by use case | `workflows.md` |

## Core Capabilities

| Task | Method |
|------|--------|
| Convert/compress | FFmpeg (see `commands.md`) |
| Generate captions | Whisper → SRT/VTT |
| Change aspect ratio | Crop, pad, or smart reframe |
| Clean audio | Normalize, denoise, enhance |
| Batch operations | Process entire folders in one run |

## Execution Pattern

1. **Clarify target** — What platform? What format? File size limit?
2. **Check source** — `ffprobe` for codec, resolution, duration, audio
3. **Process** — FFmpeg for transformation
4. **Verify** — Confirm output meets specs before delivering
5. **Deliver** — Provide file to user

## Common Requests → Actions

| User says | Agent does |
|-----------|------------|
| "Make this work for TikTok" | Reframe to 9:16, check duration ≤3min, compress |
| "Add subtitles" | Whisper → SRT → burn-in or deliver separately |
| "Compress for WhatsApp" | Target <64MB, H.264, AAC |
| "Extract audio" | `-vn -acodec mp3` or `-acodec copy` |
| "Make a GIF" | Extract frames, optimize palette, loop |
| "Split into clips" | Cut at timestamps with `-ss` and `-t` |

## Quality Rules

- **Always re-encode audio to AAC** for maximum compatibility
- **Use `-movflags +faststart`** for web playback
- **CRF 23** is good default for H.264 (lower = better, bigger)
- **Check before delivering** — verify duration, file size, playability

## Platform Quick Reference

| Platform | Aspect | Max Duration | Max Size |
|----------|--------|--------------|----------|
| TikTok | 9:16 | 3 min | 287MB |
| Instagram Reels | 9:16 | 90s | 250MB |
| YouTube Shorts | 9:16 | 60s | No limit |
| YouTube | 16:9 | 12h | 256GB |
| WhatsApp | Any | 3 min | 64MB |

## Scope

This skill:
- Processes video files user explicitly provides
- Runs FFmpeg commands on user request
- Does NOT access files without user instruction
- Does NOT upload to external services automatically
