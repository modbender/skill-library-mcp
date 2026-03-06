---
name: anthropic
description: "Anthropic Claude API integration — chat completions, streaming, vision, tool use, and batch processing via the Anthropic Messages API. Generate text with Claude Opus, Sonnet, and Haiku models, process images, use tool calling, and manage conversations. Built for AI agents — Python stdlib only, zero dependencies. Use for AI text generation, multimodal analysis, tool-augmented AI, batch processing, and Claude model interaction."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🔮", "requires": {"env": ["ANTHROPIC_API_KEY"]}, "primaryEnv": "ANTHROPIC_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🔮 Anthropic

Anthropic Claude API integration — chat completions, streaming, vision, tool use, and batch processing via the Anthropic Messages API.

## Features

- **Messages API** — Claude Opus, Sonnet, Haiku completions
- **Streaming** — real-time token streaming responses
- **Vision** — image analysis and understanding
- **Tool use** — function calling with structured output
- **System prompts** — custom system instructions
- **Multi-turn conversations** — context management
- **Batch API** — bulk message processing
- **Token counting** — estimate usage before sending
- **Extended thinking** — deep reasoning mode
- **Model listing** — available models and capabilities

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | API key/token for Anthropic |

## Quick Start

```bash
# Send a message to Claude
python3 {baseDir}/scripts/anthropic.py chat "What is the meaning of life?" --model claude-sonnet-4-20250514
```

```bash
# Chat with system prompt
python3 {baseDir}/scripts/anthropic.py chat-system --system "You are a financial analyst" "Analyze AAPL stock"
```

```bash
# Analyze an image
python3 {baseDir}/scripts/anthropic.py chat-image --image photo.jpg 'What do you see in this image?'
```

```bash
# Stream a response
python3 {baseDir}/scripts/anthropic.py stream "Write a short story about a robot" --model claude-sonnet-4-20250514
```



## Commands

### `chat`
Send a message to Claude.
```bash
python3 {baseDir}/scripts/anthropic.py chat "What is the meaning of life?" --model claude-sonnet-4-20250514
```

### `chat-system`
Chat with system prompt.
```bash
python3 {baseDir}/scripts/anthropic.py chat-system --system "You are a financial analyst" "Analyze AAPL stock"
```

### `chat-image`
Analyze an image.
```bash
python3 {baseDir}/scripts/anthropic.py chat-image --image photo.jpg 'What do you see in this image?'
```

### `stream`
Stream a response.
```bash
python3 {baseDir}/scripts/anthropic.py stream "Write a short story about a robot" --model claude-sonnet-4-20250514
```

### `batch-create`
Create a batch request.
```bash
python3 {baseDir}/scripts/anthropic.py batch-create requests.jsonl
```

### `batch-list`
List batch jobs.
```bash
python3 {baseDir}/scripts/anthropic.py batch-list
```

### `batch-get`
Get batch status.
```bash
python3 {baseDir}/scripts/anthropic.py batch-get batch_abc123
```

### `batch-results`
Get batch results.
```bash
python3 {baseDir}/scripts/anthropic.py batch-results batch_abc123
```

### `count-tokens`
Count tokens in a message.
```bash
python3 {baseDir}/scripts/anthropic.py count-tokens "How many tokens is this message?"
```

### `models`
List available models.
```bash
python3 {baseDir}/scripts/anthropic.py models
```

### `tools`
Chat with tool use.
```bash
python3 {baseDir}/scripts/anthropic.py tools --tools '[{"name":"get_weather","description":"Get weather","input_schema":{"type":"object","properties":{"location":{"type":"string"}}}}]' "What is the weather in NYC?"
```

### `thinking`
Extended thinking mode.
```bash
python3 {baseDir}/scripts/anthropic.py thinking "Solve this math problem step by step: what is 123 * 456?" --budget 10000
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/anthropic.py chat --limit 5

# Human-readable
python3 {baseDir}/scripts/anthropic.py chat --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/anthropic.py` | Main CLI — all Anthropic operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Anthropic API and results are returned to stdout. Your data stays on Anthropic servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
