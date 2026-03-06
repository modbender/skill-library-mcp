---
name: bili-summary
description: "Bilibili video download, subtitle extraction, and AI summarization
  tool. Supports video info, audio download, Whisper transcription, and
  Gemini-powered detailed summaries. Use when: user asks to download/summarize
  B站 video, extract subtitles, or transcribe bilibili video."
---


# bili-summary

Bilibili (B站) video download, subtitle extraction, and AI summarization tool.

## When to Use

✅ **USE this skill when:**

- "download Bilibili video"
- "extract B站 subtitles"
- "summarize B站 video"
- "B站视频总结"
- "bilibili transcription"
- Any Bilibili video URL

## Features

- Get video info (title, duration, uploader)
- Download B站 video (video + audio)
- Extract subtitles (B站 CC subtitles)
- Audio extraction + Whisper transcription (when no subtitles)
- Gemini AI detailed summary (chapters + key content + key insights + conclusion)

## Prerequisites

### 1. Install Dependencies

```bash
# Using miniconda3 (recommended)
~/miniconda3/bin/pip install yt-dlp faster-whisper

# Or using system Python (may require sudo)
pip install yt-dlp faster-whisper
```

### 2. Get Gemini API Key

This skill uses **Google Gemini 2.5 Flash** for AI summarization.

**Steps:**
1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

**Pricing:** Gemini 2.5 Flash has generous free tier (15 RPM, 1M TPM)

### 3. Set Environment Variable

```bash
# Add to your ~/.bashrc or ~/.zshrc for permanent setup
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Or set temporarily for current session
export GEMINI_API_KEY="your-api-key-here"
```

## Quick Start

### Full Workflow (Recommended)

```bash
# Download audio, transcribe, and summarize in one command
uv run {baseDir}/scripts/bili-summary.py "https://www.bilibili.com/video/BV1xx411c7mu" --action summary
```

### Other Actions

```bash
# Get video info only
uv run {baseDir}/scripts/bili-summary.py "URL" --action info

# Download subtitle (if available)
uv run {baseDir}/scripts/bili-summary.py "URL" --action subtitle

# Download and transcribe audio only
uv run {baseDir}/scripts/bili-summary.py "URL" --action transcribe

# Download full video
uv run {baseDir}/scripts/bili-summary.py "URL" --action video
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| url | Bilibili video URL (BV号或完整链接) | required |
| --action | Operation: info/subtitle/transcribe/video/summary | summary |
| --output | Output directory | ~/openclaw/workspace/coding-agent/temp/bili-summary |

## Output Files

Default output: `~/openclaw/workspace/coding-agent/temp/bili-summary/`

```
temp/bili-summary/
├── audio.m4a       # Downloaded audio (deleted after summary)
├── subtitle.txt    # Transcribed text (deleted after summary)
└── summary.txt    # AI summary content
```

## Workflow

### summary (full workflow)

1. **Get video info** - yt-dlp fetches title, duration, uploader
2. **Try B站 subtitles** - Call Bilibili API for CC subtitles
3. **Fallback to Whisper** - If no subtitles, download audio + faster-whisper (tiny model) transcription
4. **AI Summary** - Call Gemini 2.5 Flash API for detailed summary

### Time Estimate

| Step | Time |
|------|------|
| Audio download | ~15s |
| Whisper transcription (tiny) | ~25s |
| Gemini summary | ~5s |
| **Total** | **~45s** |

## API Configuration

### Recommended API: Google Gemini

- **Model:** gemini-2.5-flash
- **Endpoint:** https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent
- **Free Tier:** 15 requests/minute, 1M tokens/minute
- **Sign up:** https://aistudio.google.com/app/apikey

### Alternative APIs (not implemented)

If you want to use other LLMs:

- **OpenAI GPT-4o** - https://api.openai.com/v1/chat/completions
- **Anthropic Claude** - https://api.anthropic.com/v1/messages
- **MiniMax** - https://api.minimax.chat/v1/text/chatcompletion_v2

*Note: Current implementation only supports Gemini. PRs welcome for other providers.*

## First-Time Setup Guide

### Step 1: Install Python dependencies

```bash
# Check if miniconda3 exists
ls ~/miniconda3/bin/python

# Install dependencies
~/miniconda3/bin/pip install yt-dlp faster-whisper

# Or use uv
uv pip install yt-dlp faster-whisper
```

### Step 2: Get API Key

1. Go to https://aistudio.google.com/app/apikey
2. Create new API key
3. Copy the key

### Step 3: Test the setup

```bash
# Set API key
export GEMINI_API_KEY="your-key-here"

# Test with a simple video
uv run {baseDir}/scripts/bili-summary.py "https://www.bilibili.com/video/BV1xx411c7mu" --action info
```

If you see JSON output with video title, duration, etc., you're ready!

### Step 4: Run full summarization

```bash
uv run {baseDir}/scripts/bili-summary.py "https://www.bilibili.com/video/BV1xxx" --action summary
```

## Troubleshooting

### "No module named 'yt-dlp'"

```bash
~/miniconda3/bin/pip install yt-dlp faster-whisper
```

### "GEMINI_API_KEY not found"

```bash
# Check if environment variable is set
echo $GEMINI_API_KEY

# Set it
export GEMINI_API_KEY="your-key"
```

### "No subtitles available"

The skill automatically falls back to Whisper transcription. This may take longer but works for any video with audio.

### "API rate limit exceeded"

Wait a minute and retry, or check your API quota at https://aistudio.google.com/app/apikey

## Security Notes

- ✅ API key is read from `GEMINI_API_KEY` environment variable only
- ✅ No hardcoded API keys in source code
- ✅ Temporary files stored in workspace temp directory
- ⚠️ Audio/subtitle files are NOT auto-deleted (manual cleanup required)

## File Structure

```
bili-summary/
├── SKILL.md              # This documentation
├── _meta.json            # ClawHub metadata (auto-generated)
└── scripts/
    └── bili-summary.py   # Main script
```

## License

MIT License - Use at your own risk. Respect Bilibili's terms of service.
