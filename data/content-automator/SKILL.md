---
name: crusty-content-automator
description: "Faceless YouTube content automation pipeline. Generates scripts, converts to speech via ElevenLabs TTS, assembles videos with ffmpeg. Supports daily trading updates, news summaries, and educational content. Run: python3 scripts/content_automator.py --help"
version: 1.0.0
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      bins:
        - python3
        - ffmpeg
      env:
        - ELEVENLABS_API_KEY
    skillKey: content-automator
---

# Content Automator — Faceless YouTube Pipeline

Automated content creation for faceless YouTube channels. Generates scripts, converts to speech, assembles videos.

## Usage

```bash
# Generate a trading update video
python3 scripts/content_automator.py trading --portfolio ~/.openclaw/workspace/ECONOMIC_DASHBOARD.md --output ~/Videos/

# Generate from custom script
python3 scripts/content_automator.py script --file my_script.txt --title "My Video" --output ~/Videos/

# List available templates
python3 scripts/content_automator.py templates

# Generate news summary
python3 scripts/content_automator.py news --topic "AI agents" --sources "twitter,colony" --output ~/Videos/
```

## Features

1. **Script Generation** — Templates for trading updates, news summaries, educational content
2. **TTS Integration** — ElevenLabs API with voice selection
3. **Video Assembly** — ffmpeg-based composition with background visuals
4. **Metadata Generation** — YouTube titles, descriptions, tags
5. **Batch Processing** — Create multiple videos from data sources

## Templates

- `trading-update` — Daily P&L, positions, market commentary
- `news-roundup` — AI/agent industry news summary
- `tutorial` — Educational content with code examples
- `story` — Narrative content with scene breaks

## Output

Each run produces:
- `{title}.mp4` — Final video file
- `{title}.txt` — Script/lyrics
- `{title}_meta.json` — YouTube metadata (title, desc, tags)
- `{title}_assets/` — Audio segments, temp files

## Security Notes

This skill intentionally accesses:
- `ELEVENLABS_API_KEY` from environment (for TTS API calls)
- External HTTPS requests to `api.elevenlabs.io` (text-to-speech service)
- Subprocess execution of `ffmpeg` (video assembly)

These behaviors are required for core functionality and are declared in SKILL.md metadata.
