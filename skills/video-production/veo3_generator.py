#!/usr/bin/env python3
"""
Veo 3 Generator — Generate video clips via Google Gemini API
Uses: google-genai SDK, model veo-3.1-generate-preview

Usage:
  python3 veo3_generator.py --prompt "your prompt"
  python3 veo3_generator.py --prompt "..." --aspect 16:9 --duration 8
  python3 veo3_generator.py --test
"""

import os
import sys
import time
import argparse
from pathlib import Path

# ── API Key ──────────────────────────────────────────────────────────────────
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_KEY")
if not API_KEY:
    print("✗ Error: GOOGLE_API_KEY not set")
    print("  Add to ~/.zshenv: export GOOGLE_API_KEY='AIza...'")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

# ── Output folder ─────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "assets" / "veo_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL = "veo-3.1-generate-preview"


def test_connection():
    """Quick sanity check — list available models."""
    print(f"🔍 Testing connection (API key: {API_KEY[:20]}...)")
    try:
        models = [m.name for m in client.models.list() if "veo" in m.name.lower()]
        if models:
            print(f"✓ Connected. Veo models available: {models}")
        else:
            print("⚠️  Connected but no Veo models found — may need allowlist/billing")
        return True
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False


def generate_video(prompt: str, aspect: str = "16:9", duration: int = 8, filename: str = None) -> Path | None:
    """
    Generate a video clip from a text prompt using Veo 3.1.

    Args:
        prompt:   Scene description with camera direction
        aspect:   "16:9" | "9:16" | "1:1"
        duration: Target duration in seconds (model may vary)
        filename: Output filename (auto-generated if None)

    Returns:
        Path to saved .mp4, or None on failure
    """
    print(f"\n📹 Generating clip…")
    print(f"   Model:  {MODEL}")
    print(f"   Aspect: {aspect}")
    print(f"   Prompt: {prompt[:80]}{'…' if len(prompt) > 80 else ''}")

    try:
        operation = client.models.generate_videos(
            model=MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect,
                number_of_videos=1,
                duration_seconds=duration,
                negative_prompt="static scene, no movement, frozen, still image, slideshow, laggy, stuttering",
            ),
        )

        # Poll until done
        print("⏳ Waiting for generation", end="", flush=True)
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)
            print(".", end="", flush=True)
        print()  # newline

        if operation.response and operation.response.generated_videos:
            video = operation.response.generated_videos[0]

            # Build filename
            if filename is None:
                ts = int(time.time())
                filename = f"veo3_{ts}.mp4"
            filepath = OUTPUT_DIR / filename

            # Download video bytes
            video_bytes = client.files.download(file=video.video)
            filepath.write_bytes(video_bytes)

            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"✅ Saved: {filepath} ({size_mb:.1f} MB)")
            return filepath

        else:
            print(f"✗ Generation failed: {operation.error or 'No videos in response'}")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Veo 3.1 video generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 veo3_generator.py --test
  python3 veo3_generator.py --prompt "Cinematic drone shot of LA at golden hour"
  python3 veo3_generator.py --prompt "..." --aspect 9:16 --out portrait.mp4
        """
    )
    parser.add_argument("--prompt", "-p", help="Scene description")
    parser.add_argument("--aspect", "-a", default="16:9",
                        choices=["16:9", "9:16", "1:1"], help="Aspect ratio (default: 16:9)")
    parser.add_argument("--duration", "-d", type=int, default=8,
                        help="Target duration seconds, 4–8 (Gemini API limit)")
    parser.add_argument("--out", "-o", help="Output filename (default: auto)")
    parser.add_argument("--test", action="store_true", help="Test API connection only")

    args = parser.parse_args()

    if args.test:
        test_connection()
        return

    if not args.prompt:
        parser.error("--prompt is required (or use --test)")

    result = generate_video(
        prompt=args.prompt,
        aspect=args.aspect,
        duration=args.duration,
        filename=args.out,
    )
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
