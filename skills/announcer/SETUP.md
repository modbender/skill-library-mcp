# Announcer - Setup Instructions

## Prerequisites

### Required Software

- **macOS** — This skill requires Airfoil, which is macOS-only
- **Airfoil** (Rogue Amoeba) — Must be running on the host Mac
  - Download from: https://rogueamoeba.com/airfoil/
- **Python 3** — For running the announcement script
- **ffmpeg** — For audio format conversion
  ```bash
  brew install ffmpeg
  ```

### API Keys

- **ElevenLabs API key** — Required for TTS generation
  - Sign up at: https://elevenlabs.io
  - Set environment variable: `ELEVENLABS_API_KEY`

### Dependencies

- **elevenlabs skill** — Sibling skill for TTS generation (must be installed)

## Configuration

User config lives at `~/clawd/announcer/config.json`:

```json
{
  "speakers": ["Living (2)", "Kitchen", "Office"],
  "excluded": ["Computer"],
  "elevenlabs": {
    "voice_id": "your-voice-id",
    "format": "opus_48000_192"
  },
  "audio": {
    "output_format": "mp3",
    "stereo": true,
    "sample_rate": 48000,
    "bitrate": "256k",
    "chime_file": "gong_stereo.mp3"
  },
  "airfoil": {
    "source": "System-Wide Audio",
    "connection_timeout_seconds": 30,
    "volume": 0.7
  }
}
```

### Config Fields

| Field | Description |
|-------|-------------|
| `speakers` | AirPlay speaker names to connect |
| `excluded` | Speaker names to never connect |
| `elevenlabs.voice_id` | ElevenLabs voice to use |
| `audio.chime_file` | Chime sound file in `assets/` (set `null` to disable) |
| `airfoil.connection_timeout_seconds` | Time to wait for speakers to connect |
| `airfoil.volume` | Speaker volume (0.0–1.0) |

### Getting Your Voice ID

1. Log in to ElevenLabs dashboard
2. Go to Voice Library or Voice Lab
3. Copy the voice ID for your preferred voice
4. Add it to `config.json` under `elevenlabs.voice_id`
