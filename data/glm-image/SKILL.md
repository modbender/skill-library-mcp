---
name: glm-image
description: Generate images using GLM-Image API. Use when the user wants to generate, create, or draw an image from a text prompt. Triggers on requests like "generate an image of...", "create a picture of...", "draw...", or any image generation request.
---

# GLM-Image Generator

Generate images from text prompts using the GLM-Image API.

> **Attribution:** Based on [glm-image](https://github.com/ViffyGwaanl/glm-image) by ViffyGwaanl (MIT License).

## Setup

This skill supports two providers. **You only need one.**

### Option A — GLM (BigModel / Zhipu AI)

Requires `GLM_API_KEY` from https://open.bigmodel.cn → Console → API Keys

```bash
export GLM_API_KEY=your-key
# or add to ~/.openclaw/config.json: { "api_key": "your-key" }
# or add GLM_API_KEY=your-key to .env
```

### Option B — OpenRouter

Requires `OPENROUTER_API_KEY` from https://openrouter.ai → Keys

```bash
export OPENROUTER_API_KEY=your-key
# or add to ~/.openclaw/config.json: { "openrouter_api_key": "your-key" }
# or add OPENROUTER_API_KEY=your-key to .env
```

Default OpenRouter model: `google/gemini-3-pro-image-preview`. Other options: `openai/gpt-5-image-mini`, `openai/gpt-5-image`, `google/gemini-2.5-flash-image-preview`.
See full list at https://openrouter.ai/collections/image-models

**Auto-detection:** if both keys are present, GLM is used. Override with `--provider openrouter`.

## Usage

When a user requests image generation:

**Step 0 — Verify at least one API key is configured**

Run:

```bash
python3 -c "
import os, json, pathlib
glm = bool(os.environ.get('GLM_API_KEY'))
orouter = bool(os.environ.get('OPENROUTER_API_KEY'))
if not glm and not orouter:
    for p in ['~/.openclaw/config.json', '~/.claude/config.json']:
        try:
            d = json.loads(pathlib.Path(p).expanduser().read_text())
            if d.get('api_key'): glm = True
            if d.get('openrouter_api_key'): orouter = True
        except: pass
keys = []
if glm: keys.append('GLM_API_KEY')
if orouter: keys.append('OPENROUTER_API_KEY')
print('FOUND: ' + ', '.join(keys) if keys else 'KEY_MISSING')
"
```

If output is `KEY_MISSING`, tell the user:

> "No API key is configured. This skill supports two providers — you only need one:
>
> **Option A — GLM (BigModel):** Get key at https://open.bigmodel.cn → Console → API Keys, then:
> ```
> export GLM_API_KEY=your-key
> ```
>
> **Option B — OpenRouter:** Get key at https://openrouter.ai → Keys, then:
> ```
> export OPENROUTER_API_KEY=your-key
> ```
>
> For either option you can also add the key to `~/.openclaw/config.json`:
> ```json
> { "api_key": "glm-key" }
> { "openrouter_api_key": "openrouter-key" }
> ```"

Do not proceed until the user confirms a key is set.

**Step 1 — Ask for language (MANDATORY, no exceptions)**

Before running anything, ask:

> "What language is your prompt in? Please choose: zh (Chinese), en (English), ja (Japanese), ko (Korean), fr (French), de (German), es (Spanish)."

Do NOT infer language from the user's message language or any other signal. Do NOT default to any language. Do NOT proceed until the user explicitly states a language code.

**Step 2 — Run the generation script**

```bash
python3 scripts/generate.py "<prompt>" --language <code>
```

`--language` is required. The script will error if omitted.

Other defaults:

- Size: 1088x1920 (portrait HD)
- Output: `output/` folder
- No watermark

**Step 3 — Return the result**

Display the markdown image link and local file path.

## Generate Image

```bash
python3 scripts/generate.py "<prompt>" --language <zh|en|ja|ko|fr|de|es>
```

Provider is auto-detected from available keys. Override explicitly:

```bash
# Force OpenRouter with a specific model
python3 scripts/generate.py "<prompt>" --language en --provider openrouter --model google/gemini-2.5-flash-image-preview

# Force GLM
python3 scripts/generate.py "<prompt>" --language zh --provider glm
```

### Options

- `--language`: **(Required)** Prompt language. Must be explicitly provided by the user. Supported: `zh` (Chinese), `en` (English), `ja` (Japanese), `ko` (Korean), `fr` (French), `de` (German), `es` (Spanish)
- `--provider`: `glm` or `openrouter`. Auto-detected if omitted (GLM preferred when both keys present)
- `--model`: OpenRouter model slug (default: `google/gemini-3-pro-image-preview`). Ignored for GLM. See https://openrouter.ai/collections/image-models
- `--size`: Image dimensions, GLM only (default: 1088x1920). Valid range: 512-2048px, multiples of 32
- `--output`: Output directory (default: output/)
- `--quality`: Image quality, GLM only — "hd" or "standard" (default: hd)
- `--watermark`: Enable watermark, GLM only

### Language Selection Rules

- **Always ask explicitly.** Never guess from the user's message language.
- **Never default.** If the user does not specify, ask again.
- **Record as-typed.** Pass exactly what the user said (e.g., `zh`, `en`) — do not normalize.
- Reason: GLM is a Chinese-native model; prompt language significantly affects output quality and style.

### Available Sizes

- 1088x1920 (default, portrait HD)
- 1920x1088 (landscape HD)
- 1280x1280 (square)
- 1568x1056, 1056x1568
- 1472x1088, 1088x1472
- 1728x960, 960x1728

## Output Format

After successful generation, display:

1. Local file path: `output/<timestamp>_<prompt>.png`
2. Markdown image link: `![<prompt>](<url>)`

## Agent Owner

This skill is executed by the main OpenClaw agent session. The `generate.py` script
runs as a shell command via the exec tool. No sub-agents are spawned.

## Success Criteria

Image generation succeeds when:
1. Script exits with code 0
2. Image file saved to output/ directory
3. Markdown image link displayed to user

Failure conditions: invalid API key, unsupported size, network timeout (120s), API quota exceeded.

## Edge Cases

- Invalid size: must be 512-2048px in multiples of 32 — script will fail with API error
- Long prompts: prompt truncated to 30 chars in filename (full prompt used for generation)
- Network timeout: 120s API timeout, 60s download timeout — retry once if timeout
- Missing API key: script exits with clear error message listing search locations
- Chinese characters in prompt: supported, filename sanitized automatically

## Requirements

- GLM API key configured (see Setup section above)
- Python 3 with `requests` package (`pip install requests`)
