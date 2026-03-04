#!/usr/bin/env python3
"""Generate images via Ollama x/z-image-turbo with verbose logging."""

import argparse
import base64
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_MODEL = "x/z-image-turbo:latest"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SAVE_RE = re.compile(r"Image saved to:\s*(.+)")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ollama-image")


def _write_bytes(out_path: Path, data: bytes):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    log.info("Wrote %d bytes to %s", len(data), out_path)


def _try_parse_json(output: str):
    """Parse JSON from ollama --format json output (may be multiple lines)."""
    images = []
    for i, line in enumerate(output.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            log.debug("Line %d not JSON: %.80s…", i, line)
            continue
        log.debug("Line %d JSON keys: %s", i, list(obj.keys()) if isinstance(obj, dict) else type(obj))
        if isinstance(obj, dict):
            if "images" in obj and isinstance(obj["images"], list):
                images.extend([x for x in obj["images"] if isinstance(x, str)])
            if "image" in obj and isinstance(obj["image"], str):
                images.append(obj["image"])
            if "response" in obj and isinstance(obj["response"], str):
                images.append(obj["response"])
    log.info("Parsed %d image candidate(s) from JSON", len(images))
    return images


def _maybe_saved_path(output: str):
    for line in output.splitlines():
        m = SAVE_RE.search(line.strip())
        if m:
            path = m.group(1).strip()
            log.info("Detected 'Image saved to' path: %s", path)
            return path
    return None


def generate(prompt, out, width=1024, height=1024, steps=20, seed=None, negative=None, model=DEFAULT_MODEL, timeout=180):
    cmd = [
        "ollama", "run", model, prompt,
        "--width", str(width),
        "--height", str(height),
        "--steps", str(steps),
    ]
    if seed is not None:
        cmd += ["--seed", str(seed)]
    if negative:
        cmd += ["--negative", negative]

    # Run from the output directory so relative "Image saved to:" paths land there
    cwd = str(out.parent)
    os.makedirs(cwd, exist_ok=True)

    log.info("Command: %s", " ".join(cmd))
    log.info("CWD: %s", cwd)
    log.info("Timeout: %ds", timeout)

    t0 = time.time()
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        log.error("Timeout after %.1fs", elapsed)
        raise RuntimeError(f"Ollama timeout after {elapsed:.0f}s")

    elapsed = time.time() - t0
    log.info("Process exited in %.1fs with code %d", elapsed, res.returncode)
    log.info("stdout length: %d chars", len(res.stdout))
    log.info("stderr length: %d chars", len(res.stderr))

    if res.stdout:
        log.debug("stdout first 500 chars: %s", res.stdout[:500])
    if res.stderr:
        log.debug("stderr first 500 chars: %s", res.stderr[:500])

    if res.returncode != 0:
        raise RuntimeError(f"Ollama error (code {res.returncode}): {res.stderr.strip() or res.stdout.strip()}")

    # 1) Ollama saves directly to file and prints path
    saved_path = _maybe_saved_path(res.stdout) or _maybe_saved_path(res.stderr)
    # Resolve relative paths against cwd
    if saved_path and not os.path.isabs(saved_path):
        saved_path = os.path.join(cwd, saved_path)
    if saved_path and os.path.exists(saved_path):
        log.info("Found saved file at %s (%d bytes)", saved_path, os.path.getsize(saved_path))
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(saved_path, out)
        log.info("Copied to %s", out)
        return out

    # 2) Try JSON base64
    images_b64 = _try_parse_json(res.stdout)
    if images_b64:
        try:
            data = base64.b64decode(images_b64[0])
            log.info("Decoded base64: %d bytes, starts with PNG magic: %s", len(data), data[:8] == PNG_MAGIC)
            if data.startswith(PNG_MAGIC):
                _write_bytes(out, data)
                return out
        except Exception as e:
            log.warning("Base64 decode failed: %s", e)

    # 3) Fallback: raw stdout as PNG
    raw = res.stdout.encode()
    log.debug("Raw stdout first 16 bytes: %s", raw[:16])
    if raw.startswith(PNG_MAGIC):
        log.info("Raw stdout is PNG (%d bytes)", len(raw))
        _write_bytes(out, raw)
        return out

    raise RuntimeError("No image data detected in ollama output")


def main():
    ap = argparse.ArgumentParser(description="Generate image with ollama x/z-image-turbo")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--negative", default=None)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("-v", "--verbose", action="store_true", help="Extra verbose output")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    out_path = Path(args.out)
    try:
        result = generate(
            prompt=args.prompt,
            out=out_path,
            width=args.width,
            height=args.height,
            steps=args.steps,
            seed=args.seed,
            negative=args.negative,
            model=args.model,
            timeout=args.timeout,
        )
        log.info("SUCCESS: %s", result)
        print(str(result))
    except Exception as e:
        log.error("FAILED: %s", e)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
