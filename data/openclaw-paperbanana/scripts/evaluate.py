#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["paperbanana[all-providers]>=0.1.2", "openai>=1.0"]
# ///
"""
PaperBanana diagram evaluator for OpenClaw.
Compares a generated diagram against a human reference using VLM-as-Judge.
Returns scores on Faithfulness, Readability, Conciseness, and Aesthetics.
"""

import argparse
import asyncio
import os
import sys
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

    print("ERROR: No API key found for evaluation.", file=sys.stderr)
    print("Set GOOGLE_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY", file=sys.stderr)
    sys.exit(1)


def _make_openai_vlm():
    """Create an OpenAI VLM provider for evaluation."""
    from paperbanana.providers.base import VLMProvider
    from paperbanana.core.utils import image_to_base64
    from openai import AsyncOpenAI
    from tenacity import retry, stop_after_attempt, wait_exponential

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

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

    return OpenAIVLM()


async def evaluate_diagram(args, provider: str) -> str:
    """Evaluate a generated diagram against a reference."""
    gen_path = Path(args.generated)
    ref_path = Path(args.reference)

    if not gen_path.exists():
        print(f"ERROR: Generated image not found: {gen_path}", file=sys.stderr)
        sys.exit(1)
    if not ref_path.exists():
        print(f"ERROR: Reference image not found: {ref_path}", file=sys.stderr)
        sys.exit(1)

    if args.context_file:
        context = Path(args.context_file).read_text()
    elif args.context:
        context = args.context
    else:
        print("ERROR: Provide --context (text) or --context-file (path)", file=sys.stderr)
        sys.exit(1)

    print(f"🍌 Evaluating diagram with {provider}...")
    print(f"   Generated: {gen_path}")
    print(f"   Reference: {ref_path}")
    print()

    if provider == "openai":
        # Use custom OpenAI VLM for evaluation
        vlm = _make_openai_vlm()
        from paperbanana.evaluation.judge import VLMJudge
        judge = VLMJudge.__new__(VLMJudge)
        judge._vlm = vlm
        scores = await judge.evaluate(
            generated_path=str(gen_path),
            reference_path=str(ref_path),
            context=context,
            caption=args.caption,
        )
    else:
        from paperbanana.evaluation.judge import VLMJudge
        provider_name = "gemini" if provider == "gemini" else "openrouter"
        model = (os.environ.get("GEMINI_VLM_MODEL", "gemini-2.0-flash") if provider == "gemini"
                 else os.environ.get("OPENROUTER_VLM_MODEL", "google/gemini-2.0-flash-001"))
        judge = VLMJudge(provider=provider_name, model=model)
        scores = await judge.evaluate(
            generated_path=str(gen_path),
            reference_path=str(ref_path),
            context=context,
            caption=args.caption,
        )

    return scores


def main():
    parser = argparse.ArgumentParser(description="PaperBanana diagram evaluator")
    parser.add_argument("--generated", "-g", required=True, help="Path to generated image")
    parser.add_argument("--reference", "-r", required=True, help="Path to human reference image")
    parser.add_argument("--context", help="Source methodology text (inline)")
    parser.add_argument("--context-file", help="Path to source context text file")
    parser.add_argument("--caption", "-c", required=True, help="Figure caption")
    parser.add_argument("--provider", choices=["gemini", "openai", "openrouter"])
    args = parser.parse_args()

    provider = detect_provider(args.provider)
    scores = asyncio.run(evaluate_diagram(args, provider))

    print()
    print("📊 Evaluation Results:")
    print(scores)


if __name__ == "__main__":
    main()
