---
name: spaces-listener
description: Record, transcribe, and summarize X/Twitter Spaces — live or replays. Auto-downloads audio via yt-dlp, transcribes with Whisper, and generates AI summaries.
version: 1.6.0
author: jamesalmeida
tags: [twitter, x, spaces, transcription, summarization, audio, recording]
when: "User asks to record, transcribe, or listen to an X/Twitter Space"
examples:
  - "Record this Space"
  - "Transcribe this X Space"
  - "Listen to this Twitter Space and transcribe it"
  - "Download this Space audio"
metadata:
  openclaw:
    requires:
      bins: ["yt-dlp", "ffmpeg"]
    emoji: "🎧"
---

# spaces-listener

Record, transcribe, and summarize X/Twitter Spaces — live or replays. Supports multiple concurrent recordings.

## Commands

```bash
# Start recording (runs in background)
spaces listen <url>

# Record multiple Spaces at once
spaces listen "https://x.com/i/spaces/1ABC..."
spaces listen "https://x.com/i/spaces/2DEF..."

# List all active recordings
spaces list

# Check specific recording status
spaces status 1

# Stop a recording
spaces stop 1
spaces stop all

# Clean stale pid/meta files
spaces clean

# Transcribe when done
spaces transcribe ~/Desktop/space.m4a --model medium

# Summarize an existing transcript
spaces summarize ~/Desktop/space_transcript.txt

# Skip summarization
spaces transcribe ~/Desktop/space.m4a --no-summarize
```

## Requirements

```bash
brew install yt-dlp ffmpeg openai-whisper
```

For summaries, set `OPENAI_API_KEY` (transcription still works without it).

## How It Works

1. Each `spaces listen` starts a new background recording with a unique ID
2. Recordings persist even if you close terminal
3. Run `spaces list` to see all active recordings
4. When done, `spaces stop <id>` or `spaces stop all`
5. Transcribe with `spaces transcribe <file>`
6. Summaries are generated automatically after transcription (skip with `--no-summarize`)

## Output

Each space gets its own folder under `~/Dropbox/ClawdBox/XSpaces/`:
```
~/Dropbox/ClawdBox/XSpaces/
  space_username_2026-02-03_1430/
    recording.m4a     — audio
    recording.log     — progress log
    transcript.txt    — transcript
    summary.txt       — summary
```

## Critical: Agent Usage Rules

**NEVER set a timeout on Space downloads.** Spaces can be hours long.
yt-dlp stops automatically when the Space ends — don't kill it early.

The correct workflow:
1. Run `spaces listen <url>` — it starts a background process and returns immediately
2. Set a **cron job** (every 5–10 min) to check `spaces list`
3. When recording shows "No active recordings", it's done
4. Transcribe the audio file, summarize, notify the user
5. Delete the cron job

**Do NOT:**
- Use `exec` with a timeout for downloads
- Run competing download processes for the same Space
- Kill the download process manually (unless the user asks)

Audio is staged in `/tmp/spaces-listener-staging/` during recording, then
automatically copied to the final Dropbox output dir when complete. This
avoids Dropbox file-locking issues during long downloads.

## Whisper Models

| Model | Speed | Accuracy |
|-------|-------|----------|
| tiny | ⚡⚡⚡⚡ | ⭐ |
| base | ⚡⚡⚡ | ⭐⭐ |
| small | ⚡⚡ | ⭐⭐⭐ |
| medium | ⚡ | ⭐⭐⭐⭐ |
| large | 🐢 | ⭐⭐⭐⭐⭐ |
