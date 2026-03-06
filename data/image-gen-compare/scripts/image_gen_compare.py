#!/usr/bin/env python3
"""
image_gen_compare.py — generate and compare images from paid vs local models

Usage:
  # Generate with both models (default prompt)
  python3 image_gen_compare.py

  # Custom prompt
  python3 image_gen_compare.py --prompt "your prompt here"

  # One model only
  python3 image_gen_compare.py --model dalle3
  python3 image_gen_compare.py --model flux

  # List previous runs
  python3 image_gen_compare.py --list

Outputs saved to: workspace/content/images/
Metadata logged to: workspace/content/images/runs.json

Models:
  dalle3  — OpenAI DALL-E 3 (paid ~$0.04-0.08/image)
  flux    — FLUX.1-schnell via mflux (local, free, MLX/Metal)
"""

from __future__ import annotations
import argparse
import base64
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent

# Save to Proton Drive Artifacts (synced, visible in Proton Drive app)
_PROTON = Path.home() / "Library/CloudStorage/ProtonDrive-user@proton.me-folder/Artifacts/images"
_today = datetime.now().strftime("%Y/%m/%d")
OUTPUT_DIR = _PROTON / _today if _PROTON.parent.exists() else WORKSPACE / "content" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RUNS_LOG = WORKSPACE / "content" / "images" / "runs.json"
(WORKSPACE / "content" / "images").mkdir(parents=True, exist_ok=True)

# LinkedIn cover image dimensions (16:9 recommended)
LINKEDIN_W = 1200
LINKEDIN_H = 627

# DALL-E 3 closest 16:9 option
DALLE_W = 1792
DALLE_H = 1024


# ── Secrets ───────────────────────────────────────────────────────────────────

def _get_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    try:
        token_path = Path.home() / ".config/openclaw/.op-service-token"
        env = os.environ.copy()
        env["OP_SERVICE_ACCOUNT_TOKEN"] = token_path.read_text().strip()
        result = subprocess.run(
            ["op", "read", "op://OpenClaw/OpenAI API Key/credential"],
            capture_output=True, text=True, env=env, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as exc:
        print(f"Warning: 1Password fetch failed: {exc}", file=sys.stderr)
    raise RuntimeError("No OPENAI_API_KEY found")


# ── DALL-E 3 ──────────────────────────────────────────────────────────────────

def generate_dalle3(prompt: str, quality: str = "standard") -> dict:
    """Generate an image with DALL-E 3. Returns result dict."""
    import requests

    key = _get_openai_key()
    cost = 0.04 if quality == "standard" else 0.08

    print(f"\n🎨 DALL-E 3 ({quality}, {DALLE_W}×{DALLE_H}, ~${cost:.2f})...")
    start = time.monotonic()

    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": f"{DALLE_W}x{DALLE_H}",
            "quality": quality,
            "response_format": "url",
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    latency = time.monotonic() - start

    image_url = data["data"][0]["url"]
    revised_prompt = data["data"][0].get("revised_prompt", prompt)

    # Download the image
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:20]
    filename = f"dalle3_{quality}_{ts}.png"
    dest = OUTPUT_DIR / filename

    img_resp = requests.get(image_url, timeout=30)
    dest.write_bytes(img_resp.content)

    result = {
        "model": "dalle3",
        "quality": quality,
        "prompt": prompt,
        "revised_prompt": revised_prompt,
        "filename": filename,
        "path": str(dest),
        "width": DALLE_W,
        "height": DALLE_H,
        "latency_s": round(latency, 2),
        "cost_usd": cost,
        "timestamp": datetime.now().isoformat(),
    }

    print(f"  ✅ Done in {latency:.1f}s → {filename}")
    if revised_prompt != prompt:
        print(f"  📝 Revised prompt: {revised_prompt[:120]}...")

    return result


# ── FLUX.1-schnell via mflux ──────────────────────────────────────────────────

def generate_flux(prompt: str, steps: int = 4, seed: int | None = None) -> dict:
    """Generate an image with FLUX.1-schnell via mflux (local, free)."""
    try:
        # mflux v0.16+ uses explicit module paths
        from mflux.models.flux.variants.txt2img.flux import Flux1
        from mflux.models.common.config.model_config import ModelConfig
    except ImportError:
        raise RuntimeError("mflux not installed. Run: pip install mflux")

    print(f"\n🖥️  FLUX.1-schnell (local, {LINKEDIN_W}×{LINKEDIN_H}, {steps} steps, free)...")
    print("   (First run: downloads ~9GB model from HuggingFace — grab a coffee)")

    start = time.monotonic()

    # Load model (downloads from HuggingFace on first run)
    flux = Flux1(
        model_config=ModelConfig.schnell(),
        quantize=8,                # 8-bit quantization — quality/speed balance on M4
    )

    image = flux.generate_image(
        seed=seed or 42,
        prompt=prompt,
        num_inference_steps=steps,
        height=LINKEDIN_H,
        width=LINKEDIN_W,
        guidance=0.0,              # schnell doesn't use CFG
    )

    latency = time.monotonic() - start

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"flux_schnell_{steps}steps_{ts}.png"
    dest = OUTPUT_DIR / filename

    image.image.save(str(dest))

    result = {
        "model": "flux_schnell",
        "steps": steps,
        "seed": seed,
        "prompt": prompt,
        "filename": filename,
        "path": str(dest),
        "width": LINKEDIN_W,
        "height": LINKEDIN_H,
        "latency_s": round(latency, 2),
        "cost_usd": 0.0,
        "timestamp": datetime.now().isoformat(),
    }

    print(f"  ✅ Done in {latency:.1f}s → {filename}")
    return result


# ── Stable Diffusion XL via diffusers (PyTorch MPS) ─────────────────────────

# SDXL native 16:9 resolution (SDXL training bucket closest to LinkedIn 1200×627)
SDXL_W = 1344
SDXL_H = 768


def generate_sdxl(prompt: str, steps: int = 30, seed: int | None = None) -> dict:
    """Generate with SDXL base via diffusers on Apple MPS. Free, ungated, ~7GB model."""
    try:
        import torch
        from diffusers import StableDiffusionXLPipeline
    except ImportError:
        raise RuntimeError("diffusers not installed. Run: pip install diffusers accelerate")

    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS (Apple Metal) not available — is this Apple Silicon?")

    print(f"\n🍎 SDXL base (MPS, {SDXL_W}×{SDXL_H}, {steps} steps, free)...")
    print("   (First run: downloads ~7GB model from HuggingFace)")

    start = time.monotonic()

    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float32,    # float16 UNet→NaN latents on MPS (torch 2.10); float32 uses ~14GB but M4 24GB handles it
        use_safetensors=True,
    )
    pipe = pipe.to("mps")
    pipe.enable_attention_slicing()   # reduces peak VRAM without much quality loss

    generator = torch.Generator("mps").manual_seed(seed or 42)

    result_img = pipe(
        prompt=prompt,
        num_inference_steps=steps,
        height=SDXL_H,
        width=SDXL_W,
        generator=generator,
    ).images[0]

    latency = time.monotonic() - start

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:20]
    filename = f"sdxl_base_{steps}steps_{ts}.png"
    dest = OUTPUT_DIR / filename
    result_img.save(str(dest))

    result = {
        "model": "sdxl_base",
        "steps": steps,
        "seed": seed or 42,
        "prompt": prompt,
        "filename": filename,
        "path": str(dest),
        "width": SDXL_W,
        "height": SDXL_H,
        "latency_s": round(latency, 2),
        "cost_usd": 0.0,
        "timestamp": datetime.now().isoformat(),
        "notes": "PyTorch MPS (Apple Silicon). Ungated Apache 2.0.",
    }

    print(f"  ✅ Done in {latency:.1f}s → {filename}")
    return result


# ── Logging ───────────────────────────────────────────────────────────────────

def _load_runs() -> list:
    if RUNS_LOG.exists():
        return json.loads(RUNS_LOG.read_text())
    return []


def _save_run(result: dict) -> None:
    runs = _load_runs()
    runs.append(result)
    RUNS_LOG.write_text(json.dumps(runs, indent=2))


def _list_runs() -> None:
    runs = _load_runs()
    if not runs:
        print("No runs yet.")
        return
    print(f"\n{'#':<4} {'Model':<18} {'Cost':>6}  {'Time':>6}  {'File'}")
    print("-" * 70)
    for i, r in enumerate(runs, 1):
        model = r.get("model", "?")
        cost = f"${r.get('cost_usd', 0):.3f}"
        latency = f"{r.get('latency_s', 0):.1f}s"
        fname = r.get("filename", "?")
        print(f"{i:<4} {model:<18} {cost:>6}  {latency:>6}  {fname}")

    total_cost = sum(r.get("cost_usd", 0) for r in runs)
    print(f"\nTotal runs: {len(runs)} | Total paid cost: ${total_cost:.4f}")


# ── CLI ───────────────────────────────────────────────────────────────────────

DEFAULT_PROMPT = (
    "A Mac Mini on a minimal dark desk, glowing with purpose, surrounded by "
    "floating terminal windows and electric blue neural network connections streaming "
    "through the air. Warm amber accent lighting. The glow of an always-on AI system "
    "running through the night. Cinematic, moody, professional tech blog cover image. "
    "Dark background, sharp foreground detail."
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and compare images: DALL-E 3 vs FLUX local")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Image prompt")
    parser.add_argument("--model", choices=["dalle3", "flux", "sdxl", "all"], default="all")
    parser.add_argument("--quality", choices=["standard", "hd"], default="standard", help="DALL-E 3 quality")
    parser.add_argument("--steps", type=int, default=4, help="FLUX inference steps (4=fast, 8=better)")
    parser.add_argument("--seed", type=int, default=None, help="FLUX seed for reproducibility")
    parser.add_argument("--list", action="store_true", help="List previous runs")
    args = parser.parse_args()

    if args.list:
        _list_runs()
        return

    print(f"\nPrompt: {args.prompt[:100]}...")
    print(f"Output: {OUTPUT_DIR}")

    results = []

    if args.model in ("dalle3", "all"):
        try:
            result = generate_dalle3(args.prompt, quality=args.quality)
            _save_run(result)
            results.append(result)
        except Exception as exc:
            print(f"  ❌ DALL-E 3 failed: {exc}", file=sys.stderr)

    if args.model in ("flux", "all"):
        try:
            result = generate_flux(args.prompt, steps=args.steps, seed=args.seed)
            _save_run(result)
            results.append(result)
        except Exception as exc:
            print(f"  ❌ FLUX failed: {exc}", file=sys.stderr)

    if args.model in ("sdxl", "all"):
        try:
            result = generate_sdxl(args.prompt, steps=args.steps, seed=args.seed)
            _save_run(result)
            results.append(result)
        except Exception as exc:
            print(f"  ❌ SDXL failed: {exc}", file=sys.stderr)

    if results:
        print(f"\n📁 Images saved to: {OUTPUT_DIR}")
        for r in results:
            print(f"   {r['model']:20} {r['filename']}  ({r['latency_s']:.1f}s, ${r['cost_usd']:.3f})")
        if len(results) > 1:
            print("\n💡 Open side by side:")
            paths = " ".join('"' + r["path"] + '"' for r in results)
            print(f"   open {paths}")


if __name__ == "__main__":
    main()
