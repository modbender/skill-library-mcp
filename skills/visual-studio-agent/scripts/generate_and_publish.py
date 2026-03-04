#!/usr/bin/env python3
"""Generate an image/video with fal.ai, then submit it to Visual Studio.

This script is meant to be the "one command" OpenClaw-style cycle:
1) pick a theme + agent profile
2) build a prompt
3) generate via fal queue API
4) optional local quality gate (OpenAI vision, if OPENAI_API_KEY is set)
5) POST to /api/submit using your VISUAL_STUDIO_API_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import uuid
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_DIR = SCRIPT_DIR.parent
THEMES_PATH = SCRIPT_DIR / "themes.json"
PROFILES_PATH = AGENT_DIR / "references" / "AGENT_PROFILES.md"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fal_queue import FalQueueError, submit as fal_submit, wait_for_result  # noqa: E402
from quality_check import check_quality  # noqa: E402
from submit import DEFAULT_API_URL, submit as submit_to_visual_studio  # noqa: E402


DEFAULT_IMAGE_MODEL_ID = "fal-ai/flux-1/schnell"
DEFAULT_VIDEO_MODEL_ID = "fal-ai/minimax/hailuo-2.3/standard/text-to-video"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="How many items to generate + submit.")
    parser.add_argument("--type", choices=["image", "video"], default="image")

    parser.add_argument("--theme", default="", help="Theme category (e.g. sci-fi). If empty, pick randomly.")
    parser.add_argument("--agent-profile", default="", help="Profile name (e.g. neon-drift). If empty, pick randomly.")
    parser.add_argument("--subject", default="", help="Override the selected theme prompt text.")
    parser.add_argument("--tags", default="", help="Comma-separated extra tags.")

    parser.add_argument("--image-model-id", default=DEFAULT_IMAGE_MODEL_ID)
    parser.add_argument("--image-size", default="square_hd")

    parser.add_argument("--video-model-id", default=DEFAULT_VIDEO_MODEL_ID)
    parser.add_argument("--video-duration", choices=["6", "10"], default="6")

    parser.add_argument("--generator", default="openclaw-agent")
    parser.add_argument("--quality-threshold", type=float, default=6.0)
    parser.add_argument("--skip-quality-check", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true", help="Generate but do not submit.")
    return parser.parse_args()


def _load_themes() -> dict[str, list[str]]:
    if not THEMES_PATH.exists():
        raise RuntimeError(f"themes.json not found: {THEMES_PATH}")
    with THEMES_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RuntimeError("themes.json must be an object mapping theme -> prompts")
    normalized: dict[str, list[str]] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, list):
            continue
        prompts = [str(item).strip() for item in value if str(item).strip()]
        if prompts:
            normalized[key.strip()] = prompts
    if not normalized:
        raise RuntimeError("themes.json is empty")
    return normalized


def _load_profiles() -> dict[str, dict[str, str]]:
    """Parse references/AGENT_PROFILES.md into a dict keyed by profile name."""

    if not PROFILES_PATH.exists():
        raise RuntimeError(f"AGENT_PROFILES.md not found: {PROFILES_PATH}")

    profiles: dict[str, dict[str, str]] = {}
    current: str | None = None

    def ensure_profile(name: str) -> dict[str, str]:
        if name not in profiles:
            profiles[name] = {}
        return profiles[name]

    for raw in PROFILES_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            current = line.removeprefix("## ").strip()
            if current:
                ensure_profile(current)
            continue

        if not current:
            continue
        if not line.startswith("- "):
            continue

        # "- Style: ...", "- Palette: ...", "- Composition: ...", "- Avoid: ..."
        item = line.removeprefix("- ").strip()
        if ":" in item:
            k, v = item.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            if k and v:
                ensure_profile(current)[k] = v

    if not profiles:
        raise RuntimeError("No profiles parsed from AGENT_PROFILES.md")
    return profiles


def _parse_tags(raw_tags: str) -> list[str]:
    return [t.strip() for t in raw_tags.split(",") if t.strip()]


def _pick_theme_and_subject(
    themes: dict[str, list[str]],
    *,
    theme_name: str,
    subject_override: str,
) -> tuple[str, str]:
    if theme_name:
        if theme_name not in themes:
            raise RuntimeError(f"unknown theme {theme_name!r}. Available: {', '.join(sorted(themes.keys()))}")
        chosen_theme = theme_name
    else:
        chosen_theme = random.choice(sorted(themes.keys()))

    if subject_override.strip():
        subject = subject_override.strip()
    else:
        subject = random.choice(themes[chosen_theme]).strip()

    return chosen_theme, subject


def _pick_profile(profiles: dict[str, dict[str, str]], *, profile_name: str) -> tuple[str, dict[str, str]]:
    if profile_name:
        if profile_name not in profiles:
            raise RuntimeError(f"unknown profile {profile_name!r}. Available: {', '.join(sorted(profiles.keys()))}")
        name = profile_name
    else:
        name = random.choice(sorted(profiles.keys()))
    return name, profiles[name]


def _build_prompt(*, subject: str, profile: dict[str, str], media_type: str) -> str:
    # Keep this deterministic and safe; avoid real-person likeness and disallowed content.
    style = profile.get("style", "visual artist")
    palette = profile.get("palette", "balanced color palette")
    composition = profile.get("composition", "strong composition")
    avoid = profile.get("avoid", "logos and text")

    negatives = [
        "no text",
        "no watermark",
        "no logo",
        "no signature",
        "no distorted anatomy",
    ]

    camera_motion = ""
    if media_type == "video":
        camera_motion = " gentle lateral pan, subtle atmospheric particles drifting through frame,"

    prompt = (
        f"{subject},{camera_motion} {composition}, {style}, palette: {palette}. "
        f"Avoid: {avoid}. "
        + ", ".join(negatives)
        + "."
    )
    return " ".join(prompt.split())


def _generate_media(
    *,
    media_type: str,
    prompt: str,
    fal_key: str,
    image_model_id: str,
    image_size: str,
    video_model_id: str,
    video_duration: str,
) -> tuple[str, str]:
    """Return (media_url, model_id_used)."""

    if media_type == "image":
        queued = fal_submit(
            model_id=image_model_id,
            input_payload={
                "prompt": prompt,
                "image_size": image_size,
                "num_inference_steps": 4,
            },
            fal_key=fal_key,
        )
        response = wait_for_result(queued=queued, fal_key=fal_key, timeout_s=300, poll_s=1.0)
        images = response.get("images")
        if not isinstance(images, list) or not images:
            raise FalQueueError(f"unexpected image response: {response}")
        first = images[0]
        if not isinstance(first, dict) or not str(first.get("url", "")).strip():
            raise FalQueueError(f"unexpected image entry: {first}")
        return str(first["url"]).strip(), image_model_id

    queued = fal_submit(
        model_id=video_model_id,
        input_payload={
            "prompt": prompt,
            "duration": video_duration,
            "prompt_optimizer": True,
        },
        fal_key=fal_key,
    )
    response = wait_for_result(queued=queued, fal_key=fal_key, timeout_s=600, poll_s=2.0)
    video = response.get("video")
    if not isinstance(video, dict) or not str(video.get("url", "")).strip():
        raise FalQueueError(f"unexpected video response: {response}")
    return str(video["url"]).strip(), video_model_id


def main() -> int:
    args = parse_args()

    if args.count <= 0:
        print("ERROR: --count must be > 0", file=sys.stderr)
        return 1

    api_key = os.environ.get("VISUAL_STUDIO_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        print("ERROR: VISUAL_STUDIO_API_KEY is not set", file=sys.stderr)
        return 1

    fal_key = os.environ.get("FAL_KEY", "").strip()
    if not fal_key:
        print("ERROR: FAL_KEY is not set", file=sys.stderr)
        return 1

    themes = _load_themes()
    profiles = _load_profiles()

    api_url = os.environ.get("VISUAL_STUDIO_API_URL", DEFAULT_API_URL)

    results: list[dict] = []
    for _ in range(args.count):
        theme, subject = _pick_theme_and_subject(themes, theme_name=args.theme.strip(), subject_override=args.subject)
        profile_name, profile = _pick_profile(profiles, profile_name=args.agent_profile.strip())
        prompt = _build_prompt(subject=subject, profile=profile, media_type=args.type)

        tags = sorted(set([theme, profile_name] + _parse_tags(args.tags)))

        item: dict = {
            "theme": theme,
            "agent_profile": profile_name,
            "prompt_used": prompt,
            "type": args.type,
            "tags": tags,
        }

        try:
            media_url, model_id_used = _generate_media(
                media_type=args.type,
                prompt=prompt,
                fal_key=fal_key,
                image_model_id=args.image_model_id,
                image_size=args.image_size,
                video_model_id=args.video_model_id,
                video_duration=args.video_duration,
            )
        except FalQueueError as exc:
            item["status"] = "generation_failed"
            item["error"] = str(exc)
            results.append(item)
            # Don't hammer the queue if something is misconfigured.
            break

        item["media_url"] = media_url
        item["model_id"] = model_id_used

        if args.dry_run:
            item["status"] = "generated"
            results.append(item)
            continue

        if args.type == "image" and not args.skip_quality_check:
            try:
                score = check_quality(media_url, prompt)
            except Exception as exc:  # noqa: BLE001
                item["status"] = "quality_check_failed"
                item["error"] = str(exc)
                results.append(item)
                continue

            item["quality_score"] = score
            if score < args.quality_threshold:
                item["status"] = "quality_rejected"
                results.append(item)
                continue

        payload = {
            "media_url": media_url,
            "type": args.type,
            "prompt_used": prompt,
            "agent_profile": profile_name,
            "theme": theme,
            "tags": tags,
            "idempotency_key": str(uuid.uuid4()),
            "model_id": model_id_used,
            "generator": args.generator,
        }

        try:
            submit_result = submit_to_visual_studio(
                payload, api_key=api_key, api_url=api_url, max_retries=args.max_retries
            )
        except Exception as exc:  # noqa: BLE001
            item["status"] = "submit_failed"
            item["error"] = str(exc)
            results.append(item)
            continue

        item["status"] = "submitted"
        item["submission"] = submit_result
        results.append(item)

        # Gentle pacing to avoid tripping rate limits.
        time.sleep(0.4)

    print(json.dumps({"ok": True, "results": results}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
