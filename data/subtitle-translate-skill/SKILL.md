---
name: subtitle-translator
description: Translate SRT subtitle files using LLM APIs with OpenAI-compatible format. Supports both single-language and bilingual output. Use when you need to translate subtitle files (.srt) from one language to another while preserving timestamps. Processes in batches of 50 sentences with progress logging.
---

# Subtitle Translator

## Overview

Translate SRT subtitle files using LLM APIs. Supports OpenAI-compatible API format with customizable URL, API key, and model selection. Outputs single-language or bilingual subtitles with original timestamps preserved.

## Features

- **Format Support**: SRT subtitles
- **API Compatibility**: OpenAI-compatible endpoints
- **Output Modes**: Single-language or bilingual (translation above original)
- **Batch Processing**: 50 sentences per batch (configurable) with 1-second intervals
- **Progress Tracking**: Detailed logging of task progress and execution
- **Validation**: Ensures sentence count consistency and timestamp preservation

## Quick Start

### Basic Translation

```bash
python3 scripts/translate_srt.py \
  --input video.srt \
  --output video_zh.srt \
  --source-lang en \
  --target-lang zh \
  --api-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4
```

### Bilingual Output

```bash
python3 scripts/translate_srt.py \
  --input video.srt \
  --output video_bilingual.srt \
  --source-lang en \
  --target-lang zh \
  --bilingual \
  --api-url https://api.openai.com/v1 \
  --api-key sk-...
```

### Validate SRT File

```bash
python3 scripts/validate_srt.py input.srt
```

### List Available Models

```bash
python3 scripts/list_models.py \
  --api-url https://api.openai.com/v1 \
  --api-key sk-...
```

## Configuration

### Option 1: Environment Variables (Recommended)

```bash
export SUBTITLE_API_URL="https://api.openai.com/v1"
export SUBTITLE_API_KEY="sk-your-api-key"
export SUBTITLE_MODEL="gpt-4"

python3 scripts/translate_srt.py -i input.srt -o output.srt
```

### Option 2: Command Line Arguments

```bash
python3 scripts/translate_srt.py \
  -i input.srt \
  -o output.srt \
  -u https://api.openai.com/v1 \
  -k sk-your-api-key \
  -m gpt-4
```

### Option 3: Config File (Less Secure)

Create `~/.openclaw/skills/subtitle-translator/config.json`:

```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-your-api-key",
  "model": "gpt-4",
  "batch_size": 50,
  "batch_interval_ms": 1000,
  "output_mode": "single",
  "log_level": "info"
}
```

⚠️ **Security Warning**: Storing API keys in plaintext config files increases risk. Prefer environment variables or command line arguments.

## Security Considerations

1. **API Key Storage**: Use environment variables or secure secret managers instead of plaintext config files
2. **API Endpoint**: Ensure you trust the API URL you provide
3. **Proxy Environment**: The scripts honor `http_proxy`/`https_proxy` environment variables. If your environment uses untrusted proxies, API keys could be captured
4. **Network Traffic**: All subtitle content is sent to the API endpoint. Do not use with sensitive/confidential content unless you control the API

## Workflow

1. **Parse SRT**: Extract index, timecodes, and text
2. **Validate**: Optional validation of input format
3. **Batch Translation**: Send 50 sentences per request (configurable)
4. **Validate**: Ensure output count matches input
5. **Reconstruct**: Combine original timecodes with translations
6. **Output**: Generate SRT file

## Resources

### scripts/

- `translate_srt.py` - Main translation script
- `list_models.py` - List available models from API
- `validate_srt.py` - Validate SRT file format

### references/

- `srt_format.md` - SRT file format specification
