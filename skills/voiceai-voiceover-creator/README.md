# voiceai-creator-voiceover-pipeline

> Turn scripts into publishable voiceovers with Voice.ai — segments, chapters, captions, review page, and video muxing.

**📖 Skill documentation: [SKILL.md](SKILL.md)**

---

## Quick start

No install needed — just Node.js 20+ and the bundled CLI file.

```bash
# Set your API key
echo 'VOICE_AI_API_KEY=your-key-here' > .env

# Script + video → finished video with AI voiceover
node voiceai-vo.cjs build \
  --input my-script.md \
  --voice oliver \
  --title "My Video" \
  --video ./my-recording.mp4 \
  --mux

# Or just build the voiceover (no video)
node voiceai-vo.cjs build --input examples/youtube_script.md --voice ellie --title "My Video"

# List available voices
node voiceai-vo.cjs voices

# Test without an API key
node voiceai-vo.cjs build --input examples/youtube_script.md --voice ellie --title "My Video" --mock
```

Get your API key at [voice.ai/dashboard](https://voice.ai/dashboard).

## What it produces

```
out/<title>/
  segments/        # Numbered WAV files
  master.wav       # Stitched master (ffmpeg)
  master.mp3       # MP3 encode (ffmpeg)
  review.html      # Interactive review page
  chapters.txt     # YouTube chapters
  captions.srt     # SRT captions
  description.txt  # YouTube description
  manifest.json    # Build metadata
  timeline.json    # Segment timing
```

## Developer setup

To modify the source code:

```bash
git clone https://github.com/gizmoGremlin/VoiceAi-voiceover-creator.git
cd VoiceAi-voiceover-creator

# Install dev dependencies
npm install

# Build TypeScript
npm run build

# Re-bundle the CLI
npx esbuild src/cli.ts --bundle --platform=node --target=node20 --format=cjs --outfile=voiceai-vo.cjs

# Run tests
npm test
```

### FFmpeg (optional but recommended)

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

## Learn more

- **[SKILL.md](SKILL.md)** — Full skill documentation: commands, voices, outputs, configuration
- **[references/VOICEAI_API.md](references/VOICEAI_API.md)** — Voice.ai API endpoints and formats
- **[references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)** — Common issues and fixes

---

*Powered by [Voice.ai](https://voice.ai) · Follows the [Agent Skills specification](https://agentskills.io/specification)*
