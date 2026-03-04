# VEA Configuration

Config file: `~/vea/config.json`

## Full Schema

```json
{
  "api_keys": {
    "GOOGLE_API_KEY": "AIza...",
    "ELEVENLABS_API_KEY": "sk_...",
    "SOUNDSTRIPE_KEY": "...",
    "MEMORIES_API_KEY": "sk-...",
    "GOOGLE_CLOUD_PROJECT": "project-id",
    "GOOGLE_CLOUD_LOCATION": "us-central1"
  },
  "features": {
    "enable_dynamic_cropping": false,
    "enable_subtitles": true,
    "enable_fcpxml_export": true
  },
  "video_processing": {
    "default_fps": 24,
    "summary_fps": 1,
    "summary_crf": 40
  }
}
```

## API Keys

### GOOGLE_API_KEY
Gemini API key for video comprehension and script generation.
- Get from: https://aistudio.google.com/app/apikey
- Used by: GeminiGenaiManager

### ELEVENLABS_API_KEY
ElevenLabs API for TTS narration and STT subtitles.
- Get from: https://elevenlabs.io/api
- Used by: GenerateNarrationAudio, GenerateSubtitles

### SOUNDSTRIPE_KEY
Soundstripe API for background music selection.
- Get from: Soundstripe account dashboard
- Used by: MusicSelection

### MEMORIES_API_KEY
Memories.ai API for video upload/transcript.
- V1 key for uploads, V2 key for transcripts
- Used by: MemoriesAiManager

## Features

### enable_dynamic_cropping
- `true` — Use ViNet saliency model for smart cropping
- `false` — Use center crop (recommended if ViNet not installed)

**Note:** ViNet requires ~2GB download. Run `python -m lib.utils.vinet_setup` to install.

### enable_subtitles
- `true` — Generate and burn subtitles using ElevenLabs STT
- `false` — Skip subtitle generation

### enable_fcpxml_export
- `true` — Export Final Cut Pro XML project file
- `false` — Skip FCPXML export

## Video Processing

### default_fps
Target frame rate for normalized footage. Default: 24.

### summary_fps
Frame rate for video summaries (indexing). Default: 1.

### summary_crf
Quality setting for summaries (higher = smaller/worse). Default: 40.

## Environment Variables

Config values are loaded into environment variables at startup:

```python
os.environ["GOOGLE_API_KEY"] = config["api_keys"]["GOOGLE_API_KEY"]
os.environ["ELEVENLABS_API_KEY"] = config["api_keys"]["ELEVENLABS_API_KEY"]
# etc.
```

## Gemini Configuration

For Vertex AI vs Gemini API:

```python
# In GeminiGenaiManager, auto-detects based on GOOGLE_API_KEY presence:
# - If GOOGLE_API_KEY set: uses Gemini API (vertexai=False)
# - Otherwise: uses Vertex AI (requires GOOGLE_CLOUD_PROJECT)
```
