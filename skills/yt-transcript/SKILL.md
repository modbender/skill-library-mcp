---
name: YouTube Transcript Extraction
description: Extract high-quality transcripts from YouTube videos using multiple methods.
---

# YouTube Transcript Extraction

Extract high-quality transcripts from YouTube videos using multiple methods.

## Commands

```bash
# Extract transcript from YouTube URL or video ID
/root/clawd/yt-transcript https://youtu.be/VIDEO_ID
/root/clawd/yt-transcript VIDEO_ID
```

## Features

- **Dual fallback system**: Tries Supadata API first, falls back to yt-dlp
- **Auto-generated transcripts**: Works even if no manual captions exist
- **Clean output**: Returns plain text transcript ready for analysis
- **Fast**: API method completes in seconds

## Use Cases

- Summarize long videos without watching
- Extract key quotes and insights
- Content research and analysis
- Create written summaries for videos
- Extract educational content

## Technical Details

- **Primary**: Supadata API (fast, clean formatting)
- **Fallback**: yt-dlp CLI tool (comprehensive, handles edge cases)
- **Output**: Plain text transcript with timestamps removed
- **API key**: Stored in `.env` as `SUPADATA_API_KEY`

## Example Workflow

Rob sends YouTube link → Alto pulls transcript → summarizes key points → Rob decides if worth watching

Saves 10-30 minutes per video!
