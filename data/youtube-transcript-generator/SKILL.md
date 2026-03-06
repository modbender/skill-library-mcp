---
name: youtube-transcript-generator
description: Download and generate clean, readable transcripts from any YouTube video. Extracts subtitles (auto-generated or manual), removes timestamps and formatting, and outputs a clean paragraph-style transcript. Use when asked to transcribe, get transcript, or extract text from a YouTube video.
---

# YouTube Transcript Generator

Download clean transcripts from any YouTube video URL.

## Requirements

- `yt-dlp` must be installed (`brew install yt-dlp` or `pip install yt-dlp`)

## Usage

Run the bundled script with a YouTube URL:

```bash
bash scripts/get_transcript.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

The script will:
1. Try to download English manual subtitles first
2. Fall back to auto-generated English subtitles
3. Try all available languages if English is unavailable
4. Clean the raw subtitle file into readable paragraphs
5. Output the transcript to stdout and save to `transcript_VIDEO_ID.txt`

## Options

```bash
# Save to a specific file
bash scripts/get_transcript.sh "URL" output.txt

# Get transcript WITH timestamps (default: without)
bash scripts/get_transcript.sh "URL" output.txt en timestamps

# Get transcript in a specific language
bash scripts/get_transcript.sh "URL" output.txt fr
```

## How It Works

1. `yt-dlp` downloads the subtitle track (VTT/SRT format)
2. The script strips HTML tags and duplicate lines
3. **Without timestamps (default):** merges into clean, readable paragraphs
4. **With timestamps:** preserves `[HH:MM:SS]` markers before each line for easy reference

## Example Output

Input: `https://www.youtube.com/watch?v=HMTxOecbyPg`

Output:
```
How OpenClaw Runs My Entire Business. I record a podcast episode and that is
literally the only thing I do. Everything else is handled by 13 AI agents
running on a Mac Mini in my office...
```

## Troubleshooting

- **No subtitles found**: Not all videos have subtitles. The script will report which languages are available.
- **yt-dlp not found**: Install with `brew install yt-dlp` (macOS) or `pip install yt-dlp`.
- **Rate limited**: Wait a moment and retry. YouTube occasionally throttles subtitle requests.

## Links

- Full guides and templates: [OpenClaw Lab](https://openclawlab.xyz)
- Free OpenClaw installer: [installopenclawnow.com](https://installopenclawnow.com)
- Community: [OpenClaw Lab on Skool](https://www.skool.com/openclaw-lab)
