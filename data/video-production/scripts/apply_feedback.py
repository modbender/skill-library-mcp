#!/usr/bin/env python3
"""
apply_feedback.py — Re-generate only scenes marked 'revise' in feedback.json

This is the low-token revision loop:
  1. You review preview.html, mark scenes as approve/revise, add notes
  2. Copy feedback JSON, paste to Muffin → Muffin suggests new prompts
  3. Muffin updates storyboard.json with revised prompts
  4. Run this script → only flagged scenes re-generate (others untouched)

Usage:
  python3 scripts/apply_feedback.py --storyboard my_project/storyboard.json --feedback my_project/feedback.json
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_KEY")
if not API_KEY:
    print("✗ GOOGLE_API_KEY not set.")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)
MODEL = "veo-3.1-generate-preview"


def regenerate_clip(scene: dict, output_path: Path) -> bool:
    prompt = scene["prompt"]
    aspect = scene.get("aspect_ratio", "16:9")
    duration = max(4, min(8, scene.get("duration", 5)))

    print(f"\n🔄 Re-generating [{scene['id']}] {scene['label']}")
    print(f"   New prompt: {prompt[:80]}{'…' if len(prompt) > 80 else ''}")

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

            # Backup old clip before overwriting
            if output_path.exists():
                backup = output_path.with_suffix(".prev.mp4")
                output_path.rename(backup)
                print(f"   Backed up old clip → {backup.name}")

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
    parser = argparse.ArgumentParser(description="Re-generate scenes marked for revision")
    parser.add_argument("--storyboard", "-s", required=True, help="Path to storyboard.json")
    parser.add_argument("--feedback", "-f", required=True, help="Path to feedback.json")
    args = parser.parse_args()

    storyboard_path = Path(args.storyboard)
    feedback_path = Path(args.feedback)

    if not storyboard_path.exists():
        print(f"✗ Storyboard not found: {storyboard_path}")
        sys.exit(1)
    if not feedback_path.exists():
        print(f"✗ Feedback file not found: {feedback_path}")
        sys.exit(1)

    with open(storyboard_path) as f:
        sb = json.load(f)
    with open(feedback_path) as f:
        fb = json.load(f)

    project_dir = storyboard_path.parent
    clips_dir = project_dir / sb.get("output_dir", "clips")

    # Index storyboard scenes by ID
    scenes_by_id = {s["id"]: s for s in sb["scenes"]}

    # Find scenes to revise
    to_revise = [s for s in fb["scenes"] if s.get("action") == "revise"]
    approved = [s for s in fb["scenes"] if s.get("action") == "approve"]

    print(f"\n📋 Feedback summary:")
    print(f"   ✓ Approved: {len(approved)}  ↺ To revise: {len(to_revise)}")

    if not to_revise:
        print("\n✅ All scenes approved — nothing to regenerate.")
        print("   Run ffmpeg_assembler.py to build the final video.")
        return

    results = {"regenerated": [], "failed": []}

    for fb_scene in to_revise:
        scene_id = fb_scene["id"]
        notes = fb_scene.get("notes", "")

        if scene_id not in scenes_by_id:
            print(f"✗ Scene '{scene_id}' not found in storyboard — skipping")
            continue

        scene = scenes_by_id[scene_id]
        if notes:
            print(f"\n💬 Notes for [{scene_id}]: {notes}")

        clip_path = clips_dir / f"{scene_id}.mp4"
        success = regenerate_clip(scene, clip_path)

        if success:
            results["regenerated"].append(scene_id)
        else:
            results["failed"].append(scene_id)

        if fb_scene != to_revise[-1]:
            time.sleep(2)

    print(f"\n{'═'*60}")
    print(f"✅ Re-generated: {len(results['regenerated'])}  ✗ Failed: {len(results['failed'])}")
    print(f"\nNext: python3 scripts/generate_preview.py --storyboard {storyboard_path}")


if __name__ == "__main__":
    main()
