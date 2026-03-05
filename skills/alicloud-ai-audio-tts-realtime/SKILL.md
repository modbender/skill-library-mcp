---
name: alicloud-ai-audio-tts-realtime
description: Real-time speech synthesis with Alibaba Cloud Model Studio Qwen TTS Realtime models. Use when low-latency interactive speech is required, including instruction-controlled realtime synthesis.
---

Category: provider

# Model Studio Qwen TTS Realtime

Use realtime TTS models for low-latency streaming speech output.

## Critical model names

Use one of these exact model strings:
- `qwen3-tts-flash-realtime`
- `qwen3-tts-instruct-flash-realtime`
- `qwen3-tts-instruct-flash-realtime-2026-01-22`

## Prerequisites

- Install SDK in a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install dashscope
```
- Set `DASHSCOPE_API_KEY` in your environment, or add `dashscope_api_key` to `~/.alibabacloud/credentials`.

## Normalized interface (tts.realtime)

### Request
- `text` (string, required)
- `voice` (string, required)
- `instruction` (string, optional)
- `sample_rate` (int, optional)

### Response
- `audio_base64_pcm_chunks` (array<string>)
- `sample_rate` (int)
- `finish_reason` (string)

## Operational guidance

- Use websocket or streaming endpoint for realtime mode.
- Keep each utterance short for lower latency.
- For instruction models, keep instruction explicit and concise.
- Some SDK/runtime combinations may reject realtime model calls over `MultiModalConversation`; use the probe script below to verify compatibility.

## Local demo script

Use the probe script to verify realtime compatibility in your current SDK/runtime, and optionally fallback to a non-realtime model for immediate output:

```bash
.venv/bin/python skills/ai/audio/alicloud-ai-audio-tts-realtime/scripts/realtime_tts_demo.py \
  --text "这是一个 realtime 语音演示。" \
  --fallback \
  --output output/ai-audio-tts-realtime/audio/fallback-demo.wav
```

Strict mode (for CI / gating):

```bash
.venv/bin/python skills/ai/audio/alicloud-ai-audio-tts-realtime/scripts/realtime_tts_demo.py \
  --text "realtime health check" \
  --strict
```

## Output location

- Default output: `output/ai-audio-tts-realtime/audio/`
- Override base dir with `OUTPUT_DIR`.

## References

- `references/sources.md`
