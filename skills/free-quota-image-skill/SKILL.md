---
name: free-quota-image-skill
description: Generate images from text with a free-quota-first multi-provider workflow. Use this skill when a user asks for text-to-image generation that needs provider routing (Hugging Face, Gitee, ModelScope, A4F, OpenAI-compatible private endpoints), token pooling with automatic rotation on quota/auth failures, public API fallback for Hugging Face, prompt optimization, model fallback, batch generation in one command, and structured generation outputs.
metadata: {"openclaw":{"homepage":"https://github.com/Amery2010/peinture"}}
---

# Free Quota Image Skill

## Overview

Use this skill to run a provider-agnostic text-to-image pipeline with free-quota-first routing, token rotation, and prompt enhancement.

## Workflow

1. Load config from `{baseDir}/assets/config.example.yaml` or user-provided config.
2. Resolve provider order (`--provider auto` follows `routing.provider_order`).
3. Resolve model candidates per provider (`requested -> z-image-turbo -> provider default`).
4. Prepare prompt for each attempt:
   - optionally auto-translate for target models
   - optionally optimize prompt with provider text model
5. Execute generation request.
6. On quota/auth failures, rotate token; if exhausted, move to next provider.
7. Repeat the generation flow when `--count > 1`, and rotate provider/token start position per image to spread load.
8. Return stable JSON output fields or direct URL output.

## Commands

Install dependencies:

```bash
python -m pip install -r {baseDir}/scripts/requirements.txt
```

Run generation:

```bash
python {baseDir}/scripts/run_text2img.py --prompt "cinematic rainy tokyo alley" --json
```

Run with explicit provider/model:

```bash
python {baseDir}/scripts/run_text2img.py --prompt "a fox astronaut" --provider gitee --model flux-2 --json
```

Save image locally:

```bash
python {baseDir}/scripts/run_text2img.py --prompt "retro sci-fi city" --output ./out.png
```

Generate multiple images in one run:

```bash
python {baseDir}/scripts/run_text2img.py --prompt "anime passport portrait" --count 4 --json
```

## CLI contract

Use `{baseDir}/scripts/run_text2img.py` with the fixed contract:

- `--prompt` (required)
- `--provider` (`auto|huggingface|gitee|modelscope|a4f|openai_compatible`, default `auto`)
- `--model` (default `z-image-turbo`)
- `--aspect-ratio` (default `1:1`)
- `--seed` (optional int)
- `--steps` (optional int)
- `--guidance-scale` (optional float)
- `--enable-hd` (flag)
- `--optimize-prompt` / `--no-optimize-prompt` (default on)
- `--auto-translate` / `--no-auto-translate` (default off)
- `--config` (default `{baseDir}/assets/config.example.yaml`)
- `--output` (optional output file path)
- `--count` (number of images in one run, default `1`)
- `--json` (structured output)

## Output contract

When `--json` is used, output these fields on success:

- `id`
- `url`
- `provider`
- `model`
- `prompt_original`
- `prompt_final`
- `seed`
- `steps`
- `guidance_scale`
- `aspect_ratio`
- `fallback_chain`
- `elapsed_ms`

On failure, output structured error fields:

- `error_type`
- `error`
- `fallback_chain`

When `--count > 1`, JSON output contains:

- `count`
- `images` (array of standard success payloads)
- `elapsed_ms`

## References

Read only what is needed:

- Provider API wiring: `references/provider-endpoints.md`
- Model coverage and fallback: `references/model-matrix.md`
- Token rotation and date rules: `references/token-rotation-policy.md`
- Prompt optimization pipeline: `references/prompt-optimization-policy.md`
- OpenClaw setup details: `references/openclaw-integration.md`

## Scope boundaries

Keep this skill focused on text-to-image core only.

Do not add image editing, video generation, or cloud storage workflows in this skill.
