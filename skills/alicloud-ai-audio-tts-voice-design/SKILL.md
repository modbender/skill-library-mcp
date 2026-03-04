---
name: alicloud-ai-audio-tts-voice-design
description: Voice design workflows with Alibaba Cloud Model Studio Qwen TTS VD models. Use when creating custom synthetic voices from text descriptions and using them for speech synthesis.
---

Category: provider

# Model Studio Qwen TTS Voice Design

Use voice design models to create controllable synthetic voices from natural language descriptions.

## Critical model names

Use one of these exact model strings:
- `qwen3-tts-vd-2026-01-26`
- `qwen3-tts-vd-realtime-2025-12-16`

## Prerequisites

- Install SDK in a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install dashscope
```
- Set `DASHSCOPE_API_KEY` in your environment, or add `dashscope_api_key` to `~/.alibabacloud/credentials`.

## Normalized interface (tts.voice_design)

### Request
- `voice_prompt` (string, required) target voice description
- `text` (string, required)
- `stream` (bool, optional)

### Response
- `audio_url` (string) or streaming PCM chunks
- `voice_id` (string)
- `request_id` (string)

## Operational guidance

- Write voice prompts with tone, pace, emotion, and timbre constraints.
- Build a reusable voice prompt library for product consistency.
- Validate generated voice in short utterances before long scripts.

## Local helper script

Prepare a normalized request JSON and validate response schema:

```bash
.venv/bin/python skills/ai/audio/alicloud-ai-audio-tts-voice-design/scripts/prepare_voice_design_request.py \
  --voice-prompt "A warm female host voice, clear articulation, medium pace" \
  --text "这是音色设计演示"
```

## Output location

- Default output: `output/ai-audio-tts-voice-design/audio/`
- Override base dir with `OUTPUT_DIR`.

## References

- `references/sources.md`
