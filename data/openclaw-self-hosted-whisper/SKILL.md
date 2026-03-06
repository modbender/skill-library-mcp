---
name: self-hosted-whisper-api
description: Transcribe audio via the self-hosted Whisper ASR instance running on Kubernetes. Use this skill whenever the user wants to transcribe audio files, convert speech to text, generate subtitles, or translate audio. Triggers on audio transcription, speech-to-text, whisper, voice-to-text, subtitle generation, or audio translation requests.
version: 1.0.0
user-invocable: true
metadata:
  {"openclaw": {"emoji": "🎙️", "requires": {"bins": ["curl"]}}}
---

# Self-Hosted Whisper API (curl)

Transcribe an audio file via the Whisper ASR webservice at `http://whisper-asr.whisper-asr.svc.cluster.local:9000`.

Uses the [onerahmet/openai-whisper-asr-webservice](https://github.com/ahmetoner/whisper-asr-webservice) API (`/asr` endpoint).

## Quick start

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

Defaults:
- Endpoint: `http://whisper-asr.whisper-asr.svc.cluster.local:9000/asr`
- Task: `transcribe`
- Output: `txt`

## Useful flags

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --language en --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language de
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --output srt --out /tmp/subtitles.srt
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --output vtt
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --translate
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --vad-filter --json
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --word-timestamps --json
```

## Notes

- Supported `--output` formats: `txt`, `json`, `vtt`, `srt`, `tsv`
- `--translate` produces an English transcript regardless of source language
- `--vad-filter` enables voice activity detection to skip silent sections
- `--word-timestamps` adds word-level timing (use with `--json`)
- The model is configured on the server side (ASR_MODEL env var), not per request
- Swagger docs available at `http://whisper-asr.whisper-asr.svc.cluster.local:9000/docs`
- No authentication required
