---
name: qwen3-audio
description: "High-performance audio library for Apple Silicon with text-to-speech (TTS) and speech-to-text (STT)."
version: "0.0.3"
---

# Qwen3-Audio

## Overview

Qwen3-Audio is a high-performance audio processing library optimized for Apple Silicon (M1/M2/M3/M4). It delivers fast, efficient TTS and STT with support for multiple models, languages, and audio formats.

## Prerequisites

- Python 3.10+
- Apple Silicon Mac (M1/M2/M3/M4)

### Environment checks

Before using any capability, verify that all items in `./references/env-check-list.md` are complete.

## Capabilities

### Text to Speech
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" tts --text "hello world" --output "/path_to_save.wav"
```

**Returns (JSON):**
```json
{
  "audio_path": "/path_to_save.wav",
  "duration": 1.234,
  "sample_rate": 24000
}
```

### Voice Cloning
Clone any voice using a reference audio sample. Provide the wav file and its transcript:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" tts --text "hello world" --output "/path_to_save.wav" --ref_audio "sample_audio.wav" --ref_text "This is what my voice sounds like."
```
ref_audio: reference audio to clone
ref_text: transcript of the reference audio

### Use Created Voice (Shortcut)
Use a voice created with `voice create` by its ID:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" tts --text "hello world" --output "/path_to_save.wav" --ref_voice "my-voice-id"
```
This automatically loads `ref_audio` and `ref_text` from the voice profile.

### CustomVoice (Emotion Control)
Use predefined voices with emotion/style instructions:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" tts --text "hello world" --output "/path_to_save.wav" --speaker "Ryan" --language "English" --instruct "Very happy and excited."
```

### VoiceDesign (Create Any Voice)
Create any voice from a text description:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" tts --text "hello world" --output "/path_to_save.wav" --language "English" --instruct "A cheerful young female voice with high pitch and energetic tone."
```

### Automatic Speech Recognition (STT)
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" stt --audio "/sample_audio.wav" --output "/path_to_save.txt" --output-format srt
```
Test audio: https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-ASR-Repo/asr_en.wav
output-format: "txt" | "ass" | "srt" | "all"

**Returns (JSON):**
```json
{
  "text": "transcribed text content",
  "duration": 10.5,
  "sample_rate": 16000,
  "files": ["/path_to_save.txt", "/path_to_save.srt"]
}
```

### Voice Management

Voices are stored in the `voices/` directory at the skill root level. Each voice has its own folder containing:
- `ref_audio.wav` - Reference audio file
- `ref_text.txt` - Reference text transcript
- `ref_instruct.txt` - Voice style description

#### Create a Voice
Create a reusable voice profile using VoiceDesign model. The `--instruct` parameter is required to describe the voice style:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" voice create --text "This is a sample voice reference text." --instruct "A warm, friendly female voice with a professional tone." --language "English"
```
Optional: `--id "my-voice-id"` to specify a custom voice ID.

**Returns (JSON):**
```json
{
  "id": "abc12345",
  "ref_audio": "/path/to/skill/voices/abc12345/ref_audio.wav",
  "ref_text": "This is a sample voice reference text.",
  "instruct": "A warm, friendly female voice with a professional tone.",
  "duration": 3.456,
  "sample_rate": 24000
}
```

#### List Voices
List all created voice profiles:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" voice list
```

**Returns (JSON):**
```json
[
  {
    "id": "abc12345",
    "ref_audio": "/path/to/skill/voices/abc12345/ref_audio.wav",
    "ref_text": "This is a sample voice reference text.",
    "instruct": "A warm, friendly female voice with a professional tone.",
    "duration": 3.456,
    "sample_rate": 24000
  }
]
```

#### Use a Created Voice
After creating a voice, use it for TTS with the `--ref_voice` parameter. The instruct will be automatically loaded:
```bash
uv run --python ".venv/bin/python" "./scripts/mlx-audio.py" tts --text "New text to speak" --output "/output.wav" --ref_voice "abc12345"
```

## Predefined Speakers (CustomVoice)

For `Qwen3-TTS-12Hz-1.7B/0.6B-CustomVoice` models, the supported speakers and their descriptions are listed below. We recommend using each speaker's native language for best quality. Each speaker can still speak any language supported by the model.

| Speaker | Voice Description | Native Language |
| --- | --- | --- |
| Vivian | Bright, slightly edgy young female voice. | Chinese |
| Serena | Warm, gentle young female voice. | Chinese |
| Uncle_Fu | Seasoned male voice with a low, mellow timbre. | Chinese |
| Dylan | Youthful Beijing male voice with a clear, natural timbre. | Chinese (Beijing Dialect) |
| Eric | Lively Chengdu male voice with a slightly husky brightness. | Chinese (Sichuan Dialect) |
| Ryan | Dynamic male voice with strong rhythmic drive. | English |
| Aiden | Sunny American male voice with a clear midrange. | English |
| Ono_Anna | Playful Japanese female voice with a light, nimble timbre. | Japanese |
| Sohee | Warm Korean female voice with rich emotion. | Korean |


### Released Models

| Model | Features | Language Support | Instruction Control |
|---|---|---|---|
| Qwen3-TTS-12Hz-1.7B-VoiceDesign | Performs voice design based on user-provided descriptions. | Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian | ✅ |
| Qwen3-TTS-12Hz-1.7B-CustomVoice | Provides style control over target timbres via user instructions; supports 9 premium timbres covering various combinations of gender, age, language, and dialect. | Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian | ✅ |
| Qwen3-TTS-12Hz-1.7B-Base | Base model capable of 3-second rapid voice clone from user audio input; can be used for fine-tuning (FT) other models. | Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian |  |
