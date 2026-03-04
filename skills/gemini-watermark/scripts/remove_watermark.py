#!/usr/bin/env python3
"""
Gemini Watermark Remover — Pure Python, fully offline

Removes the Gemini AI star/sparkle watermark from generated images using
mathematically accurate reverse alpha blending.

No network access, no binary downloads, no external executables.
All processing is local and auditable.

Dependencies : pip install Pillow numpy   (or: uv pip install Pillow numpy)
Python       : >= 3.9

Algorithm reference: ../references/algorithm.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# ── Dependency check ────────────────────────────────────────────────────────
try:
    import numpy as np
    from PIL import Image
except ImportError as exc:
    print(f"[ERR] Missing dependency: {exc}")
    print("      Install with : pip install Pillow numpy")
    print("      Or with uv   : uv pip install Pillow numpy")
    sys.exit(1)

__version__ = "2.1.0"

# ── Configuration ────────────────────────────────────────────────────────────
SMALL_SIZE    = 48     # watermark size (px) when min(w,h) ≤ 1024
SMALL_MARGIN  = 32     # bottom-right margin for small watermark
LARGE_SIZE    = 96     # watermark size (px) when both dimensions > 1024
LARGE_MARGIN  = 64     # bottom-right margin for large watermark

ALPHA_FLOOR   = 0.002  # skip pixels whose alpha is below this (noise)
ALPHA_CEIL    = 0.99   # clamp alpha to prevent division by near-zero

NCC_EARLY_EXIT    = 0.25   # Stage-1 circuit breaker
DEFAULT_THRESHOLD = 0.35   # overall confidence threshold for detection

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# ── Alpha Map ────────────────────────────────────────────────────────────────
_ALPHA_CACHE: dict[int, np.ndarray] = {}


def _build_alpha_map(size: int) -> np.ndarray:
    """
    Construct a synthetic alpha map for the Gemini 4-pointed sparkle logo.

    The Gemini watermark is a semi-transparent white star/sparkle placed in
    the bottom-right corner of generated images.

    Model: tight central Gaussian + 4 elongated rays along cardinal axes.
      alpha = 0.0 → fully transparent (pixel unchanged)
      alpha = 1.0 → fully opaque white

    For maximum accuracy you can supply your own alpha map (--alpha-map)
    derived from a background capture of the Gemini watermark on white:
        alpha(x, y) = max(R, G, B) / 255
    """
    c    = (size - 1) / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    dx = (xx - c) / c    # normalised to [-1, 1]
    dy = (yy - c) / c

    # Central bright spot
    core = np.exp(-(dx**2 + dy**2) / (2 * 0.14**2))

    # 4 elongated rays along horizontal and vertical cardinal directions
    sigma_r = 0.55   # ray reach
    sigma_w = 0.07   # ray width (thin taper)
    ray_h = (np.exp(-dx**2 / (2 * sigma_r**2)) *
             np.exp(-dy**2 / (2 * sigma_w**2)))
    ray_v = (np.exp(-dy**2 / (2 * sigma_r**2)) *
             np.exp(-dx**2 / (2 * sigma_w**2)))

    alpha = np.minimum(1.0, core + 0.75 * np.maximum(ray_h, ray_v))
    mx = alpha.max()
    return (alpha / mx if mx > 0 else alpha).astype(np.float32)


def get_alpha_map(size: int,
                  alpha_file: Optional[str] = None) -> np.ndarray:
    """Return the alpha map for *size*; load from file if given."""
    if alpha_file:
        p = Path(alpha_file)
        if not p.is_file():
            _die(f"Alpha map not found: {alpha_file}")
        img = Image.open(p).convert("L").resize((size, size), Image.LANCZOS)
        return np.array(img, dtype=np.float32) / 255.0
    if size not in _ALPHA_CACHE:
        _ALPHA_CACHE[size] = _build_alpha_map(size)
    return _ALPHA_CACHE[size]


# ── Helpers ──────────────────────────────────────────────────────────────────
def _die(msg: str) -> None:
    print(f"[ERR] {msg}", file=sys.stderr)
    sys.exit(1)


def _select_watermark(w: int, h: int,
                      force_small: bool,
                      force_large: bool) -> tuple[int, int]:
    if force_large:
        return LARGE_SIZE, LARGE_MARGIN
    if force_small:
        return SMALL_SIZE, SMALL_MARGIN
    return ((LARGE_SIZE, LARGE_MARGIN)
            if (w > 1024 and h > 1024)
            else (SMALL_SIZE, SMALL_MARGIN))


# ── Three-Stage Detection ────────────────────────────────────────────────────
def _ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Normalised Cross-Correlation between two 2-D arrays."""
    a = a - a.mean()
    b = b - b.mean()
    denom = float(np.sqrt((a * a).sum() * (b * b).sum()))
    return float((a * b).sum() / denom) if denom > 1e-12 else 0.0


def _sobel(arr: np.ndarray) -> np.ndarray:
    """3×3 Sobel edge magnitude — pure numpy, edge-padded."""
    p = np.pad(arr, 1, mode="edge")
    gx = (-p[:-2, :-2] + p[:-2, 2:]
          - 2 * p[1:-1, :-2] + 2 * p[1:-1, 2:]
          - p[2:, :-2] + p[2:, 2:])
    gy = (-p[:-2, :-2] - 2 * p[:-2, 1:-1] - p[:-2, 2:]
          + p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:])
    return np.sqrt(gx**2 + gy**2)


def detect(pixels: np.ndarray,
           alpha: np.ndarray,
           wx: int, wy: int, size: int,
           threshold: float) -> tuple[bool, float]:
    """
    Three-stage watermark detection.
    Returns (detected: bool, confidence: float).

    Stage 1 — Spatial NCC        (50% weight, circuit-breaker at 0.25)
    Stage 2 — Gradient NCC       (30% weight)
    Stage 3 — Variance dampening (20% weight)
    """
    region = pixels[wy:wy + size, wx:wx + size]
    gray   = region.mean(axis=2)

    # Stage 1
    s1 = _ncc(gray, alpha)
    if s1 < NCC_EARLY_EXIT:
        return False, s1 * 0.5

    # Stage 2
    s2 = _ncc(_sobel(gray), _sobel(alpha))

    # Stage 3 — compare texture to the reference region directly above
    ref_y  = max(0, wy - size)
    ref    = pixels[ref_y:ref_y + size, wx:wx + size].mean(axis=2)
    s3     = float(np.clip(1.0 - gray.std() / (ref.std() + 1e-6), 0.0, 1.0))

    conf = 0.50 * s1 + 0.30 * s2 + 0.20 * s3
    return conf >= threshold, conf


# ── Reverse Alpha Blending ───────────────────────────────────────────────────
def remove_watermark(pixels: np.ndarray,
                     alpha: np.ndarray,
                     wx: int, wy: int, size: int) -> np.ndarray:
    """
    Recover original pixels via the inverse blending equation:

        watermarked = alpha * 255 + (1 - alpha) * original
        ⟹ original  = (watermarked - alpha * 255) / (1 - alpha)
    """
    out    = pixels.copy()
    region = out[wy:wy + size, wx:wx + size]

    a_3d   = np.clip(alpha, ALPHA_FLOOR, ALPHA_CEIL)[:, :, np.newaxis]
    mask   = (alpha >= ALPHA_FLOOR)[:, :, np.newaxis]

    recovered = np.clip((region - a_3d * 255.0) / (1.0 - a_3d),
                        0.0, 255.0)
    out[wy:wy + size, wx:wx + size] = np.where(mask, recovered, region)
    return out


# ── Single-Image Processing ──────────────────────────────────────────────────
def process_image(src: Path, dst: Path, *,
                  force: bool,
                  threshold: float,
                  force_small: bool,
                  force_large: bool,
                  alpha_file: Optional[str],
                  verbose: bool,
                  quiet: bool) -> bool:
    """Process one image file. Returns True on success."""

    def info(msg: str) -> None:
        if not quiet:
            print(msg)

    def vlog(msg: str) -> None:
        if verbose:
            print(f"  {msg}")

    try:
        img = Image.open(src).convert("RGB")
    except Exception as exc:
        info(f"[ERR] Cannot open {src.name}: {exc}")
        return False

    w, h = img.size
    size, margin = _select_watermark(w, h, force_small, force_large)
    wx = w - size - margin
    wy = h - size - margin

    if wx < 0 or wy < 0:
        info(f"[WARN] {src.name}: image too small ({w}×{h}) — skipped")
        return True

    alpha  = get_alpha_map(size, alpha_file)
    pixels = np.array(img, dtype=np.float32)

    vlog(f"Image {w}×{h}, watermark {size}×{size} at ({wx},{wy})")

    if force:
        pixels = remove_watermark(pixels, alpha, wx, wy, size)
        info(f"[OK] {src.name} → {dst} (forced)")
    else:
        found, conf = detect(pixels, alpha, wx, wy, size, threshold)
        vlog(f"Detection confidence: {conf:.3f} (threshold: {threshold})")
        if not found:
            info(f"[SKIP] {src.name}: no watermark detected (conf={conf:.3f})")
            return True
        pixels = remove_watermark(pixels, alpha, wx, wy, size)
        info(f"[OK] {src.name} → {dst} (conf={conf:.3f})")

    result = Image.fromarray(pixels.astype(np.uint8), "RGB")
    dst.parent.mkdir(parents=True, exist_ok=True)
    ext    = dst.suffix.lower()
    save_kw = ({"quality": 100, "subsampling": 0}
               if ext in (".jpg", ".jpeg") else {})
    result.save(dst, **save_kw)
    return True


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(
        prog="remove_watermark",
        description="Remove Gemini AI watermarks via reverse alpha blending. "
                    "No network access or binary downloads required.",
    )
    ap.add_argument("input",
                    help="Input image file or directory")
    ap.add_argument("-o", "--output",
                    help="Output file or directory")
    ap.add_argument("-f", "--force", action="store_true",
                    help="Skip detection; always remove watermark region")
    ap.add_argument("-t", "--threshold", type=float,
                    default=DEFAULT_THRESHOLD,
                    help=f"Detection confidence threshold "
                         f"(default: {DEFAULT_THRESHOLD})")
    ap.add_argument("--force-small", action="store_true",
                    help="Force 48×48 watermark size")
    ap.add_argument("--force-large", action="store_true",
                    help="Force 96×96 watermark size")
    ap.add_argument("--alpha-map",
                    help="Custom grayscale alpha map image. "
                         "Derive with alpha(x,y)=max(R,G,B)/255 from a "
                         "Gemini watermark captured on a white background.")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-q", "--quiet",   action="store_true")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")

    args = ap.parse_args()

    kwargs: dict = dict(
        force       = args.force,
        threshold   = args.threshold,
        force_small = args.force_small,
        force_large = args.force_large,
        alpha_file  = args.alpha_map,
        verbose     = args.verbose,
        quiet       = args.quiet,
    )

    src     = Path(args.input)
    success = True

    if src.is_dir():
        files = sorted(f for f in src.rglob("*")
                       if f.suffix.lower() in SUPPORTED_EXTS)
        if not files:
            print(f"[WARN] No supported images found in {src}")
            sys.exit(0)
        out_dir = (Path(args.output) if args.output
                   else src.parent / (src.name + "_cleaned"))
        for f in files:
            dst = out_dir / f.relative_to(src)
            success &= process_image(f, dst, **kwargs)

    elif src.is_file():
        if src.suffix.lower() not in SUPPORTED_EXTS:
            _die(f"Unsupported format: {src.suffix}. "
                 f"Supported: {', '.join(sorted(SUPPORTED_EXTS))}")
        dst = (Path(args.output) if args.output
               else src.with_name(f"{src.stem}_cleaned{src.suffix}"))
        success = process_image(src, dst, **kwargs)

    else:
        _die(f"Not found: {src}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
