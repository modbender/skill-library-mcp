#!/usr/bin/env python3
"""
Generate a holocube sprite kit using Gemini (nano-banana-pro).
Creates a base character and 7 emote variations, then converts to holocube-ready formats.

Usage:
    python3 generate_sprites.py --output-dir ./sprites [--api-key KEY] [--character DESCRIPTION]

Requires: uv, nano-banana-pro skill installed, GEMINI_API_KEY
"""

import sys
import os
import json
import argparse
import subprocess
import math
from pathlib import Path

NANO_BANANA_SCRIPT = None  # Auto-detected

EMOTES = {
    "neutral": "looking straight ahead with curious round glowing eyes. Default calm expression.",
    "happy": "looking happy and delighted. Upturned crescent-shaped glowing eyes like a big smile. Add warm glow.",
    "thinking": "looking like it is thinking deeply. One eye slightly squinted, the other looking up. Add small floating gears made of light around it.",
    "surprised": "looking surprised and shocked. Eyes wide open, big bright glowing circles. Mouth open in an O shape.",
    "laughing": "laughing hard. Eyes squeezed shut into happy curved lines like XD. Mouth wide open laughing. Head slightly tilted.",
    "sleeping": "sleeping peacefully. Eyes closed as gentle curved lines. Small Z Z Z letters floating up made of dim light. Much dimmer overall glow.",
}

DEFAULT_CHARACTER = (
    "A glowing holographic robot head floating in pure black void. "
    "Cyan and blue neon wireframe style. Luminous eyes. "
    "Ethereal digital particles dissolving around it. "
    "No background elements, just black. Hologram aesthetic, high contrast."
)


def find_nano_banana():
    """Find the nano-banana-pro generate_image.py script."""
    paths = [
        "/opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py",
        "/usr/local/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    # Try finding via npm
    try:
        result = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True)
        root = result.stdout.strip()
        p = os.path.join(root, "openclaw/skills/nano-banana-pro/scripts/generate_image.py")
        if os.path.exists(p):
            return p
    except Exception:
        pass
    return None


def get_api_key():
    """Get Gemini API key from env or OpenClaw config."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        key = config.get("skills", {}).get("entries", {}).get("nano-banana-pro", {}).get("apiKey", "")
        if key:
            return key
    return None


def generate_base(output_dir, character_desc, api_key, script_path):
    """Generate the base character sprite."""
    base_path = output_dir / "base.png"
    prompt = f"{character_desc} The robot looks friendly and slightly mischievous. Square composition."

    print(f"Generating base character...")
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key

    result = subprocess.run(
        ["uv", "run", script_path, "--prompt", prompt, "--filename", str(base_path), "--resolution", "1K"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    if base_path.exists():
        print(f"  ✓ Base saved: {base_path}")
        return base_path
    print(f"  ✗ Failed: {result.stderr[-200:]}")
    return None


def generate_emote(base_path, emote, desc, output_dir, character_desc, api_key, script_path):
    """Generate an emote variation from the base."""
    out_path = output_dir / f"{emote}.png"
    prompt = f"Make this robot head {desc} Keep the same wireframe holographic style on pure black background. Same character."

    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key

    result = subprocess.run(
        ["uv", "run", script_path, "--prompt", prompt, "--filename", str(out_path), "-i", str(base_path), "--resolution", "1K"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    if out_path.exists():
        print(f"  ✓ {emote}")
        return out_path
    print(f"  ✗ {emote} failed: {result.stderr[-200:]}")
    return None


def convert_to_holocube(sprites_dir):
    """Convert PNGs to holocube-ready 240x240 animated GIFs with lively motion."""
    from PIL import Image, ImageEnhance

    gif_dir = sprites_dir / "gif"
    jpg_dir = sprites_dir / "jpg"
    gif_dir.mkdir(exist_ok=True)
    jpg_dir.mkdir(exist_ok=True)

    def load(emote):
        src = sprites_dir / f"{emote}.png"
        if not src.exists():
            return None
        img = Image.open(src).convert("RGBA")
        w, h = img.size
        side = min(w, h)
        l, t = (w - side) // 2, (h - side) // 2
        return img.crop((l, t, l + side, t + side)).resize((240, 240), Image.LANCZOS)

    def xform(img, dx=0, dy=0, rot=0, scale=1.0, bright=1.0):
        f = img.copy()
        if bright != 1.0:
            f = ImageEnhance.Brightness(f).enhance(bright)
        if scale != 1.0:
            ns = int(240 * scale)
            f = f.resize((ns, ns), Image.LANCZOS)
            c = Image.new("RGBA", (240, 240), (0, 0, 0, 255))
            o = (240 - ns) // 2
            c.paste(f, (o, o), f)
            f = c
        if rot != 0:
            f = f.rotate(rot, resample=Image.BICUBIC, expand=False, fillcolor=(0, 0, 0, 255))
        if dx != 0 or dy != 0:
            c = Image.new("RGBA", (240, 240), (0, 0, 0, 255))
            c.paste(f, (int(dx), int(dy)), f)
            f = c
        rgb = Image.new("RGB", (240, 240), (0, 0, 0))
        rgb.paste(f, mask=f.split()[3])
        return rgb

    def save(frames, name, duration):
        # Also save a static JPG from frame 0
        jpg_path = jpg_dir / name.replace(".gif", ".jpg")
        frames[0].save(jpg_path, "JPEG", quality=85, subsampling=0)

        q = [f.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for f in frames]
        p = gif_dir / name
        q[0].save(p, save_all=True, append_images=q[1:], duration=duration, loop=0, optimize=True)
        print(f"  {name}: {os.path.getsize(p)//1024}KB, {len(frames)}f @ {duration}ms")

    S = math.sin
    PI2 = 2 * math.pi

    # --- NEUTRAL: float + gentle blink cycle ---
    img = load("neutral")
    if img:
        frames = []
        # 20 frames: float throughout, blink at frames 14-17
        for i in range(20):
            t = S(PI2 * i / 20)
            dy = t * 6
            bright = 0.88 + 0.12 * (t * 0.5 + 0.5)
            # Blink: scale Y slightly at frames 14-16
            sc = 1.0
            if i in (14, 15, 16):
                sc = [0.97, 0.94, 0.97][i - 14]
            frames.append(xform(img, dy=dy, scale=sc, bright=bright))
        save(frames, "adam-neutral.gif", 110)

    # --- HAPPY: energetic bounce + wiggle + glow ---
    img = load("happy")
    if img:
        frames = []
        for i in range(16):
            # Double-bounce pattern
            t = abs(S(PI2 * i / 8))  # two bounces per cycle
            dy = -t * 10
            rot = S(PI2 * i / 16) * 6
            sc = 1.0 + t * 0.07
            bright = 0.9 + 0.2 * t
            frames.append(xform(img, dy=dy, rot=rot, scale=sc, bright=bright))
        save(frames, "adam-happy.gif", 75)

    # --- THINKING: slow pendulum rock + glow pulse ---
    img = load("thinking")
    if img:
        frames = []
        for i in range(24):
            # Pendulum with slight deceleration at edges
            t = S(PI2 * i / 24)
            rot = t * 8
            dx = t * 5
            dy = abs(t) * 3
            # Faster glow flicker
            bright = 0.8 + 0.2 * abs(S(PI2 * i / 6))
            frames.append(xform(img, dx=dx, dy=dy, rot=rot, bright=bright))
        save(frames, "adam-thinking.gif", 90)

    # --- SURPRISED: big jolt → bounce settle ---
    img = load("surprised")
    if img:
        frames = []
        # Keyframed: jolt up, shake, settle
        keyframes = [
            # (dx, dy, rot, scale, bright)
            (0, 0, 0, 1.0, 1.0),       # start
            (0, -12, 0, 1.12, 1.4),     # BIG jolt up
            (6, -8, 5, 1.08, 1.2),      # shake right
            (-6, -6, -5, 1.06, 1.15),   # shake left
            (4, -4, 3, 1.04, 1.1),      # settle right
            (-3, -2, -2, 1.02, 1.05),   # settle left
            (2, -1, 1, 1.01, 1.02),     # almost still
            (-1, 0, 0, 1.0, 1.0),       # rest
            (0, 0, 0, 1.0, 0.95),       # slight dim
            (0, 0, 0, 1.0, 1.0),        # back to normal
            (0, 0, 0, 1.0, 1.0),        # hold
            (0, 0, 0, 1.0, 1.0),        # hold
        ]
        for dx, dy, rot, sc, br in keyframes:
            frames.append(xform(img, dx=dx, dy=dy, rot=rot, scale=sc, bright=br))
        save(frames, "adam-surprised.gif", 70)

    # --- LAUGHING: chaotic shaking + bounce ---
    img = load("laughing")
    if img:
        frames = []
        for i in range(20):
            # Fast lateral shake (period ~4 frames)
            shake = S(PI2 * i / 2.5) * 6
            # Slower bounce
            bounce = -abs(S(PI2 * i / 10)) * 8
            rot = S(PI2 * i / 3) * 7
            sc = 1.0 + abs(S(PI2 * i / 10)) * 0.06
            bright = 0.9 + 0.2 * abs(S(PI2 * i / 5))
            frames.append(xform(img, dx=shake, dy=bounce, rot=rot, scale=sc, bright=bright))
        save(frames, "adam-laughing.gif", 60)

    # --- SLEEPING: very slow deep breathing float ---
    img = load("sleeping")
    if img:
        frames = []
        for i in range(24):
            t = S(PI2 * i / 24)
            dy = t * 8  # big slow bob
            sc = 1.0 + t * 0.03
            rot = S(PI2 * i / 48) * 2  # very slow slight tilt
            bright = 0.45 + 0.25 * (t * 0.5 + 0.5)
            frames.append(xform(img, dy=dy, rot=rot, scale=sc, bright=bright))
        save(frames, "adam-sleeping.gif", 160)


def main():
    parser = argparse.ArgumentParser(description="Generate holocube sprite kit")
    parser.add_argument("--output-dir", default="./sprites", help="Output directory")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY)")
    parser.add_argument("--character", default=DEFAULT_CHARACTER, help="Character description for generation")
    parser.add_argument("--convert-only", action="store_true", help="Skip generation, just convert existing PNGs")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.convert_only:
        script_path = find_nano_banana()
        if not script_path:
            print("ERROR: nano-banana-pro skill not found. Install OpenClaw with nano-banana-pro.")
            sys.exit(1)

        api_key = args.api_key or get_api_key()
        if not api_key:
            print("ERROR: No GEMINI_API_KEY found. Set env var or configure in openclaw.json.")
            sys.exit(1)

        # Generate base
        base = generate_base(output_dir, args.character, api_key, script_path)
        if not base:
            sys.exit(1)

        # Copy base as neutral
        import shutil
        shutil.copy(base, output_dir / "neutral.png")

        # Generate emote variations
        print(f"\nGenerating emotes...")
        for emote, desc in EMOTES.items():
            if emote == "neutral":
                continue
            generate_emote(base, emote, desc, output_dir, args.character, api_key, script_path)

    # Convert to holocube formats
    print(f"\nConverting to holocube formats...")
    convert_to_holocube(output_dir)
    print(f"\nDone! Sprites in {output_dir}")


if __name__ == "__main__":
    main()
