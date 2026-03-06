#!/usr/bin/env python3
"""Analyze videos from URLs with Google Gemini models."""

from __future__ import annotations

import argparse
import os
import sys

DEFAULT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_PROMPT = (
    "Summarize this video and provide key moments with approximate timestamps."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a public video URL with Gemini."
    )
    parser.add_argument("--video-url", required=True, help="Public video URL to analyze.")
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Instruction to guide the analysis.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model name (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key. If omitted, GEMINI_API_KEY or GOOGLE_API_KEY is used.",
    )
    return parser.parse_args()


def resolve_api_key(cli_api_key: str | None) -> str:
    api_key = cli_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY, or pass --api-key."
        )
    return api_key


def import_google_genai():
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'google-genai'. Install it with: pip install google-genai"
        ) from exc
    return genai, types


def main() -> int:
    args = parse_args()

    try:
        api_key = resolve_api_key(args.api_key)
        genai, types = import_google_genai()
        client = genai.Client(api_key=api_key)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        contents = types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=args.video_url)),
                types.Part(text=args.prompt),
            ]
        )
        response = client.models.generate_content(model=args.model, contents=contents)
        print((response.text or "").strip())

        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
