---
name: whisper-cpp
description: Install and use whisper.cpp (local, free/offline speech-to-text) with OpenClaw. Supports downloading different ggml model sizes (tiny/base/small/medium/large-*) and configuring tools.media.audio to transcribe inbound voice notes without paid provider APIs.
---

# whisper-cpp (Local Whisper STT for OpenClaw)

This skill sets up **local whisper.cpp** STT for inbound Telegram voice notes.

## Dependencies

You need build tools (`git`, `cmake`, compiler toolchain) + `curl` and `ffmpeg` (to decode Telegram OGG/Opus → WAV).

## Install

From this skill directory:

```bash
bash scripts/install_whisper_cpp.sh
bash scripts/download_models.sh
bash scripts/install_wrapper.sh
bash scripts/patch_openclaw_audio.sh
```

Send a Telegram voice note to test.

## Tuning

### Model choice

This setup uses **ggml Whisper models** stored in `~/.cache/whisper`.

Common model names you can download:
- `tiny`, `base`, `small`, `medium`
- `large-v1`, `large-v2`, `large-v3` (bigger/slower, usually more accurate)

By default we download: `base` + `small`.

To download specific models:

```bash
bash scripts/download_models.sh tiny base small
```

For the OpenClaw wrapper, you can select:

```bash
OPENCLAW_WHISPER_MODEL=small openclaw-whisper-stt /path/to/audio
```

- Default language: auto-detect (`OPENCLAW_WHISPER_LANG=auto`)
- Force a language (example):
  ```bash
  OPENCLAW_WHISPER_LANG=en openclaw-whisper-stt /path/to/audio
  ```

Models are stored in: `~/.cache/whisper`.

## Cleanup (optional)

After install (whisper-cli + libs are in `~/.local/`):

```bash
bash scripts/cleanup_build.sh
```

## Troubleshooting

Confirm OpenClaw is using the wrapper:

```bash
which openclaw-whisper-stt
openclaw config get tools.media.audio.models
```

Test the wrapper directly:

```bash
openclaw-whisper-stt /path/to/audio.ogg
OPENCLAW_WHISPER_MODEL=small openclaw-whisper-stt /path/to/audio.ogg
```

Follow gateway logs while sending a Telegram voice note:

```bash
openclaw logs --follow
```

## Files

- Wrapper source: `bin/openclaw-whisper-stt.sh` (linked to `~/.local/bin/openclaw-whisper-stt`)
- OpenClaw config patcher: `scripts/patch_openclaw_audio.sh`
