---
name: gemini-reader
description: Understand local non-text files (PDF, video, audio) using Gemini API. Use when the user asks to read, summarize, or analyze a PDF document, video file (mp4/mov/webm), or audio file (mp3/wav/m4a/ogg), including audio transcription. NOT for images — the main model already has vision capabilities, prefer using it directly for image understanding.
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "requires": { "env": ["GEMINI_API_KEY"], "pip": ["google-genai"] },
      },
  }
---

# Gemini Reader

Analyze local PDF, video, and audio files via Gemini API (Python SDK `google-genai`).

## Prerequisites

- `google-genai` Python package installed (`pip install google-genai`)
- `GEMINI_API_KEY` environment variable set
- Supported: PDF, video (mp4/webm/mov/avi/mkv), audio (mp3/wav/m4a/ogg)

## Usage

```bash
python3 scripts/gemini_read.py <file> "<prompt>" [--model MODEL] [--output PATH]
```

### Examples

```bash
# Summarize a PDF
python3 scripts/gemini_read.py paper.pdf "Summarize the key findings of this paper"

# Analyze a video
python3 scripts/gemini_read.py lecture.mp4 "List the main topics covered in this video"

# Transcribe audio
python3 scripts/gemini_read.py recording.m4a "Transcribe this audio verbatim"

# Save output to file
python3 scripts/gemini_read.py report.pdf "Extract all data tables" --output tables.txt
```

### Model selection

| Alias | Full name | Best for |
|-------|-----------|----------|
| `3-flash` (default) | gemini-3-flash-preview | Fast, cheap, everyday use |
| `2.5-flash` | gemini-2.5-flash | Stable, good balance |
| `2.5-pro` | gemini-2.5-pro | Deep analysis, long docs |
| `3-pro` | gemini-3-pro-preview | Advanced reasoning |
| `3.1-pro` | gemini-3.1-pro-preview | Latest pro capabilities |

Use alias with `-m`: `gemini_read.py file.pdf "prompt" -m 2.5-pro`

## Notes

- Files are uploaded to Google's Gemini API for processing and deleted after use. Do not use with confidential or sensitive files.
- The script enforces a file extension whitelist (PDF/video/audio only), blocks known sensitive paths, and rejects symlinks.
- All files go through File Upload API (upload -> generate -> cleanup), unified flow regardless of size
- For files on remote nodes (e.g. Mac), transfer to VM first using Tailscale or scp
- The script auto-detects MIME type from file extension
- API calls are direct — no sandbox restrictions, no CLI overhead
- Requires `GEMINI_API_KEY` env var or `google-genai` configured auth
