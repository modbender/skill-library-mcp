---
name: yt-digest
description: Extract summaries, transcripts, and key moments from YouTube videos.
---

# yt-digest

Extract summaries, transcripts, and key moments from YouTube videos.

## Features

- **Transcript extraction**: Get full transcript with timestamps
- **Summary**: AI-generated summary of video content
- **Key moments**: Extract chapters and highlights
- **Audio output**: Convert summary to audio (via sag skill)

## Usage

```bash
# Get transcript
yt-digest transcript "https://youtube.com/watch?v=..."

# Get summary
yt-digest summary "https://youtube.com/watch?v=..."

# Get key moments/chapters
yt-digest chapters "https://youtube.com/watch?v=..."

# Full analysis
yt-digest analyze "https://youtube.com/watch?v=..."
```

## Output

```
📺 Video: How to Build AI Agents
👤 Channel: TechChannel
⏱️ Duration: 15:32

## Summary
This video covers the basics of building AI agents...

## Key Moments
- 0:00 Introduction
- 2:30 Setting up the environment
- 5:45 Building the first agent
- 10:20 Advanced techniques
- 14:00 Conclusion

## Transcript (first 1000 chars)
...
```

## Requirements

Uses YouTube's transcript API (no API key needed for public videos).
