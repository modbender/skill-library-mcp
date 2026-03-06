#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["paperbanana[all-providers]>=0.1.2", "openai>=1.0"]
# ///
"""
PaperBanana statistical plot generator for OpenClaw.
Generates publication-quality plots from CSV/JSON data.
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Optional


def detect_provider(explicit: str | None = None) -> str:
    """Auto-detect provider from env vars."""
    if explicit:
        key_map = {"gemini": "GOOGLE_API_KEY", "openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY"}
        key = key_map.get(explicit)
        if key and not os.environ.get(key):
            print(f"ERROR: --provider {explicit} requires {key}", file=sys.stderr)
            sys.exit(1)
        return explicit

    if os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"

    print("ERROR: No API key found.", file=sys.stderr)
    print("Set GOOGLE_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY", file=sys.stderr)
    sys.exit(1)


def _make_openai_providers():
    """Create OpenAI VLM + ImageGen providers."""
    from PIL import Image as PILImage
    from paperbanana.providers.base import ImageGenProvider, VLMProvider
    from paperbanana.core.utils import image_to_base64
    from openai import AsyncOpenAI
    from tenacity import retry, stop_after_attempt, wait_exponential

    api_key = os.environ["OPENAI_API_KEY"]
    client = AsyncOpenAI(api_key=api_key)

    class OpenAIVLM(VLMProvider):
        @property
        def name(self) -> str:
            return "openai"

        @property
        def model_name(self) -> str:
            return os.environ.get("OPENAI_VLM_MODEL", "gpt-5.2")

        def is_available(self) -> bool:
            return True

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
        async def generate(self, prompt, images=None, system_prompt=None,
                          temperature=1.0, max_tokens=4096, response_format=None):
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            content = []
            if images:
                for img in images:
                    b64 = image_to_base64(img)
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
            content.append({"type": "text", "text": prompt})
            messages.append({"role": "user", "content": content})
            model = self.model_name
            kwargs = {"model": model, "messages": messages, "temperature": temperature}
            if any(model.startswith(p) for p in ("gpt-5", "o1", "o3", "o4")):
                kwargs["max_completion_tokens"] = max_tokens
            else:
                kwargs["max_tokens"] = max_tokens
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
            resp = await client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content

    class OpenAIImageGen(ImageGenProvider):
        @property
        def name(self) -> str:
            return "openai_imagen"

        @property
        def model_name(self) -> str:
            return os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1.5")

        def is_available(self) -> bool:
            return True

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
        async def generate(self, prompt, negative_prompt=None, width=1024, height=1024, seed=None):
            full_prompt = prompt
            if negative_prompt:
                full_prompt += f"\n\nAvoid: {negative_prompt}"
            model = self.model_name
            kwargs = {"model": model, "prompt": full_prompt, "n": 1}
            if "gpt-image" in model:
                kwargs["quality"] = "high"
                ratio = width / height
                if ratio > 1.2:
                    kwargs["size"] = "1536x1024"
                elif ratio < 0.83:
                    kwargs["size"] = "1024x1536"
                else:
                    kwargs["size"] = "1024x1024"
            else:
                ratio = width / height
                if ratio > 1.3:
                    kwargs["size"] = "1792x1024"
                elif ratio < 0.77:
                    kwargs["size"] = "1024x1792"
                else:
                    kwargs["size"] = "1024x1024"
                kwargs["response_format"] = "b64_json"
            resp = await client.images.generate(**kwargs)
            data = resp.data[0]
            if hasattr(data, "b64_json") and data.b64_json:
                image_bytes = base64.b64decode(data.b64_json)
            elif hasattr(data, "url") and data.url:
                import httpx
                async with httpx.AsyncClient() as http:
                    r = await http.get(data.url)
                    image_bytes = r.content
            else:
                raise ValueError("No image data in response")
            return PILImage.open(BytesIO(image_bytes))

    return OpenAIVLM(), OpenAIImageGen()


def _build_pipeline(provider: str, args):
    """Build pipeline for the given provider."""
    from paperbanana import PaperBananaPipeline
    from paperbanana.core.config import Settings

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"/tmp/paperbanana-plot-{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_settings = {
        "optimize_inputs": not args.no_optimize,
        "refinement_iterations": args.iterations,
        "output_dir": str(output_dir),
        "output_format": args.format,
        "save_metadata": True,
    }

    if provider == "openai":
        vlm, image_gen = _make_openai_providers()
        settings = Settings(**base_settings)
        return PaperBananaPipeline(settings=settings, vlm_client=vlm, image_gen_fn=image_gen)
    elif provider == "gemini":
        settings = Settings(vlm_provider="gemini", vlm_model="gemini-2.0-flash",
                          image_provider="google_imagen", image_model="gemini-2.0-flash-preview-image-generation",
                          **base_settings)
        return PaperBananaPipeline(settings=settings)
    elif provider == "openrouter":
        settings = Settings(vlm_provider="openrouter", image_provider="openrouter_imagen", **base_settings)
        return PaperBananaPipeline(settings=settings)
    else:
        print(f"ERROR: Unknown provider '{provider}'", file=sys.stderr)
        sys.exit(1)


async def generate_plot(args, provider: str) -> str:
    """Generate a statistical plot from data."""
    from paperbanana import GenerationInput, DiagramType

    pipeline = _build_pipeline(provider, args)

    if args.data_file:
        data_path = Path(args.data_file)
        if data_path.suffix == ".csv":
            import pandas as pd
            data_json = pd.read_csv(data_path).to_json()
        else:
            data_json = data_path.read_text()
    elif args.data:
        data_json = args.data
    else:
        print("ERROR: Provide --data or --data-file", file=sys.stderr)
        sys.exit(1)

    try:
        json.loads(data_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON data: {e}", file=sys.stderr)
        sys.exit(1)

    gen_input = GenerationInput(
        source_context=data_json,
        communicative_intent=args.intent,
        diagram_type=DiagramType.STATISTICAL_PLOT,
        raw_data=json.loads(data_json),
    )

    print(f"🍌 Generating plot with {provider}...")
    print(f"   Intent: {args.intent}")
    print(f"   Iterations: {args.iterations}")
    print()

    result = await pipeline.generate(gen_input)
    return result.image_path


def main():
    parser = argparse.ArgumentParser(description="PaperBanana plot generator")
    parser.add_argument("--data", "-d", help="JSON data string")
    parser.add_argument("--data-file", help="Path to CSV or JSON data file")
    parser.add_argument("--intent", required=True, help="Description of desired plot")
    parser.add_argument("--iterations", "-n", type=int, default=3, help="Refinement rounds")
    parser.add_argument("--aspect", help="Aspect ratio")
    parser.add_argument("--no-optimize", action="store_true", help="Disable input optimization")
    parser.add_argument("--format", "-f", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--provider", choices=["gemini", "openai", "openrouter"])
    args = parser.parse_args()

    if not args.data and not args.data_file:
        print("ERROR: Provide --data or --data-file", file=sys.stderr)
        sys.exit(1)

    provider = detect_provider(args.provider)
    image_path = asyncio.run(generate_plot(args, provider))

    resolved = str(Path(image_path).resolve())
    print()
    print(f"✅ Plot saved: {resolved}")
    print(f"MEDIA:{resolved}")


if __name__ == "__main__":
    main()
