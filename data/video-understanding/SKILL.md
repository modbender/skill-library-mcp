---
name: video-understanding
description: >
  Analyze videos with Google Gemini multimodal AI. Download from any URL (Loom, YouTube, TikTok,
  Vimeo, Twitter/X, Instagram, 1000+ sites) and get transcripts, descriptions, and answers to
  questions. Use when asked to watch, analyze, summarize, or transcribe a video, or answer
  questions about video content. Triggers on video URLs or requests involving video understanding.
compatibility: "Requires yt-dlp, ffmpeg, and GEMINI_API_KEY environment variable. Python 3.10+ with uv."
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      bins: ["yt-dlp", "ffmpeg"]
      env: ["GEMINI_API_KEY"]
    primaryEnv: "GEMINI_API_KEY"
    install:
      - id: "yt-dlp-brew"
        kind: "brew"
        formula: "yt-dlp"
        bins: ["yt-dlp"]
        label: "Install yt-dlp (brew)"
      - id: "ffmpeg-brew"
        kind: "brew"
        formula: "ffmpeg"
        bins: ["ffmpeg"]
        label: "Install ffmpeg (brew)"
---

# Video Understanding (Gemini)

Analyze videos using Google Gemini's multimodal video understanding. Supports 1000+ video sources via yt-dlp.

## Requirements

- `yt-dlp` — `brew install yt-dlp` / `pip install yt-dlp`
- `ffmpeg` — `brew install ffmpeg` (for merging video+audio streams)
- `GEMINI_API_KEY` environment variable

## Default Output

Returns structured JSON:
- **transcript** — Verbatim transcript with `[MM:SS]` timestamps
- **description** — Visual description (people, setting, UI, text on screen, flow)
- **summary** — 2-3 sentence summary
- **duration_seconds** — Estimated duration
- **speakers** — Identified speakers

## Usage

### Analyze a video (structured JSON output)

```bash
uv run {baseDir}/scripts/analyze_video.py "<video-url>"
```

### Ask a question (adds "answer" field)

```bash
uv run {baseDir}/scripts/analyze_video.py "<video-url>" -q "What product is shown?"
```

### Override prompt entirely

```bash
uv run {baseDir}/scripts/analyze_video.py "<video-url>" -p "Custom prompt" --raw
```

### Download only (no analysis)

```bash
uv run {baseDir}/scripts/analyze_video.py "<video-url>" --download-only -o video.mp4
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-q` / `--question` | Question to answer (added to default fields) | none |
| `-p` / `--prompt` | Override entire prompt (ignores -q) | structured JSON |
| `-m` / `--model` | Gemini model | gemini-2.5-flash |
| `-o` / `--output` | Save output to file | stdout |
| `--keep` | Keep downloaded video file | false |
| `--download-only` | Download only, skip analysis | false |
| `--max-size` | Max file size in MB | 500 |
| `--raw` | Raw text output instead of JSON | false |

## How It Works

1. **YouTube URLs** → Passed directly to Gemini (no download needed)
2. **All other URLs** → Downloaded via yt-dlp → uploaded to Gemini File API → poll until processed
3. Gemini analyzes video with structured prompt → returns JSON
4. Temp files and Gemini uploads cleaned up automatically

## Supported Sources

Any URL supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md): Loom, YouTube, TikTok, Vimeo, Twitter/X, Instagram, Dailymotion, Twitch, and 1000+ more.

## Tips

- Use `-q` for targeted questions on top of the full analysis
- YouTube is fastest (no download step)
- Large videos (10min+) work fine — Gemini File API supports up to 2GB (free) / 20GB (paid)
- The script auto-installs Python dependencies via `uv`
