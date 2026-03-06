#!/usr/bin/env python3
"""Run quality gate + submission for one generated media item."""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from quality_check import check_quality  # noqa: E402
from submit import DEFAULT_API_URL, submit  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-url", required=True)
    parser.add_argument("--type", choices=["image", "video"], default="image")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--agent-profile", required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--tags", default="")
    parser.add_argument("--idempotency-key", default="")
    parser.add_argument("--model-id", default="")
    parser.add_argument("--generator", default="openclaw-agent")
    parser.add_argument("--quality-threshold", type=float, default=6.0)
    parser.add_argument("--skip-quality-check", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    return parser.parse_args()


def parse_tags(raw_tags: str) -> list[str]:
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("VISUAL_STUDIO_API_KEY")
    if not api_key:
        print("ERROR: VISUAL_STUDIO_API_KEY is not set", file=sys.stderr)
        return 1

    quality_score = None
    quality_passed = True

    if args.type == "image" and not args.skip_quality_check:
        try:
            quality_score = check_quality(args.media_url, args.prompt)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: quality check failed, rejecting submission: {exc}", file=sys.stderr)
            return 2

        if quality_score < args.quality_threshold:
            quality_passed = False
            print(
                f"WARN: quality score {quality_score:.1f} below threshold {args.quality_threshold:.1f}",
                file=sys.stderr,
            )
            return 2

    payload = {
        "media_url": args.media_url,
        "type": args.type,
        "prompt_used": args.prompt,
        "agent_profile": args.agent_profile,
        "theme": args.theme,
        "tags": parse_tags(args.tags),
        "idempotency_key": args.idempotency_key or str(uuid.uuid4()),
        "model_id": args.model_id or None,
        "generator": args.generator,
    }

    api_url = os.environ.get("VISUAL_STUDIO_API_URL", DEFAULT_API_URL)

    try:
        result = submit(payload, api_key=api_key, api_url=api_url, max_retries=args.max_retries)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: submission failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "quality_score": quality_score,
                "quality_passed": quality_passed,
                "submission": result,
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
