---
name: voice-transcriber
description: Voice note transcription and archival for OpenClaw agents. Powered by Deepgram Nova-3. Transcribes audio messages, saves both audio files and text transcripts. Perfect for voice-first AI workflows, founder journaling, and meeting notes.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: curl, jq, Deepgram API key
metadata: {"openclaw": {"emoji": "\ud83c\udf99\ufe0f", "requires": {"env": ["DEEPGRAM_API_KEY"], "bins": ["curl", "jq"]}, "primaryEnv": "DEEPGRAM_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# Voice Transcriber 🎙️

Audio transcription via Whisper + voice note journaling.

## When to Use

- Transcribing voice messages or audio files
- Saving voice notes with full transcripts
- Converting speech to text from any audio format

## Usage

### Transcribe audio
```bash
bash {baseDir}/scripts/transcribe.sh /path/to/audio.ogg
bash {baseDir}/scripts/transcribe.sh /path/to/audio.ogg --out /path/to/output.txt
```

### Save voice note with transcript
```bash
python3 {baseDir}/scripts/save_voice_note.py /path/to/audio.ogg "Optional context"
```

## Supported Formats

OGG, MP3, WAV, M4A, FLAC, WEBM

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
