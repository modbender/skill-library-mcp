---
name: YouTube Video Transcript
slug: youtube-video-transcript
version: 1.0.0
homepage: https://clawic.com/skills/youtube-video-transcript
description: Fetch, summarize, and save YouTube transcripts with timestamp navigation, chapter detection, and searchable content.
changelog: Initial release with transcript extraction, timestamp navigation, chapter detection, and multi-format export.
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["yt-dlp"]},"install":[{"id":"brew","kind":"brew","formula":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (Homebrew)"},{"id":"pip","kind":"pip","package":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (pip)"}],"os":["linux","darwin","win32"]}}
---

Most YouTube transcript tools either require paid APIs, use suspicious proxies, or just dump raw text without structure. This skill extracts transcripts locally using yt-dlp, preserves timestamps for navigation, detects chapters automatically, and exports to any format you need.

## When to Use

User shares a YouTube link and wants to read instead of watch. User asks what someone says about a topic at a specific moment. User needs to extract quotes with timestamps for research or content creation. User wants to summarize a video or search within its content.

## How It Works

```
         ┌──────────────────────────────────────────────┐
         │           YOUTUBE TRANSCRIPT FLOW            │
         └──────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
    ┌─────────┐         ┌──────────┐         ┌─────────┐
    │  VIDEO  │         │ METADATA │         │SUBTITLES│
    │   URL   │         │  FETCH   │         │  CHECK  │
    └────┬────┘         └────┬─────┘         └────┬────┘
         │                   │                    │
         │  youtube.com/     │  Title, duration,  │  Manual first,
         │  watch?v=...      │  chapters, lang    │  auto fallback
         │                   │                    │
         └───────────────────┴────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ EXTRACT + CLEAN │
                    │ VTT → Markdown  │
                    │ with timestamps │
                    └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌───────────┐   ┌──────────┐
        │ CHAPTERS │   │  SEARCH   │   │  EXPORT  │
        │ detected │   │ by topic  │   │ MD/SRT/  │
        │ or smart │   │ timestamp │   │ TXT/JSON │
        └──────────┘   └───────────┘   └──────────┘
```

## The Extraction Process

### 1. 📋 Get Metadata First

Always fetch video info before extracting subtitles:

```bash
yt-dlp -j "VIDEO_URL"
```

This gives you title, duration, official chapters, and available languages. Use it to confirm the right video and check what subtitles exist.

### 2. 📝 Prefer Manual Subtitles

Manual (uploaded) subtitles are higher quality than auto-generated:

```bash
# Try manual first
yt-dlp --write-sub --sub-lang en --skip-download "VIDEO_URL"

# Fall back to auto-generated if manual unavailable
yt-dlp --write-auto-sub --sub-lang en --skip-download "VIDEO_URL"
```

Auto-generated transcripts often have errors, missing punctuation, and wrong word boundaries. Manual subtitles are human-verified.

### 3. 🕐 Preserve Timestamps Always

Every segment must include timestamps. Format: `[HH:MM:SS]` or `[MM:SS]` for videos under 1 hour.

**Why this matters:** Users need to jump to specific moments. "Take me to where they discuss pricing" requires knowing the timestamp.

**Output format:**
```markdown
[00:00] Welcome to this video about machine learning
[00:15] Today we'll cover three main topics
[00:30] First, let's talk about neural networks
```

## Chapter Detection

### From Video Markers

Many videos have chapter markers embedded. Extract from metadata:

```bash
yt-dlp -j "VIDEO_URL" | jq '.chapters'
```

### Smart Detection (No Markers)

When video lacks chapters, detect natural breaks from transcript:
- Topic changes (semantic shift in content)
- Speaker changes (different voice patterns)
- Explicit transitions ("Now let's talk about...", "Moving on...")
- Long pauses between segments

## Search Within Transcripts

When user asks "where do they talk about X":

1. Search transcript for keywords and semantic matches
2. Return segments with timestamps
3. Include surrounding context (10-15 seconds before/after)

**Response format:**
```
Found 3 mentions of "machine learning":

[05:23] "...this is where machine learning really shines..."
Context: Discussing data processing approaches

[12:45] "...traditional methods vs machine learning..."
Context: Comparison section
```

Generate clickable links: `https://youtube.com/watch?v=VIDEO_ID&t=323`

## Architecture

Memory lives in `~/youtube-video-transcript/`. See `memory-template.md` for structure.

```
~/youtube-video-transcript/
├── memory.md          # Preferences + recent videos
├── videos/            # Cached transcripts (with consent)
│   └── {video_id}.md  # Individual video data
└── exports/           # Exported files
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Advanced patterns | `patterns.md` |

## Core Rules

### 1. Metadata Before Extraction

Always run `yt-dlp -j URL` first. This confirms the video, shows available languages, and reveals official chapters. Never extract blind.

### 2. Manual Over Auto

| Subtitle Type | Quality | When to Use |
|---------------|---------|-------------|
| Manual | High | Always try first |
| Auto-generated | Medium | Fallback only |

Check with `yt-dlp --list-subs URL` for unfamiliar channels.

### 3. Timestamps Are Sacred

Never strip timestamps during any operation. They enable navigation, citation, and deep linking into the video.

### 4. Cache With Consent

| User Response | Action |
|---------------|--------|
| "Yes, save it" | Cache to ~/youtube-video-transcript/videos/ |
| "No thanks" | Don't cache, show once |
| Not asked yet | Ask after first extraction |

Always tell user where files are saved and offer to show or delete them.

### 5. Handle Multiple Languages

If user doesn't specify:
1. Check available languages
2. Prefer manual over auto
3. Default to English
4. Report which language was used

```bash
yt-dlp --list-subs "VIDEO_URL"
```

### 6. Quote Extraction Includes Context

When extracting quotes for research:
- 10-15 seconds before/after for context
- Exact timestamp for the quote start
- Speaker identification if multiple speakers

### 7. Transparency on Quality

| Subtitle Type | Tell User |
|---------------|-----------|
| Manual | "Using official subtitles" |
| Auto-generated | "Using auto-generated (may have errors)" |
| None available | "No subtitles found for this video" |

## Export Formats

| Format | Use Case | Command |
|--------|----------|---------|
| Markdown | Reading, notes | Default |
| SRT | Video editors | `--sub-format srt` |
| Plain text | Search, grep | Strip timestamps |
| JSON | Programmatic | `--write-info-json` |

## Common Traps

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Not checking subtitles first | Wasted time on unavailable video | Always `--list-subs` first |
| Ignoring auto-generated quality | Garbage text with errors | Prefer manual, warn about auto |
| Losing timestamps | Can't navigate video | Never strip in any operation |
| Extracting without metadata | Missing title, chapters | Always fetch `-j` first |
| Caching without consent | Privacy violation | Ask before saving |

## Quick Commands

| User Says | Action |
|-----------|--------|
| "Transcribe this video" | Extract + display |
| "What do they say about X?" | Search + timestamps |
| "Save this transcript" | Cache with confirmation |
| "Export as SRT" | Convert format |
| "Show saved videos" | List ~/youtube-video-transcript/videos/ |
| "Delete video X" | Remove from cache |

## Security & Privacy

**Data that stays local (with your consent):**
- Transcripts cached in ~/youtube-video-transcript/ (only if you agree)
- Preferences stored locally (only after confirmation)
- No external API calls beyond YouTube's public subtitle endpoints

**Transparency guarantees:**
- Always asks before saving transcripts locally
- Tells you where files are saved
- Offers to show or delete saved data anytime

**This skill does NOT:**
- Use proxy services or third-party APIs
- Send your queries to external services
- Store credentials or authentication
- Save anything without your explicit consent

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `summarizer` — create summaries from any content
- `video-captions` — generate and edit video subtitles
- `ffmpeg` — advanced video and audio processing

## Feedback

- If useful: `clawhub star youtube-video-transcript`
- Stay updated: `clawhub sync`
