---
name: vea
description: Video Editing Agent (VEA) for automated video processing, highlight generation, and editing. Use when asked to index videos, create highlight reels, generate narration, add subtitles, select background music, or perform any video editing task. Supports long-form video comprehension and AI-powered clip selection.
metadata: {"openclaw": {"requires": {"env": ["MEMORIES_API_KEY"], "bins": ["ffmpeg"]}, "primaryEnv": "MEMORIES_API_KEY", "homepage": "https://github.com/Memories-ai-labs/vea-open-source"}}
---

## Installation

VEA is open source! Get it from GitHub:

```bash
# Clone the repo
git clone https://github.com/Memories-ai-labs/vea-open-source.git
cd vea-open-source

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
source .venv/bin/activate

# Copy config and add your API keys
cp config.example.json config.json
```

**📄 Paper**: https://arxiv.org/abs/2509.16811
**💻 Code**: https://github.com/Memories-ai-labs/vea-open-source

## Requirements

- **Python 3.11+**
- **FFmpeg** - Must be installed on system
- **uv** - Package manager (installed above)
- **API Keys** (in `config.json`):
  - `MEMORIES_API_KEY` (required) - Video indexing & comprehension - Get at https://memories.ai/app/service/key
  - `GOOGLE_API_KEY` (required) - Script generation - Google Cloud Console
  - `ELEVENLABS_API_KEY` (required) - TTS narration & subtitles
  - `SOUNDSTRIPE_KEY` (optional) - Background music selection

### Install FFmpeg

| OS | Command |
|----|---------|
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Windows | Download from ffmpeg.org |

## Start Server

```bash
gcloud auth application-default login  # Authenticate GCP
source .venv/bin/activate
python -m src.app
```

Server runs at `http://localhost:8000`

### Privacy Note
- Videos processed locally by VEA server
- Video frames sent to Memories.ai for AI comprehension
- ElevenLabs receives text for TTS narration
- All intermediate files stored locally in `data/outputs/`

# Video Editing Agent (VEA)

Local video editing service at `http://localhost:8000`. Runs from `~/vea`.

## ⚠️ User Interaction Flow (MUST FOLLOW)

**Before processing any video edit request, show config options and wait for confirmation:**

```
📹 VEA Video Edit Configuration

🎬 Source Video: [video path/name]
📝 Edit Request: [user's prompt]

Please confirm the following settings:
┌─────────────────┬────────┬─────────────────────────┐
│ Setting         │ Value  │ Description             │
├─────────────────┼────────┼─────────────────────────┤
│ 🔊 Original Audio        │ ❌ OFF │ Keep original video sound    │
│ 🎤 Narration             │ ✅ ON  │ AI-generated voiceover       │
│ 🎵 Background Music      │ ✅ ON  │ Auto-select from Soundstripe │
│ 📝 Subtitles             │ ✅ ON  │ Auto-generate and burn-in    │
│ 📐 Aspect Ratio          │ 16:9   │ 16:9 / 9:16 vertical / 1:1   │
│ 🎼 Snap to Beat          │ ❌ OFF │ Sync cuts to music beats     │
└─────────────────┴────────┴─────────────────────────┘

Reply "confirm" to start editing, or tell me which settings to adjust.
```

**Default Settings:**
- `original_audio`: false (mute original, use narration instead)
- `narration`: true (enable AI voiceover)
- `music`: true (enable background music)
- `subtitles`: true (enable subtitles)
- `aspect_ratio`: 1.78 (16:9 landscape)
- `snap_to_beat`: false (no beat sync)

**Aspect Ratio Options:**
- `16:9` (1.78) — Landscape, YouTube
- `9:16` (0.5625) — Vertical, TikTok/Reels
- `1:1` (1.0) — Square, Instagram

## Quick Start

```bash
# Start VEA server (use tmux for long tasks)
cd ~/vea && source .venv/bin/activate && python src/app.py
```

## Core Workflows

### 1. Index a Video (Required First Step)

Before any editing, index the video to enable AI comprehension:

```bash
curl -X POST "http://localhost:8000/video-edit/v1/index" \
  -H "Content-Type: application/json" \
  -d '{"blob_path": "data/videos/PROJECT_NAME/video.mp4"}'
```

Creates `~/vea/data/indexing/PROJECT_NAME/media_indexing.json`.

### 2. Generate Highlight Reel

```bash
curl -X POST "http://localhost:8000/video-edit/v1/flexible_respond" \
  -H "Content-Type: application/json" \
  -d '{
    "blob_path": "data/videos/PROJECT_NAME/video.mp4",
    "prompt": "Create a 1-minute highlight reel of the best moments",
    "video_response": true,
    "original_audio": false,
    "music": true,
    "narration": true,
    "aspect_ratio": 1.78,
    "subtitles": true
  }'
```

**Parameters:**
- `video_response: true` — Generate video output (vs text-only)
- `original_audio: false` — Mute original audio, use narration
- `music: true` — Add background music (requires Soundstripe API)
- `narration: true` — Generate AI voiceover (ElevenLabs)
- `subtitles: true` — Burn subtitles into video
- `aspect_ratio` — 1.78 (16:9), 1.0 (square), 0.5625 (9:16 vertical)

### 3. Manual Video Assembly

For more control, use the helper scripts:

```bash
# Add background music to existing video
python ~/vea/scripts/add_soundstripe_music.py

# Generate video with subtitles
python ~/vea/scripts/add_music_subtitles.py
```

## Directory Structure

```
~/vea/
├── data/
│   ├── videos/PROJECT_NAME/      # Source videos
│   ├── indexing/PROJECT_NAME/    # media_indexing.json
│   └── outputs/PROJECT_NAME/     # Final outputs
│       ├── PROJECT_NAME.mp4      # Final video
│       ├── clip_plan.json        # Clip timestamps + narration
│       ├── narrations/           # TTS audio files
│       ├── subtitles/            # SRT files
│       └── music/                # Background music
├── config.json                   # API keys configuration
└── src/app.py                    # FastAPI server
```

## API Keys (in config.json)

| Key | Service | Purpose | Required |
|-----|---------|---------|----------|
| `MEMORIES_API_KEY` | Memories.ai | Video indexing & comprehension | ✅ Yes |
| `GOOGLE_API_KEY` | Gemini | Script generation | ✅ Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs | TTS narration, STT subtitles | ✅ Yes |
| `SOUNDSTRIPE_KEY` | Soundstripe | Background music selection | Optional |

## Common Issues

**"ViNet assets not found"** — Dynamic cropping disabled. Set `enable_dynamic_cropping: false` in config.json.

**Subprocess fails from API but works manually** — Run server in tmux to preserve environment.

**Music download 401/403** — Check Soundstripe API key validity.

**Clip timestamps wrong** — Ensure `original_audio: true` to enable timestamp refinement via transcription.

## Manual Music Addition

When Soundstripe fails, manually download and mix:

```bash
# Download from Soundstripe API
SOUNDSTRIPE_KEY=$(jq -r '.api_keys.SOUNDSTRIPE_KEY' ~/vea/config.json)
curl -s "https://api.soundstripe.com/v1/songs/TRACK_ID" \
  -H "Authorization: Token $SOUNDSTRIPE_KEY" | jq '.included[0].attributes.versions.mp3'

# Mix with ffmpeg (15-20% music volume)
ffmpeg -y -i video.mp4 -i music.mp3 \
  -filter_complex "[1:a]volume=0.18,afade=t=out:st=70:d=4[m];[0:a][m]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac output.mp4
```

## References

- [API Documentation](references/api.md) — Full endpoint specs
- [Config Schema](references/config.md) — Configuration options
