# Dub YouTube with Voice.ai

> Dub YouTube videos with AI voiceovers — chapters, captions, and audio replacement in one command.

**📖 Skill documentation: [SKILL.md](SKILL.md)**

## Quick start

Requires Node.js 20+. No install needed.

```bash
# Set your API key
export VOICE_AI_API_KEY=your-key-here

# Dub a YouTube video with AI voiceover
node voiceai-vo.cjs build \
  --input my-script.md \
  --voice oliver \
  --title "My YouTube Video" \
  --video ./my-recording.mp4 \
  --mux \
  --template youtube

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
  muxed.mp4        # Dubbed video (if --video --mux)
  segments/        # Numbered WAV files
  master.wav       # Stitched voiceover
  master.mp3       # MP3 for upload
  chapters.txt     # Paste into YouTube description
  captions.srt     # Upload as YouTube subtitles
  description.txt  # Ready-made YouTube description
  review.html      # Interactive review page
```

## Learn more

- **[SKILL.md](SKILL.md)** — Full skill documentation: commands, voices, outputs, configuration
- **[references/VOICEAI_API.md](references/VOICEAI_API.md)** — Voice.ai API endpoints and formats
- **[references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)** — Common issues and fixes

---

*Powered by [Voice.ai](https://voice.ai) · Follows the [Agent Skills specification](https://agentskills.io/specification)*
