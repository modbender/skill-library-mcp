---
name: video-analyzer
description: Download, transcribe, and analyze videos from YouTube, X/Twitter, and TikTok with local Whisper processing. Perfect for extracting TL;DRs, timestamps, and actionable insights.
homepage: https://github.com/minilozio/video-analyzer-skill
metadata:
  {
    "openclaw":
      {
        "emoji": "🎥",
        "requires": { "bins": ["uv", "yt-dlp", "ffmpeg", "whisper-cli"] },
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
            {
              "id": "yt-dlp-brew",
              "kind": "brew",
              "formula": "yt-dlp",
              "bins": ["yt-dlp"],
              "label": "Install yt-dlp (brew)",
            },
            {
              "id": "ffmpeg-brew",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg (brew)",
            },
            {
              "id": "whisper-cpp-brew",
              "kind": "brew",
              "formula": "ggerganov/ggerganov/whisper-cpp",
              "bins": ["whisper-cli"],
              "label": "Install whisper-cpp (brew)",
            },
          ],
      },
  }
---

# Video Analyzer 🎥

A tool to download, transcribe, and analyze videos from any platform using a smart two-tier system (yt-dlp for fast subtitles, local whisper-cpp for robust fallback).

## How to Use

When the user asks you to summarize, transcribe, or download a video/audio from a URL, use the bundled python script:

```bash
uv run {baseDir}/scripts/analyze_video.py --action <ACTION> --url "<URL>" [--quality <normal|max>] [--lang <en|it|etc>]
```

### Supported Actions:
- `transcript`: Extracts the text with timestamps. **Use this when the user asks for a summary or transcript.**
- `download-video`: Downloads the video as MP4 to the Desktop.
- `download-audio`: Downloads the audio as M4A/MP3 to the Desktop.

### Analyzing a Video (IMPORTANT)

If the user asks for a **summary, analysis, or key moments**:
1. Run the script with `--action transcript`.
2. The script will output the path to a `.txt` file containing the timestamped transcript.
3. Read that file.
4. Output your response **EXACTLY** in this Markdown format:

```markdown
## 📝 TL;DR
[A punchy 3-sentence summary of the video's core message]

## ⏱️ Key Moments
- [MM:SS] [Brief description of what is discussed]
- [MM:SS] [Brief description of what is discussed]
- [MM:SS] [Brief description of what is discussed]
*(Extract 3 to 7 key moments depending on video length)*

## 💡 Actionable Insights
1. [Practical takeaway 1]
2. [Practical takeaway 2]
3. [Practical takeaway 3]

---
```

### Local Whisper Quality
If the script needs to fall back to Whisper (e.g., for X/Twitter videos), it uses `normal` by default:
- `normal`: Fast (~1 min for 30 min video) — **Default**
- `max`: Best quality (~5 min for 30 min video) — use `--quality max` when accuracy is critical

### Multilingual Support
All Whisper models are **multilingual by default**. The skill can transcribe videos in any language (Italian, Spanish, Japanese, etc.).

**IMPORTANT:** Always respond to the user in THEIR language, not the video's language. If the user speaks Italian but sends an English video, give them the summary in Italian. 

### Finding specific moments
The transcript includes **precise timestamps** like `[05:53] text...`. If the user asks "When do they talk about X?", grep the transcript and return the exact timestamp from the file.
