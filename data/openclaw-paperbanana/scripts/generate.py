#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["paperbanana[all-providers]>=0.1.2", "openai>=1.0"]
# ///
"""
PaperBanana diagram generator for OpenClaw.
Wraps the paperbanana Python API to generate publication-quality academic diagrams.
Outputs MEDIA: lines for OpenClaw auto-attachment.

Supports three providers:
  - gemini:     Free tier via GOOGLE_API_KEY
  - openai:     Paid via OPENAI_API_KEY (gpt-5.2 + gpt-image-1.5)
  - openrouter: Paid via OPENROUTER_API_KEY (any model)
"""

import argparse
import asyncio
import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Optional


def detect_provider(explicit: str | None = None) -> str:
    """Auto-detect provider from env vars, or use explicit override. Returns provider name."""
    if explicit:
        key_map = {
            "gemini": "GOOGLE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }
        key = key_map.get(explicit)
        if key and not os.environ.get(key):
            print(f"ERROR: --provider {explicit} requires {key}", file=sys.stderr)
            sys.exit(1)
        return explicit

    # Auto-detect priority: gemini (free) > openai > openrouter
    if os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"

    print("ERROR: No API key found.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Set one of these in ~/.openclaw/openclaw.json → skills.entries.paperbanana.env:", file=sys.stderr)
    print("  GOOGLE_API_KEY=AIza...     (free, recommended)", file=sys.stderr)
    print("  OPENAI_API_KEY=sk-...      (paid, high quality)", file=sys.stderr)
    print("  OPENROUTER_API_KEY=sk-...  (paid, any model)", file=sys.stderr)
    sys.exit(1)


def _make_openai_providers():
    """Create OpenAI VLM + ImageGen providers that implement PaperBanana's interfaces."""
    from PIL import Image as PILImage
    from paperbanana.providers.base import ImageGenProvider, VLMProvider
    from paperbanana.core.utils import image_to_base64
    from openai import AsyncOpenAI
    from tenacity import retry, stop_after_attempt, wait_exponential

    api_key = os.environ["OPENAI_API_KEY"]
    client = AsyncOpenAI(api_key=api_key)

    class OpenAIVLM(VLMProvider):
        """OpenAI VLM provider using the Chat Completions API."""

        @property
        def name(self) -> str:
            return "openai"

        @property
        def model_name(self) -> str:
            return os.environ.get("OPENAI_VLM_MODEL", "gpt-5.2")

        def is_available(self) -> bool:
            return True

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
        async def generate(
            self,
            prompt: str,
            images: Optional[list] = None,
            system_prompt: Optional[str] = None,
            temperature: float = 1.0,
            max_tokens: int = 4096,
            response_format: Optional[str] = None,
        ) -> str:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            content = []
            if images:
                for img in images:
                    b64 = image_to_base64(img)
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    })
            content.append({"type": "text", "text": prompt})
            messages.append({"role": "user", "content": content})

            model = self.model_name
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            # Newer models (gpt-5.x, o-series) use max_completion_tokens
            if any(model.startswith(p) for p in ("gpt-5", "o1", "o3", "o4")):
                kwargs["max_completion_tokens"] = max_tokens
            else:
                kwargs["max_tokens"] = max_tokens
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            resp = await client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content

    class OpenAIImageGen(ImageGenProvider):
        """OpenAI image generation using DALL-E 3 / gpt-image-1."""

        @property
        def name(self) -> str:
            return "openai_imagen"

        @property
        def model_name(self) -> str:
            return os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1.5")

        def is_available(self) -> bool:
            return True

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
        async def generate(
            self,
            prompt: str,
            negative_prompt: Optional[str] = None,
            width: int = 1024,
            height: int = 1024,
            seed: Optional[int] = None,
        ) -> PILImage.Image:
            full_prompt = prompt
            if negative_prompt:
                full_prompt += f"\n\nAvoid: {negative_prompt}"

            model = self.model_name
            kwargs = {
                "model": model,
                "prompt": full_prompt,
                "n": 1,
            }

            if "gpt-image" in model:
                # gpt-image-1 / gpt-image-1.5: 1024x1024, 1024x1536, 1536x1024, auto
                kwargs["quality"] = "high"
                ratio = width / height
                if ratio > 1.2:
                    kwargs["size"] = "1536x1024"
                elif ratio < 0.83:
                    kwargs["size"] = "1024x1536"
                else:
                    kwargs["size"] = "1024x1024"
            else:
                # DALL-E 3: limited sizes
                ratio = width / height
                if ratio > 1.3:
                    kwargs["size"] = "1792x1024"
                elif ratio < 0.77:
                    kwargs["size"] = "1024x1792"
                else:
                    kwargs["size"] = "1024x1024"

            # gpt-image models return b64_json by default
            if "gpt-image" not in model:
                kwargs["response_format"] = "b64_json"

            resp = await client.images.generate(**kwargs)

            # Handle both b64_json and url responses
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


def _get_provider_info(provider: str) -> dict:
    """Get display info for the selected provider."""
    if provider == "gemini":
        return {
            "vlm_model": os.environ.get("GEMINI_VLM_MODEL", "gemini-2.0-flash"),
            "image_model": os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.0-flash-preview-image-generation"),
        }
    elif provider == "openai":
        return {
            "vlm_model": os.environ.get("OPENAI_VLM_MODEL", "gpt-5.2"),
            "image_model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1.5"),
        }
    elif provider == "openrouter":
        return {
            "vlm_model": os.environ.get("OPENROUTER_VLM_MODEL", "google/gemini-2.0-flash-001"),
            "image_model": os.environ.get("OPENROUTER_IMAGE_MODEL", "google/gemini-2.0-flash-001"),
        }
    return {}


def _build_pipeline(provider: str, args):
    """Build the PaperBanana pipeline for the given provider."""
    from paperbanana import PaperBananaPipeline
    from paperbanana.core.config import Settings

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"/tmp/paperbanana-{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_settings = {
        "optimize_inputs": not args.no_optimize,
        "auto_refine": args.auto_refine,
        "refinement_iterations": args.iterations,
        "output_dir": str(output_dir),
        "output_format": args.format,
        "save_iterations": True,
        "save_metadata": True,
    }

    if provider == "openai":
        # Inject custom OpenAI providers directly into the pipeline
        vlm, image_gen = _make_openai_providers()
        settings = Settings(**base_settings)
        return PaperBananaPipeline(settings=settings, vlm_client=vlm, image_gen_fn=image_gen)
    elif provider == "gemini":
        settings = Settings(
            vlm_provider="gemini",
            vlm_model=os.environ.get("GEMINI_VLM_MODEL", "gemini-2.0-flash"),
            image_provider="google_imagen",
            image_model=os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.0-flash-preview-image-generation"),
            **base_settings,
        )
        return PaperBananaPipeline(settings=settings)
    elif provider == "openrouter":
        settings = Settings(
            vlm_provider="openrouter",
            vlm_model=os.environ.get("OPENROUTER_VLM_MODEL", "google/gemini-2.0-flash-001"),
            image_provider="openrouter_imagen",
            image_model=os.environ.get("OPENROUTER_IMAGE_MODEL", "google/gemini-2.0-flash-001"),
            **base_settings,
        )
        return PaperBananaPipeline(settings=settings)
    else:
        print(f"ERROR: Unknown provider '{provider}'", file=sys.stderr)
        sys.exit(1)


async def generate_diagram(args, provider: str) -> str:
    """Run the PaperBanana pipeline and return the output image path."""
    from paperbanana import GenerationInput, DiagramType

    pipeline = _build_pipeline(provider, args)

    # Get source context
    if args.input:
        context = Path(args.input).read_text()
    elif args.context:
        context = args.context
    else:
        print("ERROR: Provide --input (file path) or --context (text string)", file=sys.stderr)
        sys.exit(1)

    gen_input = GenerationInput(
        source_context=context,
        communicative_intent=args.caption,
        diagram_type=DiagramType.METHODOLOGY,
    )

    # Aspect ratio is handled via Settings, not GenerationInput
    # The pipeline uses it when calling the image gen provider

    info = _get_provider_info(provider)
    print(f"🍌 Generating diagram with {provider}...")
    print(f"   VLM: {info['vlm_model']}")
    print(f"   Image: {info['image_model']}")
    print(f"   Optimize: {not args.no_optimize}")
    print(f"   Iterations: {'auto' if args.auto_refine else args.iterations}")
    print()

    result = await pipeline.generate(gen_input)
    return result.image_path


async def continue_run(args, provider: str) -> str:
    """Continue a previous PaperBanana run with feedback."""
    import glob
    from paperbanana.core.resume import load_resume_state

    pipeline = _build_pipeline(provider, args)

    if args.continue_run:
        run_id = args.continue_run
    else:
        runs = sorted(glob.glob("/tmp/paperbanana-*/run_*"))
        if not runs:
            print("ERROR: No previous runs found to continue.", file=sys.stderr)
            sys.exit(1)
        run_dir = runs[-1]
        run_id = Path(run_dir).name

    parent_dir = None
    for d in sorted(glob.glob("/tmp/paperbanana-*"), reverse=True):
        if (Path(d) / run_id).exists() or any(Path(d).iterdir()):
            parent_dir = d
            break

    if not parent_dir:
        print(f"ERROR: Could not find run '{run_id}'", file=sys.stderr)
        sys.exit(1)

    print(f"🍌 Continuing run: {run_id}")
    print(f"   Feedback: {args.feedback}")
    print()

    state = load_resume_state(parent_dir, run_id)
    result = await pipeline.continue_run(
        resume_state=state,
        additional_iterations=args.iterations,
        user_feedback=args.feedback or "",
    )
    return result.image_path


def main():
    parser = argparse.ArgumentParser(description="PaperBanana diagram generator")

    # Input options
    parser.add_argument("--input", "-i", help="Path to methodology text file")
    parser.add_argument("--context", "-c", help="Methodology text (inline string)")
    parser.add_argument("--caption", help="Figure caption / communicative intent")

    # Generation options
    parser.add_argument("--iterations", "-n", type=int, default=3, help="Refinement rounds (default: 3)")
    parser.add_argument("--auto-refine", action="store_true", help="Loop until critic is satisfied")
    parser.add_argument("--aspect", help="Aspect ratio: 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 21:9")
    parser.add_argument("--no-optimize", action="store_true", help="Disable input optimization")
    parser.add_argument("--format", "-f", default="png", choices=["png", "jpeg", "webp"], help="Output format")

    # Provider options
    parser.add_argument("--provider", choices=["gemini", "openai", "openrouter"], help="Override auto-detected provider")

    # Continuation options
    parser.add_argument("--continue", dest="do_continue", action="store_true", help="Continue latest run")
    parser.add_argument("--continue-run", help="Continue specific run by ID")
    parser.add_argument("--feedback", help="User feedback for refinement")

    args = parser.parse_args()

    # Detect provider
    provider = detect_provider(args.provider)

    # Route to generation or continuation
    if args.do_continue or args.continue_run:
        if not args.feedback:
            print("WARNING: No --feedback provided. Continuing with additional iterations only.", file=sys.stderr)
        image_path = asyncio.run(continue_run(args, provider))
    else:
        if not args.caption:
            print("ERROR: --caption is required for new diagram generation.", file=sys.stderr)
            sys.exit(1)
        if not args.input and not args.context:
            print("ERROR: Provide --input (file) or --context (text) for diagram generation.", file=sys.stderr)
            sys.exit(1)
        image_path = asyncio.run(generate_diagram(args, provider))

    # Deliver result
    resolved = str(Path(image_path).resolve())
    print()
    print(f"✅ Diagram saved: {resolved}")
    print(f"MEDIA:{resolved}")


if __name__ == "__main__":
    main()
