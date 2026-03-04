# Usage Examples

## Basic Examples

### 1. Simple Transcription
```bash
python transcribe.py audio.mp3
```
Output:
```
This is the transcribed text from the audio file...
```

### 2. Portuguese Audio
```bash
python transcribe.py podcast.mp3 --language pt
```

### 3. Save to File
```bash
python transcribe.py meeting.mp3 --output meeting.txt
```

## Advanced Examples

### Generate Subtitles (SRT)
```bash
python transcribe.py movie.mp4 --format srt --output movie.srt
```

### Word-Level Timestamps
```bash
python transcribe.py interview.mp3 --format srt --word_timestamps --output interview.srt
```

### High Quality with VAD
```bash
python transcribe.py lecture.mp3 \
    --model large-v3 \
    --vad_filter \
    --language en \
    --format json \
    --output lecture.json
```

### Translate Foreign Language to English
```bash
python transcribe.py french_speech.mp3 --task translate --format txt
```

### CPU-Only Mode (No GPU)
```bash
python transcribe.py audio.mp3 --device cpu --compute_type int8
```

## Python API Examples

### Basic Usage
```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")
segments, info = model.transcribe("audio.mp3", language="pt")

for segment in segments:
    print(f"[{segment.start:.2f}s] {segment.text}")
```

### With Word Timestamps
```python
segments, info = model.transcribe(
    "audio.mp3",
    language="pt",
    word_timestamps=True
)

for segment in segments:
    for word in segment.words:
        print(f"{word.start:.2f}: {word.word}")
```

### Batch Processing
```python
import os
from pathlib import Path

audio_dir = Path("./podcasts")
model = WhisperModel("small", device="cuda")

for audio_file in audio_dir.glob("*.mp3"):
    segments, _ = model.transcribe(str(audio_file), language="pt")
    text = " ".join([seg.text for seg in segments])
    
    output_file = audio_file.with_suffix(".txt")
    output_file.write_text(text, encoding="utf-8")
    print(f"Transcribed: {audio_file} -> {output_file}")
```

## Tips & Tricks

### 1. Faster Processing
- Use smaller models (tiny, base) for quick drafts
- Use larger models (medium, large-v3) for final/published content
- Enable VAD filter to skip silent parts

### 2. Better Accuracy
- Use `--initial_prompt` to guide the model:
  ```bash
  python transcribe.py medical.mp3 --initial_prompt "Medical terminology and patient diagnosis"
  ```

### 3. Boost Specific Words
- Use `--hotwords` for domain-specific terminology:
  ```bash
  python transcribe.py tech.mp3 --hotwords "Kubernetes,Docker,Microservices"
  ```

### 4. Handle Long Files
- The model automatically handles long audio files
- For very long files, consider splitting into chunks

## Common Workflows

### Podcast Workflow
```bash
# 1. Transcribe to SRT
python transcribe.py episode.mp3 --format srt --output episode.srt

# 2. Generate clean text (no timestamps)
python transcribe.py episode.mp3 --output episode.txt
```

### Meeting Notes Workflow
```bash
# Transcribe with high accuracy
python transcribe.py meeting.mp3 \
    --model medium \
    --language pt \
    --vad_filter \
    --output meeting.txt
```

### Video Subtitle Workflow
```bash
# Extract audio first (using ffmpeg)
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# Transcribe to SRT with word timestamps
python transcribe.py audio.aac \
    --format srt \
    --word_timestamps \
    --output video.srt
```