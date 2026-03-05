---
name: video-audio-replace
description: Replace video audio with TTS voice while preserving original timing. Includes subtitle generation from video using Whisper. Uses ElevenLabs or Edge TTS, aligns each audio segment to original timestamp, adjusts speed (0.85-1.15x), and inserts silence gaps.
metadata:
  tags: video, audio, tts, elevenlabs, whisper, subtitle, voice, replace
---

# Video Audio Replace

Replace a video's original audio with TTS-generated voice while maintaining precise timing alignment. Also supports generating subtitles from video using Whisper.

## Full Workflow

### Step 1: Generate subtitles from video (optional)
If you don't have an SRT file, generate one from the video using the included script:

```bash
# Generate subtitles from video (uses faster-whisper, free, local)
generate_subtitles.py video.mp4 -o subtitles.srt -l zh
```

Or manually with Python:

```bash
# Using faster-whisper (recommended, local, free)
pip install faster-whisper srt

python3 << 'EOF'
from faster_whisper import WhisperModel
import srt
from datetime import timedelta

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("input_video.mp4", language="zh")

# Generate SRT
def format_time(seconds):
    td = timedelta(seconds=seconds)
    return f"{td.seconds//3600:02d}:{(td.seconds%3600)//60:02d}:{td.seconds%60:02d},{td.microseconds//1000:03d}"

srt_content = ""
for i, seg in enumerate(segments, 1):
    start = format_time(seg.start)
    end = format_time(seg.end)
    srt_content += f"{i}\n{start} --> {end}\n{seg.text.strip()}\n\n"

with open("subtitles.srt", "w", encoding="utf-8") as f:
    f.write(srt_content)
EOF
```

### Step 2: Replace audio with TTS
Use the generated SRT to create a new video with TTS voice.

## When to use

- Dubbing videos with AI-generated voice
- Converting subtitle files to voice-over
- Creating multilingual video versions

## Requirements

### API Keys (choose one)
- **ElevenLabs**: Set `ELEVENLABS_API_KEY` environment variable
- **Edge TTS** (free, no key needed): Use `--engine edge`

### System dependencies
- ffmpeg
- sox (optional, for advanced processing)

## Usage

### Basic usage (ElevenLabs)
```bash
video-audio-replace --video input.mp4 --srt subtitles.srt --output output.mp4 --voice "Liam"
```

### Using Edge TTS (free, no API key)
```bash
video-audio-replace --video input.mp4 --srt subtitles.srt --output output.mp4 --engine edge --voice "zh-CN-YunxiNeural"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--video` | Input video file | Required |
| `--srt` | SRT subtitle file | Required |
| `--output` | Output video file | input_tts.mp4 |
| `--voice` | Voice ID or name | Liam (ElevenLabs) |
| `--engine` | TTS engine: elevenlabs, edge | elevenlabs |
| `--speed-range` | Speed adjustment range | 0.85-1.15 |

## Examples

### English voice (ElevenLabs)
```bash
video-audio-replace --video 2028.mp4 --srt 2028.srt --output 2028_final.mp4 --voice "Liam"
```

### Chinese voice (Edge TTS)
```bash
video-audio-replace --video video.mp4 --srt subs.srt --output result.mp4 --engine edge --voice "zh-CN-YunxiNeural"
```

## How it works

1. Extract original audio from video
2. Split audio into segments based on subtitle timestamps
3. Generate TTS audio for each subtitle segment
4. Adjust TTS speed (within 0.85-1.15x) to match original segment duration
5. Add silence padding to fill any remaining time gap
6. Merge all segments preserving original timing gaps
7. Replace video audio with aligned TTS audio

## Available Voices

### ElevenLabs (require API key)
- `Liam` - Energetic male (recommended)
- `Sarah` - Professional female
- `Brian` - Deep resonant male
- Run `curl` with your API key to list all voices

### Edge TTS (free)
- Chinese: `zh-CN-XiaoxiaoNeural`, `zh-CN-YunxiNeural`, `zh-CN-YunyangNeural`
- English: `en-US-JennyNeural`, `en-US-GuyNeural`
- Many more languages available
