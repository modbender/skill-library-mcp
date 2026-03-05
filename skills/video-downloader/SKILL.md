---
name: Video Downloader
slug: video-downloader
version: 1.0.0
homepage: https://clawic.com/skills/video-downloader
description: Download online videos with quality and format controls using yt-dlp for reliable local saves.
changelog: Initial release with local yt-dlp wrapper, quality controls, and explicit security boundaries.
metadata: {"clawdbot":{"emoji":"⬇️","requires":{"bins":["yt-dlp","python3"]},"install":[{"id":"brew","kind":"brew","formula":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (Homebrew)"}],"os":["linux","darwin"]}}
---

# Video Downloader

Download single videos from user-provided URLs with predictable quality, format, and output paths.

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

Use this skill when the user asks to download a video or extract audio from a video URL.
It is optimized for one-off downloads with explicit quality and format requirements.

## Architecture

Memory lives in `~/video-downloader/`. See `memory-template.md` for structure.

```text
~/video-downloader/
├── memory.md             # Status + user preferences
├── downloads-log.md      # Optional history of completed downloads
└── failed-downloads.md   # Optional retries and failure reasons
```

## Quick Reference

Load only what you need to keep context small during execution.

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Command recipes | `commands.md` |
| Download script | `download_video.py` |

## Core Rules

### 1. Confirm Rights and Target First
- Ask for the exact URL and intended use when unclear.
- If the request implies unauthorized copying, refuse and suggest legal alternatives.

### 2. Inspect Metadata Before Downloading
- Run metadata check first to confirm title, duration, and available formats.
- If metadata fetch fails, stop and report the exact error instead of retrying blindly.

### 3. Match Quality to User Intent
- Use `best` when user says "highest quality".
- Use capped quality (`1080p`, `720p`, etc.) for smaller files or device limits.
- Use audio-only mode only when they explicitly want audio extraction.

### 4. Use Deterministic Output Names
- Save files as `%(title)s [%(id)s].%(ext)s` to reduce collisions.
- Keep downloads in a user-approved directory and never write outside it.

### 5. Prefer the Local Wrapper Script
- Use `python3 download_video.py "<url>" ...` for consistent behavior.
- Fall back to raw `yt-dlp` commands only if the user asks for custom flags not covered by the script.

### 6. Verify Output Before Declaring Success
- Confirm file exists, extension matches request, and size is non-zero.
- For audio-only downloads, confirm output is `.mp3`.

## Common Traps

- Downloading playlists accidentally -> use `--no-playlist` by default.
- Choosing `best` for limited storage -> oversized files and slow transfers.
- Re-trying blocked URLs repeatedly -> temporary ban risk and no progress.
- Saving with title only -> filename collisions across similar uploads.
- Skipping metadata check -> wrong media downloaded from redirected links.

## External Endpoints

The downloader only contacts domains implied by the user-provided URL.

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| User-provided video host URL domains (via `yt-dlp`) | Requested media URL and standard downloader headers | Fetch metadata and media streams |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Only the target media URL and standard downloader request headers sent by `yt-dlp`.

**Data that stays local:**
- Downloaded files in the selected output folder.
- Optional memory notes under `~/video-downloader/`.

**This skill does NOT:**
- Store credentials in plain text.
- Access files outside user-approved output paths.
- Download playlists unless the user explicitly asks.
- Make undeclared network requests outside the target media host.

## Trust

By using this skill, requests are sent to the video host domains behind the provided URL.
Only install if you trust those services with your request metadata.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `video` — video processing workflows
- `ffmpeg` — codec conversion tasks
- `audio` — audio cleanup workflows
- `youtube-video-transcript` — transcript extraction

## Feedback

- If useful: `clawhub star video-downloader`
- Stay updated: `clawhub sync`
