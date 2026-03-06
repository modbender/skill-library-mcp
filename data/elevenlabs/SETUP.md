# ElevenLabs - Setup Instructions

## Prerequisites

### Required Software

- **Python 3** — For running the ElevenLabs API scripts
- **ffmpeg** — For audio format conversion (used by some helper scripts)
  ```bash
  brew install ffmpeg
  ```
- **afplay** (macOS) — For optional audio playback (built-in on macOS)

Requires the `requests` Python package:

```bash
python3 -m pip install requests
```

### API Key

You need an ElevenLabs API key:

1. Sign up at: https://elevenlabs.io
2. Get your API key from the dashboard
3. Set environment variable:
   ```bash
   export ELEVENLABS_API_KEY="your-api-key-here"
   ```

Add to your shell profile (`.zshrc`, `.bashrc`, etc.) for persistence.

## Configuration

### API Key Location

The skill looks for `ELEVENLABS_API_KEY` in:
1. Environment variables (recommended)
2. `.env` file in skill folder (optional)
3. `.env` in dedicated state dir (see below)

### State Directory

Some scripts (like `quota.py`) use a dedicated state directory:
- **Default**: `~/.openclaw/elevenlabs/`
- **Override**: Set `ELEVENLABS_DIR` environment variable

The state directory can contain:
- `.env` file with `ELEVENLABS_API_KEY`
- Cached quota/usage data
- Voice clone samples (in `voiceclone-samples/`)

Created automatically on first use.

### Voice Cloning Samples

For security, `voiceclone.py` only reads audio files from:
- `~/.openclaw/elevenlabs/voiceclone-samples/`

Copy your voice samples there before running voice clone commands:
```bash
mkdir -p ~/.openclaw/elevenlabs/voiceclone-samples
cp ~/path/to/sample.mp3 ~/.openclaw/elevenlabs/voiceclone-samples/
```

Or use `--sample-dir <path>` to specify a different directory.

## Output Formats

All scripts support multiple audio formats via `--format`:

### Recommended Formats
- **`opus_48000_192`** — Best for AirPlay announcements (high quality, efficient)
- **`mp3_44100_192`** — High-quality MP3 for general use
- **`mp3_44100_128`** — Default (good quality, smaller files)

### Low-latency Formats
- **`pcm_16000`** — Raw PCM for real-time applications
- **`pcm_24000`** — Higher quality PCM

### Telephony
- **`alaw_8000`** — A-law encoding for phone systems

See SKILL.md for full format list.

## Models

Different models for different use cases:

| Model | Use When |
|-------|----------|
| **eleven_v3** | ⭐ Default - Supports audio tags like `[laughs]`, `[sighs]`, best for storytelling |
| **eleven_turbo_v2_5** | Low-latency, required for real-time/conversational, good for German |
| **eleven_flash_v2_5** | Fastest/cheapest for simple narration |

## Verification

Test your setup:

```bash
# Check quota
python3 ~/Developer/Skills/elevenlabs/scripts/quota.py

# List voices
python3 ~/Developer/Skills/elevenlabs/scripts/voices.py

# Generate test audio
python3 ~/Developer/Skills/elevenlabs/scripts/speech.py "Hello world" \
  -v <voice-id> -o test.mp3
```

Get a voice ID from the voices list, then generate speech to verify everything works.
