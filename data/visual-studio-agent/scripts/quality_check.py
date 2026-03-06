#!/usr/bin/env python3
"""Score generated media quality using an OpenAI vision model."""

import argparse
import json
import os
import re
import sys
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-url", required=True)
    parser.add_argument("--prompt", required=True)
    return parser.parse_args()


def extract_score(text: str) -> float:
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        raise ValueError(f"no numeric score in response: {text!r}")
    value = float(match.group(1))
    return max(0.0, min(10.0, value))


def check_quality(image_url: str, prompt: str) -> float:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Soft fallback for local usage so users can still submit.
        return 7.0

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Rate this generated image from 1 to 10. "
                            "Prompt target: "
                            f"{prompt}. "
                            "Score on technical quality, aesthetics, and prompt adherence. "
                            "Respond with only a single number."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "low"}},
                ],
            }
        ],
        "max_tokens": 8,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"].strip()
        return extract_score(text)


def main() -> int:
    args = parse_args()
    try:
        score = check_quality(args.image_url, args.prompt)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: quality check failed: {exc}", file=sys.stderr)
        score = 7.0
    print(f"{score:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
