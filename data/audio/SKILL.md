---
name: Audio
slug: audio
version: 1.0.1
description: Process, enhance, and convert audio files with noise removal, normalization, format conversion, transcription, and podcast workflows.
changelog: Declare required binaries (ffmpeg, ffprobe), add requirements section with optional deps, add explicit scope
metadata: {"clawdbot":{"emoji":"🔊","requires":{"bins":["ffmpeg","ffprobe"]},"os":["linux","darwin","win32"]}}
---

## Requirements

**Required:**
- `ffmpeg` / `ffprobe` — core audio processing

**Optional (for advanced features):**
- `sox` — additional noise reduction
- `whisper` — local transcription (or use API)
- `demucs` — stem separation

## Quick Reference

| Situation | Load |
|-----------|------|
| FFmpeg commands by task | `commands.md` |
| Loudness standards by platform | `loudness.md` |
| Podcast production workflow | `podcast.md` |
| Transcription workflow | `transcription.md` |

## Core Capabilities

| Task | Method |
|------|--------|
| Convert formats | FFmpeg (`-acodec`) |
| Remove noise | FFmpeg filters or SoX |
| Normalize loudness | `ffmpeg-normalize` or `-af loudnorm` |
| Transcribe | Whisper → text, SRT, VTT |
| Separate stems | Demucs (vocals, drums, bass, other) |

## Execution Pattern

1. **Clarify goal** — What format? What loudness? What platform?
2. **Analyze source** — `ffprobe` for codec, sample rate, channels, duration
3. **Process** — FFmpeg/SoX for transformation
4. **Verify** — Check output plays, meets specs, sounds correct
5. **Deliver** — Provide file to user

## Common Requests → Actions

| User says | Agent does |
|-----------|------------|
| "Convert to MP3" | `-acodec libmp3lame -q:a 2` |
| "Remove background noise" | Apply highpass/lowpass or dedicated denoiser |
| "Normalize for podcast" | `-af loudnorm=I=-16:TP=-1.5:LRA=11` |
| "Transcribe this" | Whisper → output SRT/VTT/TXT |
| "Extract audio from video" | `-vn -acodec copy` or re-encode |
| "Make it smaller" | Lower bitrate: `-b:a 128k` or `-b:a 96k` |
| "Speed up 1.5x" | `-af atempo=1.5` |

## Format Quick Reference

| Format | Use Case | Quality |
|--------|----------|---------|
| WAV | Master, editing | Lossless |
| FLAC | Archive, audiophile | Lossless compressed |
| MP3 | Universal sharing | Lossy, 128-320 kbps |
| AAC/M4A | Apple, podcasts | Lossy, efficient |
| OGG/Opus | WhatsApp, Discord | Lossy, very efficient |

## Quality Defaults

- **Podcast:** -16 LUFS (Spotify), -19 LUFS (Apple)
- **Music:** -14 LUFS (Spotify), -16 LUFS (Apple Music)
- **MP3 quality:** VBR `-q:a 2` (~190 kbps) or CBR `-b:a 192k`
- **Sample rate:** 44.1kHz for music, 48kHz for video sync

## Scope

This skill:
- Processes audio files user explicitly provides
- Runs FFmpeg commands on user request
- Does NOT access cloud services without user knowing
- Does NOT store files persistently (user manages their files)
