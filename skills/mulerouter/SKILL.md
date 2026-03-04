---
name: mulerouter
description: Generates images and videos using MuleRouter or MuleRun multimodal APIs. Text-to-Image, Image-to-Image, Text-to-Video, Image-to-Video, video editing (VACE, keyframe interpolation). Use when the user wants to generate, edit, or transform images and videos using AI models like Wan2.6, Veo3, Nano Banana Pro, Sora2, Midjourney.
compatibility: Requires Python 3.10+, uv, MULEROUTER_API_KEY env var, and one of MULEROUTER_BASE_URL or MULEROUTER_SITE env var. Needs network access to api.mulerouter.ai or api.mulerun.com. The API key is sent in Authorization headers to the configured endpoint.
homepage: https://github.com/mulerouter/mulerouter-skills
allowed-tools: Bash(uv run *) Bash(uv sync *) Read
metadata:
  clawdbot:
    requires:
      env: ["MULEROUTER_API_KEY"]
      env_one_of: ["MULEROUTER_BASE_URL", "MULEROUTER_SITE"]
      bins: ["uv", "python3"]
    primaryEnv: "MULEROUTER_API_KEY"
    install: "uv sync"
    files: ["scripts/*", "models/*", "core/*", "pyproject.toml"]
---

# MuleRouter API

Generate images and videos using MuleRouter or MuleRun multimodal APIs.

## Required Environment Variables

This skill requires the following environment variables to be set before use:

| Variable | Required | Description |
|----------|----------|-------------|
| `MULEROUTER_API_KEY` | **Yes** | API key for authentication ([get one here](https://www.mulerouter.ai/app/api-keys?utm_source=github_claude_plugin)) |
| `MULEROUTER_BASE_URL` | **Yes*** | Custom API base URL (e.g., `https://api.mulerouter.ai`). Takes priority over SITE. |
| `MULEROUTER_SITE` | **Yes*** | API site: `mulerouter` or `mulerun`. Used if BASE_URL is not set. |

*At least one of `MULEROUTER_BASE_URL` or `MULEROUTER_SITE` must be set.

The API key is included in `Authorization: Bearer` headers when making network calls to the configured API endpoint.

**If any of these variables are missing, the scripts will fail with a configuration error.** Check the Configuration section below to set them up.

## Configuration Check

Before running any commands, verify the environment is configured:

### Step 1: Check for existing configuration

Run the built-in config check script:

```bash
uv run python -c "from core.config import load_config; load_config(); print('Configuration OK')"
```

If this prints "Configuration OK", skip to **Step 3**. If it raises a `ValueError`, proceed to Step 2.

### Step 2: Configure if needed

**If the variables above are not set**, ask the user to provide their API key and preferred endpoint.

**Create a `.env` file** in the skill's working directory:

```env
# Option 1: Use custom base URL (takes priority over SITE)
MULEROUTER_BASE_URL=https://api.mulerouter.ai
MULEROUTER_API_KEY=your-api-key

# Option 2: Use site (if BASE_URL not set)
# MULEROUTER_SITE=mulerun
# MULEROUTER_API_KEY=your-api-key
```

**Note:** `MULEROUTER_BASE_URL` takes priority over `MULEROUTER_SITE`. If both are set, `MULEROUTER_BASE_URL` is used.

**Note:** The skill only loads variables prefixed with `MULEROUTER_` from the `.env` file. Other variables in the file are ignored.

**Important:** Do NOT use `export` shell commands to set credentials. Use a `.env` file or ensure the variables are already present in your shell environment before invoking the skill.

### Step 3: Using `uv` to run scripts

The skill uses `uv` for dependency management and execution. Make sure `uv` is installed and available in your PATH.

Run `uv sync` to install dependencies.

## Quick Start

### 1. List available models

```bash
uv run python scripts/list_models.py
```

### 2. Check model parameters

```bash
uv run python models/alibaba/wan2.6-t2v/generation.py --list-params
```

### 3. Generate content

**Text-to-Video:**
```bash
uv run python models/alibaba/wan2.6-t2v/generation.py --prompt "A cat walking through a garden"
```

**Text-to-Image:**
```bash
uv run python models/alibaba/wan2.6-t2i/generation.py --prompt "A serene mountain lake"
```

**Image-to-Video:**
```bash
uv run python models/alibaba/wan2.6-i2v/generation.py --prompt "Gentle zoom in" --image "https://example.com/photo.jpg" #remote image url
```
```bash
uv run python models/alibaba/wan2.6-i2v/generation.py --prompt "Gentle zoom in" --image "/path/to/local/image.png" #local image path
```

## Image Input

For image parameters (`--image`, `--images`, etc.), **prefer local file paths** over base64.

```bash
# Preferred: local file path (auto-converted to base64)
--image /tmp/photo.png

--images ["/tmp/photo.png"]
```

Local file paths are validated before reading: only files with recognized image extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.tif`, `.svg`, `.ico`, `.heic`, `.heif`, `.avif`) are accepted. Paths pointing to sensitive system directories or non-image files are rejected. Valid image files are converted to base64 and sent to the API, avoiding command-line length limits that occur with raw base64 strings.

## Workflow

1. Check configuration: verify `MULEROUTER_API_KEY` and either `MULEROUTER_BASE_URL` or `MULEROUTER_SITE` are set
2. Install dependencies: run `uv sync`
3. Run `uv run python scripts/list_models.py` to discover available models
4. Run `uv run python models/<path>/<action>.py --list-params` to see parameters
5. Execute with appropriate parameters
6. Parse output URLs from results

## Model Selection

When listing models, each model's **tags** (e.g., `[SOTA]`) are displayed by default next to its name. Tags help identify model characteristics at a glance — for example, `SOTA` indicates a state-of-the-art model.

You can also filter models by tag using `--tag`:
```bash
uv run python scripts/list_models.py --tag SOTA
```

**If you are unsure which model to use**, present the available options to the user and let them choose. Use the `AskUserQuestion` tool (or equivalent interactive prompt) to ask the user which model they prefer. For example, if the user asks to "generate an image" without specifying a model, list the relevant image generation models with their tags and descriptions, and ask the user to pick one.

## Tips
1. For an image generation model, a suggested timeout is 5 minutes.
2. For a video generation model, a suggested timeout is 15 minutes.

## References

- [REFERENCE.md](references/REFERENCE.md) - API configuration and CLI options
- [MODELS.md](references/MODELS.md) - Complete model specifications
