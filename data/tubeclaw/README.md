# TubeClaw

**YouTube Video Analyzer** - Extract insights from any YouTube video, remove fluff, and discover resources.

## Why?

YouTube videos are full of valuable information buried in:
- ⏱️ Long introductions
- 📢 Sponsor segments  
- 🎵 Music/intros
- 💬 Off-topic discussions

**TubeClaw** extracts the signal from the noise.

## Features

- ✅ Fetches video transcripts
- ✅ Removes ads & sponsorships
- ✅ Extracts key insights
- ✅ Finds mentioned tools/resources
- ✅ Identifies GitHub repos & links
- ✅ Generates clean summary

## Quick Start

```bash
# Clone
git clone https://github.com/Snail3D/tubeclaw.git
cd tubeclaw

# Install dependencies (video-transcript-downloader)
# See: https://github.com/Snail3D/video-transcript-downloader

# Analyze a video
node analyze.js --url "https://youtube.com/watch?v=..."
```

## Example

```bash
node analyze.js --url "https://www.youtube.com/watch?v=AEmHcFH1UgQ"
```

**Output:**
```
🎯 TUBECLAW ANALYSIS

📝 SUMMARY:
Discussion about PI coding agent harness, Claude Code, 
and the future of AI agents...

🏷️ TOPICS:
ai, agents, coding, bash, security

🔗 RESOURCES:
  1. https://github.com/... (PI project)
  2. Claude Code (Technology mentioned)
  3. https://sentry.io/...

📊 Transcript length: 45023 chars
🎬 Video: https://www.youtube.com/watch?v=AEmHcFH1UgQ
```

## Requirements

- Node.js 14+
- [video-transcript-downloader](https://github.com/Snail3D/video-transcript-downloader) skill
- OpenClaw/Clawdbot environment

## How It Works

1. **Extract** - Gets transcript via youtube-transcript-plus
2. **Clean** - Removes ads, intros, filler
3. **Analyze** - Extracts topics, tools, links
4. **Summarize** - Generates actionable summary

## Future Features

- [ ] AI-powered deep analysis (Claude/GPT)
- [ ] Chapter/timestamp extraction
- [ ] Export to Notion/Obsidian
- [ ] Compare multiple videos
- [ ] Build knowledge base from channel

## License

MIT - OpenClaw
