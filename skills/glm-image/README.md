# GLM Image Generator

Generate images from text prompts using [GLM-Image](https://open.bigmodel.cn) (Zhipu AI) or [OpenRouter](https://openrouter.ai) image models.

> **Attribution:** Based on [glm-image](https://github.com/ViffyGwaanl/glm-image) by ViffyGwaanl (MIT License).

## Sample

**Multi-agent orchestration — scrapbook style (Chinese)**

Generated with `google/gemini-3-pro-image-preview` via OpenRouter:

![Multi-agent scrapbook illustration](samples/multi-agent-scrapbook-zh.jpg)

## Setup

This skill supports two providers. You only need one.

**Option A — GLM (BigModel / Zhipu AI)**

```bash
export GLM_API_KEY=your-key
```

Get your key at https://open.bigmodel.cn → Console → API Keys

**Option B — OpenRouter**

```bash
export OPENROUTER_API_KEY=your-key
```

Get your key at https://openrouter.ai → Keys

Default model: `google/gemini-3-pro-image-preview`. Override with `--model`.

If both keys are present, GLM is preferred. Override with `--provider openrouter`.

## Usage

```bash
# Auto-detect provider
python3 scripts/generate.py "a sunset over mountains" --language en

# Force OpenRouter with specific model
python3 scripts/generate.py "一只猫在月光下" --language zh --provider openrouter --model openai/gpt-5-image-mini

# Force GLM
python3 scripts/generate.py "a robot playing chess" --language en --provider glm
```

### Options

| Flag | Description |
|------|-------------|
| `--language` | **Required.** `zh` `en` `ja` `ko` `fr` `de` `es` |
| `--provider` | `glm` or `openrouter` (auto-detected if omitted) |
| `--model` | OpenRouter model slug (ignored for GLM) |
| `--size` | Image dimensions, GLM only (default: 1088x1920) |
| `--quality` | `hd` or `standard`, GLM only (default: hd) |
| `--output` | Output directory (default: `output/`) |
| `--watermark` | Enable watermark, GLM only |

## Output

Images saved to `output/` with timestamped filenames. Cost displayed after generation.

## Requirements

- Python 3
- `requests` library (`pip install requests`)
