---
name: youtube-pro
description: Advanced YouTube analysis, transcripts, and metadata extraction.
metadata: {"clawdbot":{"emoji":"📺"}}
---

# YouTube Pro (Miss Kim Edition)

Deep dive into YouTube content. Uses `summarize` for transcripts and `web_fetch` for metadata.

## Workflow

### 1. Fast Summary / Transcript
Use the built-in `summarize` tool:
- **Summary**: `summarize "URL"`
- **Transcript**: `summarize "URL" --youtube auto --extract-only`

### 2. Video Intelligence (Miss Kim analysis)
When the Master wants to "analyze" a video:
- Fetch transcript via `summarize`.
- Use `gemini` (MiniPC) to analyze the core message, audience sentiment (via comments if available), and practical takeaways.

### 3. Audio/Frame Extraction (Optional)
If frames or audio are needed:
- Use `yt-dlp` (MiniPC) to download specific segments.
- Use `ffmpeg` to extract frames for visual analysis.

## Protocol
- **Brevity**: Summarize long transcripts into "핵심 요약 5줄" first.
- **Actionable**: Always add a "미스 김의 제언" (Miss Kim's Suggestion) at the end.
- **Links**: Always include the source link with timestamps for key moments.
