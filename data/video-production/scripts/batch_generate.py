#!/usr/bin/env python3
"""
batch_generate.py — Generate all clips from storyboard.json

Reads storyboard.json, calls Veo 3 for each scene.
Skips scenes that already have a clip (safe to re-run).

Usage:
  python3 scripts/batch_generate.py --storyboard my_project/storyboard.json
  python3 scripts/batch_generate.py --storyboard my_project/storyboard.json --force  # re-generate all
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# ── API setup ─────────────────────────────────────────────────────────────────
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_KEY")
if not API_KEY:
    print("✗ GOOGLE_API_KEY not set. Add to ~/.zshenv and re-run.")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)
MODEL = "veo-3.1-generate-preview"


def generate_clip(scene: dict, output_path: Path) -> bool:
    """Generate a single Veo 3 clip for a scene. Returns True on success."""
    prompt = scene["prompt"]
    aspect = scene.get("aspect_ratio", "16:9")
    duration = scene.get("duration", 5)
    duration = max(4, min(8, duration))  # clamp to Gemini API limits

    print(f"\n{'─'*60}")
    print(f"🎬 [{scene['id']}] {scene['label']}")
    print(f"   Prompt: {prompt[:80]}{'…' if len(prompt) > 80 else ''}")
    print(f"   Aspect: {aspect}  Duration: {duration}s")

    try:
        operation = client.models.generate_videos(
            model=MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect,
                number_of_videos=1,
                negative_prompt="static, frozen, no motion, slideshow, laggy, low quality",
            ),
        )

        print("⏳ Generating", end="", flush=True)
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)
            print(".", end="", flush=True)
        print()

        if operation.response and operation.response.generated_videos:
            video = operation.response.generated_videos[0]
            video_bytes = client.files.download(file=video.video)
            output_path.write_bytes(video_bytes)
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✅ Saved: {output_path.name} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"✗ No video returned: {operation.error}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch generate Veo 3 clips from storyboard")
    parser.add_argument("--storyboard", "-s", required=True, help="Path to storyboard.json")
    parser.add_argument("--force", "-f", action="store_true", help="Re-generate even if clip exists")
    args = parser.parse_args()

    storyboard_path = Path(args.storyboard)
    if not storyboard_path.exists():
        print(f"✗ Storyboard not found: {storyboard_path}")
        sys.exit(1)

    with open(storyboard_path) as f:
        sb = json.load(f)

    project_dir = storyboard_path.parent
    output_dir = project_dir / sb.get("output_dir", "clips")
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = sb["scenes"]
    print(f"\n📋 Project: {sb.get('project', 'untitled')}")
    print(f"   Scenes:  {len(scenes)}")
    print(f"   Output:  {output_dir}")

    results = {"generated": [], "skipped": [], "failed": []}

    for scene in scenes:
        clip_path = output_dir / f"{scene['id']}.mp4"

        if clip_path.exists() and not args.force:
            size_mb = clip_path.stat().st_size / (1024 * 1024)
            print(f"\n⏭  [{scene['id']}] {scene['label']} — already exists ({size_mb:.1f} MB), skipping")
            results["skipped"].append(scene["id"])
            continue

        success = generate_clip(scene, clip_path)
        if success:
            results["generated"].append(scene["id"])
        else:
            results["failed"].append(scene["id"])

        # Brief pause between API calls
        if scene != scenes[-1]:
            time.sleep(2)

    # Summary
    print(f"\n{'═'*60}")
    print(f"✅ Generated: {len(results['generated'])}  ⏭  Skipped: {len(results['skipped'])}  ✗ Failed: {len(results['failed'])}")
    if results["failed"]:
        print(f"   Failed scenes: {', '.join(results['failed'])}")
    print(f"\nNext step: python3 scripts/generate_preview.py --storyboard {storyboard_path}")


if __name__ == "__main__":
    main()
