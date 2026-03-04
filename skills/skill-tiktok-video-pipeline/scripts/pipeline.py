#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["moviepy>=2.0"]
# ///
"""
TikTok Video Pipeline v2.0.0 — full orchestrator
Product image → base video (Runway/Veo) → [slowmo] → caption overlay → final MP4
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time


SKILLS_BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
RUNWAY_SCRIPT = os.path.join(SKILLS_BASE, "skill-runway-video-gen", "scripts", "generate_video.py")
OVERLAY_SCRIPT = os.path.join(SKILLS_BASE, "skill-tiktok-ads-video", "scripts", "overlay.py")

PRODUCTS_JSON = os.path.join(os.path.dirname(__file__), "..", "config", "products.json")

DEFAULT_AUDIO = os.environ.get(
    "DEFAULT_AUDIO",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "audio_Hyperfun.mp3"),
)


def load_products():
    with open(PRODUCTS_JSON) as f:
        return json.load(f)


def get_video_duration(path):
    from moviepy import VideoFileClip
    clip = VideoFileClip(path)
    dur = clip.duration
    clip.close()
    return dur


def apply_slowmo(input_path, output_path, factor=0.83):
    """Apply slowmo at fixed factor (e.g. 0.83x = ~12s from 10s base)."""
    from moviepy import VideoFileClip
    from moviepy import vfx
    t0 = time.time()
    print(f"[pipeline] ⏳ Applying slowmo at {factor}x speed factor ...")
    clip = VideoFileClip(input_path)
    slow = clip.with_effects([vfx.MultiplySpeed(factor)])
    slow.write_videofile(output_path, fps=30, logger=None)
    clip.close()
    slow.close()
    print(f"[pipeline] ✅ Slowmo done → {output_path} ({time.time()-t0:.1f}s)")


def apply_stretch(input_path, output_path, target_duration):
    """Stretch video to fill target_duration seconds."""
    from moviepy import VideoFileClip
    from moviepy import vfx
    t0 = time.time()
    print(f"[pipeline] ⏳ Stretching to {target_duration}s ...")
    clip = VideoFileClip(input_path)
    speed = clip.duration / target_duration
    slow = clip.with_effects([vfx.MultiplySpeed(speed)])
    slow.write_videofile(output_path, fps=30, logger=None)
    clip.close()
    slow.close()
    print(f"[pipeline] ✅ Stretch done → {output_path} ({time.time()-t0:.1f}s)")


def run_runway(image, prompt, output, duration=10, ratio="720:1280"):
    t0 = time.time()
    print(f"[pipeline] ⏳ Step 1: Generating video via Runway Gen4 Turbo ...")
    cmd = [
        "uv", "run", RUNWAY_SCRIPT,
        "--image", image,
        "--prompt", prompt,
        "--output", output,
        "--duration", str(duration),
        "--ratio", ratio,
    ]
    result = subprocess.run(cmd, check=True)
    print(f"[pipeline] ✅ Runway done ({time.time()-t0:.1f}s)")
    return result.returncode == 0


def run_veo(image, prompt, output):
    """Try Veo via veo3-video-gen skill. Falls back to Runway on 429."""
    veo_script = os.path.join(SKILLS_BASE, "veo3-video-gen", "scripts", "generate.py")
    if not os.path.exists(veo_script):
        print("[pipeline] Veo script not found, falling back to Runway ...")
        return False
    t0 = time.time()
    print(f"[pipeline] ⏳ Step 1: Generating video via Veo ...")
    cmd = ["uv", "run", veo_script, "--image", image, "--prompt", prompt, "--output", output]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"[pipeline] ✅ Veo done ({time.time()-t0:.1f}s)")
        return True
    print("[pipeline] Veo failed (429 or error) — falling back to Runway ...")
    return False


def run_overlay(video, product, style, output, audio=None):
    t0 = time.time()
    print(f"[pipeline] ⏳ Step 3: Applying caption overlay ({style}) ...")
    cmd = [
        "uv", "run", "--with", "moviepy", "--with", "pillow",
        OVERLAY_SCRIPT,
        "--video", video,
        "--product", product,
        "--style", style,
        "--output", output,
    ]
    if audio:
        cmd += ["--audio", audio]
    subprocess.run(cmd, check=True)
    print(f"[pipeline] ✅ Overlay done → {output} ({time.time()-t0:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="TikTok Video Pipeline v2.0.0 — full end-to-end")
    parser.add_argument("--product", required=True, choices=["rain_cloud", "hydro_bottle", "mini_cam"])
    parser.add_argument("--image", required=True, help="Source product image path")
    parser.add_argument("--output", required=True, help="Final output MP4 path")
    parser.add_argument("--style", default="subtitle_talk", choices=["subtitle_talk", "phrase_slam", "random"])
    parser.add_argument("--engine", default="auto", choices=["runway", "veo", "auto"])
    parser.add_argument("--extend-to", type=float, default=12.0, dest="extend_to",
                        help="Target duration in seconds for auto-stretch (default: 12)")
    parser.add_argument("--prompt", default="", help="Motion description for video generation")
    parser.add_argument("--audio", default=None,
                        help=f"Audio file to mix into overlay (default: $DEFAULT_AUDIO env or bundled Hyperfun)")
    parser.add_argument("--slowmo", action="store_true",
                        help="Apply 0.83x slowmo stretch to fill ~12s before overlay (uses moviepy)")
    args = parser.parse_args()

    # Resolve audio path
    audio_path = args.audio or DEFAULT_AUDIO
    if not os.path.exists(audio_path):
        print(f"[pipeline] ⚠️  Audio file not found: {audio_path} — overlay will run without audio")
        audio_path = None

    products = load_products()
    product = products[args.product]

    pipeline_start = time.time()
    print(f"\n[pipeline] === TikTok Video Pipeline v2.0.0 ===")
    print(f"[pipeline] Product: {product['name']} | Style: {args.style} | Engine: {args.engine}")
    print(f"[pipeline] Slowmo: {'yes (0.83x)' if args.slowmo else 'auto-stretch to ' + str(args.extend_to) + 's'}")
    print(f"[pipeline] Audio: {audio_path or 'none'}\n")

    with tempfile.TemporaryDirectory() as tmp:
        base_video = os.path.join(tmp, "base.mp4")
        processed_video = os.path.join(tmp, "processed.mp4")

        # Step 1 — Generate base video
        prompt = args.prompt or f"product in action, cinematic, smooth motion, {product['name']}"

        if args.engine == "runway":
            run_runway(args.image, prompt, base_video)
        elif args.engine == "veo":
            if not run_veo(args.image, prompt, base_video):
                run_runway(args.image, prompt, base_video)
        else:  # auto
            if not run_veo(args.image, prompt, base_video):
                run_runway(args.image, prompt, base_video)

        if not os.path.exists(base_video):
            print("[pipeline] ERROR: Base video generation failed", file=sys.stderr)
            sys.exit(1)

        # Step 2 — Slowmo / Stretch
        dur = get_video_duration(base_video)
        print(f"[pipeline] Step 2: Base video duration = {dur:.1f}s")

        if args.slowmo:
            apply_slowmo(base_video, processed_video, factor=0.83)
            caption_input = processed_video
        elif args.extend_to > dur:
            apply_stretch(base_video, processed_video, args.extend_to)
            caption_input = processed_video
        else:
            print(f"[pipeline] No stretch needed ({dur:.1f}s >= {args.extend_to}s)")
            caption_input = base_video

        # Step 3 — Caption overlay
        run_overlay(caption_input, args.product, args.style, args.output, audio=audio_path)

    elapsed = time.time() - pipeline_start
    print(f"\n[pipeline] ✅ Final video saved: {args.output} (total: {elapsed:.1f}s)")


if __name__ == "__main__":
    main()
