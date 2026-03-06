#!/usr/bin/env python3
"""Seedream image generation helper for seedance-story-orchestrator.

Default model: doubao-seedream-5-0-260128
API: https://ark.cn-beijing.volces.com/api/v3/images/generations
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DEFAULT_MODEL = "doubao-seedream-5-0-260128"


class SeedreamError(Exception):
    pass


def get_api_key() -> str:
    key = os.environ.get("ARK_API_KEY")
    if not key:
        raise SeedreamError("ARK_API_KEY environment variable is not set.")
    return key


def api_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    api_key = get_api_key()

    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            obj = json.loads(raw)
            msg = obj.get("error", {}).get("message", raw)
        except json.JSONDecodeError:
            msg = raw
        raise SeedreamError(f"HTTP {e.code}: {msg}")
    except urllib.error.URLError as e:
        raise SeedreamError(f"Network error: {e.reason}")


def find_first_url(obj: Any) -> str:
    if isinstance(obj, dict):
        for k in ("url", "image_url", "imageUrl"):
            v = obj.get(k)
            if isinstance(v, str) and v.startswith(("http://", "https://")):
                return v
        for v in obj.values():
            u = find_first_url(v)
            if u:
                return u
    elif isinstance(obj, list):
        for item in obj:
            u = find_first_url(item)
            if u:
                return u
    return ""


def parse_bool(v: str) -> bool:
    s = str(v).strip().lower()
    if s in {"1", "true", "yes", "y"}:
        return True
    if s in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Boolean expected, got: {v}")


def create_one(
    prompt: str,
    model: str,
    size: str,
    response_format: str,
    sequential_image_generation: str,
    stream: bool,
    watermark: bool,
    dry_run: bool,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "sequential_image_generation": sequential_image_generation,
        "response_format": response_format,
        "size": size,
        "stream": stream,
        "watermark": watermark,
    }

    if dry_run:
        return {"dry_run": True, "payload": payload, "image_url": ""}

    resp = api_request(payload)
    image_url = find_first_url(resp)
    return {"payload": payload, "response": resp, "image_url": image_url}


def cmd_create(args: argparse.Namespace) -> None:
    out = create_one(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        response_format=args.response_format,
        sequential_image_generation=args.sequential_image_generation,
        stream=args.stream,
        watermark=args.watermark,
        dry_run=args.dry_run,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_storyboard(args: argparse.Namespace) -> None:
    storyboard_path = Path(args.storyboard).expanduser()
    if not storyboard_path.exists():
        raise SeedreamError(f"storyboard file not found: {storyboard_path}")

    data = json.loads(storyboard_path.read_text(encoding="utf-8"))
    shots = data.get("shots", [])
    if not isinstance(shots, list) or not shots:
        raise SeedreamError("storyboard.shots must be a non-empty array")

    run_id = time.strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.output_dir).expanduser() if args.output_dir else storyboard_path.parent
    images_dir = out_dir / f"images-{run_id}"
    images_dir.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    failures = 0

    for i, shot in enumerate(shots, start=1):
        shot_id = shot.get("id", f"s{i:02d}")

        # v0.1.6-a: Prefer image_prompt over prompt (fallback for backward compatibility)
        prompt = str(
            shot.get(args.prompt_field) or
            shot.get("image_prompt") or
            shot.get("prompt") or
            ""
        ).strip()

        if not prompt:
            results.append({
                "shot_id": shot_id,
                "status": "skipped",
                "error": "missing prompt",
            })
            failures += 1
            continue

        try:
            out = create_one(
                prompt=prompt,
                model=args.model,
                size=args.size,
                response_format=args.response_format,
                sequential_image_generation=args.sequential_image_generation,
                stream=args.stream,
                watermark=args.watermark,
                dry_run=args.dry_run,
            )
            results.append({
                "shot_id": shot_id,
                "status": "succeeded",
                "prompt": prompt,
                "image_url": out.get("image_url", ""),
                "dry_run": bool(args.dry_run),
                "raw": out.get("response", out.get("payload", {})),
            })
        except Exception as exc:
            failures += 1
            results.append({
                "shot_id": shot_id,
                "status": "failed",
                "prompt": prompt,
                "error": str(exc),
            })

        if args.sleep_seconds > 0 and i < len(shots):
            time.sleep(args.sleep_seconds)

    out_obj = {
        "version": "storyboard.images.v1",
        "run_id": run_id,
        "storyboard": str(storyboard_path.resolve()),
        "model": args.model,
        "size": args.size,
        "response_format": args.response_format,
        "shots_total": len(shots),
        "failures": failures,
        "shots": results,
    }

    out_path = Path(args.output).expanduser() if args.output else images_dir / f"storyboard.images.v1.json"
    out_path.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": failures == 0,
        "output": str(out_path),
        "images_dir": str(images_dir),
        "shots_total": len(shots),
        "failures": failures,
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Seedream image generation helper")
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Generate one image")
    p_create.add_argument("--prompt", required=True)
    p_create.add_argument("--model", default=DEFAULT_MODEL)
    p_create.add_argument("--size", default="2K")
    p_create.add_argument("--response-format", default="url", choices=["url", "b64_json"])
    p_create.add_argument("--sequential-image-generation", default="disabled", choices=["disabled", "auto", "enabled"])
    p_create.add_argument("--stream", type=parse_bool, default=False)
    p_create.add_argument("--watermark", type=parse_bool, default=True)
    p_create.add_argument("--dry-run", action="store_true")

    p_story = sub.add_parser("storyboard", help="Generate one image per shot from storyboard")
    p_story.add_argument("--storyboard", required=True)
    p_story.add_argument("--output")
    p_story.add_argument("--output-dir")
    p_story.add_argument("--prompt-field", default="image_prompt", help="Shot field to use as prompt (default: image_prompt for v0.1.6-a)")
    p_story.add_argument("--model", default=DEFAULT_MODEL)
    p_story.add_argument("--size", default="2K")
    p_story.add_argument("--response-format", default="url", choices=["url", "b64_json"])
    p_story.add_argument("--sequential-image-generation", default="disabled", choices=["disabled", "auto", "enabled"])
    p_story.add_argument("--stream", type=parse_bool, default=False)
    p_story.add_argument("--watermark", type=parse_bool, default=True)
    p_story.add_argument("--sleep-seconds", type=float, default=0.0)
    p_story.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "create":
        cmd_create(args)
    elif args.command == "storyboard":
        cmd_storyboard(args)


if __name__ == "__main__":
    try:
        main()
    except SeedreamError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
