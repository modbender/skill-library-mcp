---
name: audio-processing
description: Audio ingestion, analysis, transformation, and generation (Transcribe, TTS, VAD, Features).
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires": { 
          "bins": ["ffmpeg", "python3"], 
          "pip": ["openai-whisper", "gTTS", "librosa", "pydub", "soundfile", "numpy", "webrtcvad-wheels"] 
        },
        "install":
          [
            {
              "id": "ffmpeg",
              "kind": "brew",
              "package": "ffmpeg",
              "label": "Install ffmpeg",
            },
            {
              "id": "python-deps",
              "kind": "pip",
              "package": "openai-whisper gTTS librosa pydub soundfile numpy webrtcvad-wheels",
              "label": "Install Python dependencies",
            }
          ],
        "version": "1.1.0",
      },
  }
---

# Audio Processing Skill

A comprehensive toolset for audio manipulation and analysis with security validations.

## Security

- File paths are validated to prevent path traversal attacks
- Access to system directories (/etc, /proc, /sys, /root) is blocked
- TTS text input is limited to 10,000 characters
- All file operations use resolved absolute paths

## Tool API

### audio_tool
Perform audio operations like transcription, text-to-speech, and feature extraction.

- **Parameters:**
  - `action` (string, required): One of `transcribe`, `tts`, `extract_features`, `vad_segments`, `transform`.
  - `file_path` (string, optional): Path to input audio file.
  - `text` (string, optional): Text for TTS (max 10,000 chars).
  - `output_path` (string, optional): Path for output file (default: auto-generated).
  - `model` (string, optional): Whisper model size (tiny, base, small, medium, large). Default: `base`.
  - `ops` (string, optional): JSON string of operations for transform action.

**Usage:**

```bash
# Transcribe audio file
uv run --with "openai-whisper" --with "pydub" --with "numpy" skills/audio-processing/tool.py transcribe --file_path input.wav

# Transcribe with specific model
uv run --with "openai-whisper" skills/audio-processing/tool.py transcribe --file_path input.wav --model small

# Text-to-speech
uv run --with "gTTS" skills/audio-processing/tool.py tts --text "Hello world" --output_path hello.mp3

# Extract audio features
uv run --with "librosa" --with "numpy" --with "soundfile" skills/audio-processing/tool.py extract_features --file_path input.wav

# Voice activity detection (find speech segments)
uv run --with "pydub" skills/audio-processing/tool.py vad_segments --file_path input.wav

# Transform audio (trim, resample, normalize)
uv run --with "pydub" skills/audio-processing/tool.py transform --file_path input.wav --ops '[{"op": "trim", "start": 10, "end": 30}, {"op": "normalize"}]'
```

## Actions

### transcribe
Convert speech to text using OpenAI Whisper.

- Returns: `{ "text": "...", "segments": [...] }`
- Models: tiny, base, small, medium, large (larger = more accurate, slower)

### tts
Generate speech from text using Google TTS.

- Returns: `{ "file_path": "output.mp3", "status": "created" }`
- Language: English (default)

### extract_features
Extract audio features for analysis.

- Returns: duration, sample_rate, mfcc_mean, rms_mean
- Useful for audio classification, quality analysis

### vad_segments
Detect speech segments using silence detection.

- Returns: `{ "segments": [{ "start": 0.5, "end": 3.2 }, ...] }`
- Uses FFmpeg silencedetect filter
- Aggressiveness: 1-3 (default: 2)

### transform
Apply transformations to audio files.

- Operations: trim, resample, normalize
- Returns: `{ "file_path": "output.wav" }`

## Requirements

- **ffmpeg:** Required for VAD and transform operations
- **Python 3.8+:** All operations
- **Disk Space:** Whisper models range from 100MB (tiny) to 3GB (large)

## Error Handling

- Returns JSON error object on failure
- Validates all file paths before processing
- Gracefully handles missing dependencies
