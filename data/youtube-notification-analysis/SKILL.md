---
name: youtube-notification-analysis
description: Analyze YouTube notifications for investment and trading insights. Use when user wants investment advice from YouTube, analyzing stock crypto or financial content, executing /ytb_trade command, or getting video subtitles via yt-dlp and whisper-cpp. Workflow is open YouTube click notification bell extract video IDs get subtitles or download plus whisper-cpp analyze then execute trades.
---

# YouTube Notification Analysis

Analyze YouTube notifications for investment insights.

## Workflow

1. **Open YouTube**: `browser action=open profile=openclaw targetUrl=https://www.youtube.com`
2. **Click notification bell**: Find ref="e8" button
3. **Extract video IDs**: From snapshot, find investment-related videos
4. **Get subtitles**:
   - First try: `yt-dlp --write-subs --skip-download --sub-lang zh-Hans,en <video_url>`
   - If no subtitles: Download video + whisper-cpp analysis
5. **Analyze**: Summarize investment recommendations
6. **Execute trades**: Use tiger-trade skill

## Subtitle Extraction

```bash
# Try yt-dlp first
yt-dlp --write-subs --skip-download --sub-lang zh-Hans,en "https://www.youtube.com/watch?v=VIDEO_ID" -o /tmp/sub

# If no subtitles, download + whisper
yt-dlp -f best "https://www.youtube.com/watch?v=VIDEO_ID" -o /tmp/video.mp4
whisper-cpp/bin/main -m whisper-cpp/models/ggml-base.bin -f /tmp/video.mp4 --language ZH
```

## Investment Analysis

Focus on investment and trading related videos from YouTube notifications. Analyze content for stock, crypto, macro finance, and market trends.

## Logging

All logs saved to `/tmp/youtube_investment_*.log`
