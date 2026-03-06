#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLM-Image generation script for Claude Code skill.
Generates an image from a text prompt and outputs markdown-formatted result.

Supports two providers:
  - glm       : BigModel / Zhipu AI (requires GLM_API_KEY)
  - openrouter: OpenRouter image models (requires OPENROUTER_API_KEY)

Auto-detects provider from available keys unless --provider is specified.
"""

import os
import sys
import json
import base64
import datetime
import re
import argparse
import requests


SUPPORTED_LANGUAGES = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
}

# Default OpenRouter image model. Override with --model.
# gemini-3-pro: strong image generation with good text rendering
OPENROUTER_DEFAULT_MODEL = "google/gemini-3-pro-image-preview"

# GLM-Image known pricing (source: BigModel API docs, as of Jan 2026)
GLM_PRICE_STANDARD_CNY = 0.10   # ¥ per image
GLM_PRICE_HD_CNY       = 0.20   # ¥ per image (HD quality)
CNY_TO_USD             = 0.138  # approximate; fluctuates


# ---------------------------------------------------------------------------
# Key loaders
# ---------------------------------------------------------------------------

def _load_key_from_env_and_configs(env_var: str, config_key: str) -> str | None:
    """Try env var → config files → .env files. Returns None if not found."""
    value = os.environ.get(env_var)
    if value:
        return value

    config_paths = [
        "config.json",
        os.path.expanduser("~/.openclaw/config.json"),
        os.path.expanduser("~/.claude/config.json"),
    ]
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                    if data.get(config_key):
                        return data[config_key]
            except Exception:
                pass

    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    env_paths = [
        os.path.join(skill_dir, ".env"),
        ".env",
        os.path.expanduser("~/.env"),
    ]
    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f"{env_var}="):
                            val = line.split("=", 1)[1].strip().strip('"')
                            if val:
                                return val
            except Exception:
                pass

    return None


# ---------------------------------------------------------------------------
# Cost helpers
# ---------------------------------------------------------------------------

def fetch_openrouter_cost(generation_id: str, api_key: str) -> float | None:
    """
    Fallback: query OpenRouter's /api/v1/generation endpoint for cost in USD.
    Only used when cost wasn't in the main response's usage field.
    """
    try:
        url = f"https://openrouter.ai/api/v1/generation?id={generation_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", {}).get("total_cost")
    except Exception:
        return None


def glm_cost_str(quality: str) -> str:
    """Return formatted cost string for a GLM image generation."""
    cny = GLM_PRICE_HD_CNY if quality == "hd" else GLM_PRICE_STANDARD_CNY
    usd = cny * CNY_TO_USD
    return f"¥{cny:.2f} (~${usd:.4f}) — verify at https://open.bigmodel.cn/console"


def load_glm_key() -> str:
    key = _load_key_from_env_and_configs("GLM_API_KEY", "api_key")
    if not key:
        raise ValueError(
            "GLM_API_KEY not found.\n"
            "Get your key at https://open.bigmodel.cn → Console → API Keys\n"
            "Then set it via:\n"
            "  export GLM_API_KEY=your-key\n"
            "  or add to ~/.openclaw/config.json: {\"api_key\": \"your-key\"}\n"
            "  or add GLM_API_KEY=your-key to .env"
        )
    return key


def load_openrouter_key() -> str:
    key = _load_key_from_env_and_configs("OPENROUTER_API_KEY", "openrouter_api_key")
    if not key:
        raise ValueError(
            "OPENROUTER_API_KEY not found.\n"
            "Get your key at https://openrouter.ai → Keys\n"
            "Then set it via:\n"
            "  export OPENROUTER_API_KEY=your-key\n"
            "  or add to ~/.openclaw/config.json: {\"openrouter_api_key\": \"your-key\"}\n"
            "  or add OPENROUTER_API_KEY=your-key to .env"
        )
    return key


def detect_provider() -> str:
    """Return 'glm' or 'openrouter' based on which key is available."""
    if _load_key_from_env_and_configs("GLM_API_KEY", "api_key"):
        return "glm"
    if _load_key_from_env_and_configs("OPENROUTER_API_KEY", "openrouter_api_key"):
        return "openrouter"
    raise ValueError(
        "No API key found. Configure one of:\n"
        "  GLM_API_KEY       — from https://open.bigmodel.cn (GLM Image)\n"
        "  OPENROUTER_API_KEY — from https://openrouter.ai  (Gemini, GPT-5 Image, etc.)"
    )


# ---------------------------------------------------------------------------
# GLM provider
# ---------------------------------------------------------------------------

def generate_image_glm(
    prompt: str,
    size: str = "1088x1920",
    quality: str = "hd",
    watermark: bool = False,
    output_dir: str = "output",
) -> dict:
    api_key = load_glm_key()
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = {
        "model": "glm-image",
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "watermark_enabled": str(watermark).lower(),
    }

    response = requests.post(url, headers=headers, json=body, timeout=120)
    response.raise_for_status()
    data = response.json()

    if "data" not in data or not data["data"]:
        raise RuntimeError("No image returned from GLM API")

    image_url = data["data"][0]["url"]

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = re.sub(r'[\\/:*?"<>|]', "", prompt).replace(" ", "_")[:30]
    filename = f"{timestamp}_{safe_prompt}.png"
    filepath = os.path.join(output_dir, filename)

    img_response = requests.get(image_url, timeout=60)
    img_response.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(img_response.content)

    return {"url": image_url, "local_path": filepath, "prompt": prompt, "quality": quality}


# ---------------------------------------------------------------------------
# OpenRouter provider
# ---------------------------------------------------------------------------

def generate_image_openrouter(
    prompt: str,
    model: str = OPENROUTER_DEFAULT_MODEL,
    output_dir: str = "output",
) -> dict:
    api_key = load_openrouter_key()
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # Some models output both text+image, others image-only.
    # "image" modality is always required; include "text" for hybrid models.
    #
    # Margin guard: gpt-5-image-mini and similar models often place content at
    # the very edge of the canvas, causing visible clipping. Appending an explicit
    # instruction to leave inset padding reliably prevents this.
    MARGIN_GUARD = (
        " LAYOUT: Leave comfortable margins on all four sides so nothing is cut off or "
        "near the edge. Prefer a tall vertical layout for long content. The model may "
        "choose appropriate dimensions — vertical orientation is recommended but not mandatory."
    )
    padded_prompt = prompt + MARGIN_GUARD

    body = {
        "model": model,
        "messages": [{"role": "user", "content": padded_prompt}],
        "modalities": ["image", "text"],
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=body, timeout=120)
    response.raise_for_status()
    data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("No choices returned from OpenRouter")

    message = choices[0].get("message", {})
    images = message.get("images")
    if not images:
        raise RuntimeError(
            f"No image in OpenRouter response. Model '{model}' may not support image output.\n"
            f"Try: google/gemini-3-pro-image-preview or openai/gpt-5-image-mini"
        )

    generation_id = data.get("id")
    # Cost is available directly in usage.cost (USD)
    usage_cost = data.get("usage", {}).get("cost")

    image_data_url = images[0]["image_url"]["url"]  # "data:image/png;base64,..."

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = re.sub(r'[\\/:*?"<>|]', "", prompt).replace(" ", "_")[:30]
    filename = f"{timestamp}_{safe_prompt}.png"
    filepath = os.path.join(output_dir, filename)

    _, b64_data = image_data_url.split(",", 1)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64_data))

    return {
        "url": image_data_url,
        "local_path": filepath,
        "prompt": prompt,
        "generation_id": generation_id,
        "usage_cost": usage_cost,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate image from prompt")
    parser.add_argument("prompt", help="Image description")
    parser.add_argument(
        "--language",
        required=True,
        choices=list(SUPPORTED_LANGUAGES.keys()),
        help=(
            "Prompt language (REQUIRED). Supported: "
            + ", ".join(f"{k} ({v})" for k, v in SUPPORTED_LANGUAGES.items())
        ),
    )
    parser.add_argument(
        "--provider",
        choices=["glm", "openrouter"],
        default=None,
        help="API provider. Auto-detected from available keys if not specified.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            f"Model to use (OpenRouter only). Default: {OPENROUTER_DEFAULT_MODEL}. "
            "See https://openrouter.ai/collections/image-models"
        ),
    )
    # GLM-only options
    parser.add_argument("--size", default="1088x1920", help="Image size, GLM only (default: 1088x1920)")
    parser.add_argument("--quality", default="hd", help="Image quality, GLM only (default: hd)")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    parser.add_argument("--watermark", action="store_true", help="Enable watermark, GLM only")

    args = parser.parse_args()

    provider = args.provider or detect_provider()

    try:
        if provider == "glm":
            if args.model:
                print(f"Warning: --model is ignored for provider 'glm' (model is always glm-image)", file=sys.stderr)
            result = generate_image_glm(
                prompt=args.prompt,
                size=args.size,
                quality=args.quality,
                watermark=args.watermark,
                output_dir=args.output,
            )
        else:  # openrouter
            model = args.model or OPENROUTER_DEFAULT_MODEL
            result = generate_image_openrouter(
                prompt=args.prompt,
                model=model,
                output_dir=args.output,
            )

        lang_label = SUPPORTED_LANGUAGES.get(args.language, args.language)
        print(f"Provider: {provider}")
        print(f"Language: {lang_label} ({args.language})")
        print(f"Image saved: {result['local_path']}")
        print(f"\nMarkdown URL:\n![{result['prompt']}]({result['url']})")
        print(f"\nLocal path: {result['local_path']}")

        # Cost reporting
        if provider == "glm":
            print(f"\nCost: {glm_cost_str(result.get('quality', args.quality))}")
        else:
            cost = result.get("usage_cost")
            if cost is None:
                # fallback: query generation endpoint
                gen_id = result.get("generation_id")
                if gen_id:
                    cost = fetch_openrouter_cost(gen_id, load_openrouter_key())
            if cost is not None:
                print(f"\nCost: ${cost:.6f} USD")
            else:
                print(f"\nCost: unavailable — check https://openrouter.ai/activity")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
