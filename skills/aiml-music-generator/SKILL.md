---
name: aimlapi-music
description: Generate high-quality music/songs via AIMLAPI. Supports Suno, Udio, Minimax, and ElevenLabs music models. Use when the user asks for music, songs, or soundtracks with specific lyrics or styles.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎵",
        "requires": { "bins": ["python"], "env": ["AIMLAPI_API_KEY"] },
        "primaryEnv": "AIMLAPI_API_KEY",
      },
  }
---

# AIMLAPI Music Generation

## Overview

Generate music tracks using state-of-the-art AI models (Suno, Udio, Minimax, ElevenLabs).

## Quick start

```bash
# General music (instrumental)
python {baseDir}/scripts/gen_music.py \
  --prompt "cyberpunk synthwave with heavy bass and retro synths" \
  --model "minimax/music-2.0"

# Song with lyrics
python {baseDir}/scripts/gen_music.py \
  --prompt "A happy pop song about a robot learning to feel" \
  --lyrics "[Verse 1]\nWires and gears, clicking in time..." \
  --model "minimax/music-2.0"

# Short clip (ElevenLabs)
python {baseDir}/scripts/gen_music.py \
  --prompt "lo-fi pop hip-hop ambient" \
  --model "elevenlabs/eleven_music" \
  --length 20000
```

## Arguments

- `--prompt`: (Required) Style or context for the music.
- `--lyrics`: Optional lyrics for vocal tracks.
- `--model`: Model choice (default: `minimax/music-2.0`).
- `--length`: Length in milliseconds (primarily for ElevenLabs).
- `--out-dir`: Directory to save the final MP3.

## Workflow

The script uses a two-step process:
1. `POST /v2/generate/audio`: Creates the generation task.
2. `GET /v2/generate/audio?generation_id=...`: Polls for the result until `completed` or `failed`.
