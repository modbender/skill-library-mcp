#!/usr/bin/env python3
"""
ImaginePro AI Image Generation API — CLI Helper Script

Zero-dependency Python script (stdlib only) for interacting with the ImaginePro API.
Designed for use by AI agents (Claude Code, OpenClaw, Codex, etc.).

Usage:
    export IMAGINEPRO_API_KEY="your-key"
    python3 imaginepro_api.py <command> [options]

Commands:
    imagine   — Submit an image generation request (returns messageId)
    wait      — Submit + poll until done (blocking)
    status    — Check generation status by messageId
    upscale   — Upscale an image (Midjourney button or Flux upscale)
    removebg  — Remove background from an image
    enhance   — Enhance/expand a prompt (free)
    models    — List available models with credit costs

Get your API key at: https://platform.imaginepro.ai/dashboard/setup
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://api.imaginepro.ai/api/v1"

# Model name → backend endpoint mapping
MODEL_ENDPOINTS = {
    "midjourney": "/midjourney/imagine",
    "alpha v6": "/midjourney/imagine",
    "flux": "/flux/imagine",
    "nano-banana": "/universal/imagine",
    "nano banana": "/universal/imagine",
    "lumi-girl": "/universal/zimage",
    "lumi girl": "/universal/zimage",
    "mj-video": "/video/mj/generate",
    "mj video": "/video/mj/generate",
}

# Credit costs per operation
CREDIT_COSTS = {
    "midjourney_fast": 10,
    "midjourney_relax": 5,
    "midjourney_upscale": 5,
    "flux_imagine": 6,
    "flux_upscale": 2,
    "nano_banana_imagine": 6,
    "lumi_girl_imagine": 6,
    "mj_video": 10,
    "remove_bg": 5,
    "prompt_enhance": 0,
}


def get_api_key():
    """Read the API key from the IMAGINEPRO_API_KEY environment variable."""
    key = os.environ.get("IMAGINEPRO_API_KEY", "").strip()
    if not key:
        print(
            json.dumps(
                {
                    "error": "IMAGINEPRO_API_KEY environment variable is not set. "
                    "Get your key at https://platform.imaginepro.ai/dashboard/setup"
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    return key


# ──────────────────────────────────────────────────────────────────────────────
# HTTP helpers (stdlib only — no requests/httpx dependency)
# ──────────────────────────────────────────────────────────────────────────────


def api_request(method, path, data=None, api_key=None):
    """
    Make an HTTP request to the ImaginePro API.

    Args:
        method: HTTP method (GET or POST).
        path: API path (e.g., "/flux/imagine"). Appended to BASE_URL.
        data: Request body as a dict (JSON-encoded for POST requests).
        api_key: Bearer token. Reads from env if not provided.

    Returns:
        Parsed JSON response as a dict.

    Raises:
        SystemExit on HTTP errors with a JSON error message to stderr.
    """
    if api_key is None:
        api_key = get_api_key()

    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            error_json = json.loads(error_body)
        except json.JSONDecodeError:
            error_json = {"message": error_body, "statusCode": e.code}
        print(json.dumps(error_json), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(
            json.dumps({"error": f"Connection error: {e.reason}"}), file=sys.stderr
        )
        sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Core API functions
# ──────────────────────────────────────────────────────────────────────────────


def imagine(prompt, model="flux", mode="fast", n=1, ref_images=None, width=None, height=None,
            start_frame=None, end_frame=None):
    """
    Submit an image generation request.

    Args:
        prompt: Text prompt describing the desired image.
        model: One of midjourney, flux, nano-banana, lumi-girl, mj-video.
        mode: Generation speed mode — "fast" or "relax" (Midjourney only).
        n: Number of images to generate (Flux / Nano Banana).
        ref_images: List of reference image URLs (Nano Banana only).
        width: Image width in pixels (Lumi Girl only, max 1024, divisible by 8).
        height: Image height in pixels (Lumi Girl only, max 1024, divisible by 8).
        start_frame: Start frame URL (MJ Video only, required).
        end_frame: End frame URL (MJ Video only, required).

    Returns:
        Dict with messageId from the API.
    """
    model_lower = model.lower().strip()
    endpoint = MODEL_ENDPOINTS.get(model_lower)
    if not endpoint:
        print(
            json.dumps(
                {
                    "error": f"Unknown model: {model}. Available: midjourney, flux, nano-banana, lumi-girl, mj-video"
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    # Build request body based on model type
    if model_lower in ("midjourney", "alpha v6"):
        # Midjourney: prompt can include --relax, --ar, etc.
        full_prompt = prompt
        if mode == "relax" and "--relax" not in prompt:
            full_prompt += " --relax"
        data = {"prompt": full_prompt}

    elif model_lower == "flux":
        data = {"prompt": prompt, "n": n}

    elif model_lower in ("nano-banana", "nano banana"):
        # Build multi-modal contents array
        contents = [{"type": "text", "text": f"Image creation: {prompt}"}]
        if ref_images:
            for img_url in ref_images:
                if img_url:
                    contents.append({"type": "image", "url": img_url})
        data = {"contents": contents, "model": "nano-banana-2"}

    elif model_lower in ("lumi-girl", "lumi girl"):
        # Calculate dimensions from --ar in prompt if not explicitly provided
        w = width or 1024
        h = height or 1024
        if not width and not height:
            import re
            ar_match = re.search(r"--ar\s+(\d+):(\d+)|--aspect-ratio\s+(\d+):(\d+)", prompt, re.IGNORECASE)
            if ar_match:
                wr = int(ar_match.group(1) or ar_match.group(3))
                hr = int(ar_match.group(2) or ar_match.group(4))
                ratio = wr / hr
                if ratio >= 1:
                    w, h = 1024, int(1024 / ratio)
                else:
                    w, h = int(1024 * ratio), 1024
        # Snap to multiples of 8
        w = max(8, (min(1024, w) // 8) * 8)
        h = max(8, (min(1024, h) // 8) * 8)
        data = {"prompt": prompt, "steps": 4, "width": w, "height": h}

    elif model_lower in ("mj-video", "mj video"):
        if not start_frame or not end_frame:
            print(
                json.dumps({"error": "MJ Video requires --start-frame and --end-frame URLs."}),
                file=sys.stderr,
            )
            sys.exit(1)
        data = {
            "prompt": prompt,
            "startFrameUrl": start_frame,
            "endFrameUrl": end_frame,
            "timeout": 900,
        }

    else:
        data = {"prompt": prompt}

    return api_request("POST", endpoint, data)


def check_status(message_id):
    """
    Poll the status of a generation task.

    Args:
        message_id: The messageId returned from a generation request.

    Returns:
        Dict with status, progress, uri, images, etc.
    """
    return api_request("GET", f"/midjourney/message/{message_id}")


def wait_for_result(prompt, model="flux", timeout=300, interval=5, **kwargs):
    """
    Submit a generation request and poll until completion.

    Args:
        prompt: Text prompt.
        model: Model name.
        timeout: Max seconds to wait (default 300).
        interval: Polling interval in seconds (default 5).
        **kwargs: Additional args passed to imagine().

    Returns:
        Final status dict with uri/images on success.
    """
    result = imagine(prompt, model=model, **kwargs)
    message_id = result.get("messageId")
    if not message_id:
        return result

    start = time.time()
    while time.time() - start < timeout:
        time.sleep(interval)
        status = check_status(message_id)
        s = status.get("status", "").upper()

        if s == "DONE":
            status["messageId"] = message_id
            return status
        elif s == "FAIL":
            status["messageId"] = message_id
            return status

        # Print progress to stderr so stdout stays clean for JSON
        progress = status.get("progress", 0)
        print(f"[{int(time.time() - start)}s] Status: {s}, Progress: {progress}%", file=sys.stderr)

    return {
        "error": f"Timed out after {timeout}s",
        "messageId": message_id,
        "status": "TIMEOUT",
    }


def upscale_image(message_id=None, button="U1", image_url=None, scale=2):
    """
    Upscale an image via Midjourney button action or Flux upscale.

    For Midjourney: provide message_id and button (U1-U4, V1-V4).
    For Flux: provide image_url and scale (2-4).
    """
    if image_url:
        # Flux upscale
        return api_request("POST", "/flux/upscale", {"image": image_url, "scale": scale})
    elif message_id:
        # Midjourney button action
        return api_request(
            "POST", "/midjourney/button", {"messageId": message_id, "button": button}
        )
    else:
        print(
            json.dumps({"error": "Provide --id (Midjourney) or --image (Flux) for upscaling."}),
            file=sys.stderr,
        )
        sys.exit(1)


def remove_background(image_url):
    """Remove background from an image URL."""
    return api_request("POST", "/tools/remove-bg", {"image": image_url})


def enhance_prompt(prompt):
    """Expand a short prompt into a detailed, high-quality prompt (free)."""
    return api_request("POST", "/tools/prompt-extend", {"prompt": prompt})


def list_models():
    """Return a structured list of available models and their costs."""
    return {
        "models": [
            {
                "name": "midjourney",
                "aliases": ["alpha v6"],
                "endpoint": "/midjourney/imagine",
                "credits": {"fast": 10, "relax": 5},
                "features": ["--ar", "--style", "--chaos", "--no", "--seed", "--q", "--relax"],
                "description": "Midjourney v6 — artistic and photorealistic images",
            },
            {
                "name": "flux",
                "aliases": [],
                "endpoint": "/flux/imagine",
                "credits": {"per_image": 6},
                "features": ["batch generation (n)"],
                "description": "Flux — fast general-purpose image generation",
            },
            {
                "name": "nano-banana",
                "aliases": ["nano banana"],
                "endpoint": "/universal/imagine",
                "credits": {"per_image": 6},
                "features": ["reference images", "virtual try-on", "product mockup", "style transfer"],
                "description": "Nano Banana v2 — multi-modal generation with reference images",
            },
            {
                "name": "lumi-girl",
                "aliases": ["lumi girl"],
                "endpoint": "/universal/zimage",
                "credits": {"per_image": 6},
                "features": ["--ar", "custom width/height"],
                "description": "Lumi Girl — character portraits and stylized images",
            },
            {
                "name": "mj-video",
                "aliases": ["mj video"],
                "endpoint": "/video/mj/generate",
                "credits": {"per_video": 10},
                "features": ["start/end frame interpolation"],
                "description": "MJ Video — video generation from start and end frames",
            },
        ],
        "tools": [
            {
                "name": "flux-upscale",
                "endpoint": "/flux/upscale",
                "credits": 2,
                "description": "Upscale any image (2x-4x)",
            },
            {
                "name": "midjourney-upscale",
                "endpoint": "/midjourney/button",
                "credits": 5,
                "description": "Upscale/variant of Midjourney images (U1-U4, V1-V4)",
            },
            {
                "name": "remove-bg",
                "endpoint": "/tools/remove-bg",
                "credits": 5,
                "description": "Remove image background",
            },
            {
                "name": "prompt-enhance",
                "endpoint": "/tools/prompt-extend",
                "credits": 0,
                "description": "Expand a short prompt into a detailed prompt (free)",
            },
        ],
    }


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def output(data, raw_json=False):
    """Print output to stdout. If raw_json, print compact JSON; otherwise pretty-print."""
    if raw_json:
        print(json.dumps(data))
    else:
        print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="ImaginePro AI Image Generation API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Get your API key at: https://platform.imaginepro.ai/dashboard/setup",
    )
    parser.add_argument("--json", action="store_true", help="Output compact JSON (default is pretty-printed)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # imagine — submit generation request
    p_imagine = subparsers.add_parser("imagine", help="Submit an image generation request")
    p_imagine.add_argument("--prompt", "-p", required=True, help="Text prompt for generation")
    p_imagine.add_argument(
        "--model", "-m", default="flux",
        choices=["midjourney", "flux", "nano-banana", "lumi-girl", "mj-video"],
        help="Model to use (default: flux)",
    )
    p_imagine.add_argument("--mode", default="fast", choices=["fast", "relax"], help="Speed mode (Midjourney only)")
    p_imagine.add_argument("--n", type=int, default=1, help="Number of images (Flux/Nano Banana)")
    p_imagine.add_argument("--ref-image", action="append", dest="ref_images", help="Reference image URL (Nano Banana, repeatable)")
    p_imagine.add_argument("--width", type=int, help="Image width (Lumi Girl, max 1024, divisible by 8)")
    p_imagine.add_argument("--height", type=int, help="Image height (Lumi Girl, max 1024, divisible by 8)")
    p_imagine.add_argument("--start-frame", help="Start frame URL (MJ Video)")
    p_imagine.add_argument("--end-frame", help="End frame URL (MJ Video)")

    # wait — submit + poll until done
    p_wait = subparsers.add_parser("wait", help="Submit and wait for result (blocking)")
    p_wait.add_argument("--prompt", "-p", required=True, help="Text prompt for generation")
    p_wait.add_argument(
        "--model", "-m", default="flux",
        choices=["midjourney", "flux", "nano-banana", "lumi-girl", "mj-video"],
        help="Model to use (default: flux)",
    )
    p_wait.add_argument("--mode", default="fast", choices=["fast", "relax"], help="Speed mode (Midjourney only)")
    p_wait.add_argument("--n", type=int, default=1, help="Number of images (Flux/Nano Banana)")
    p_wait.add_argument("--ref-image", action="append", dest="ref_images", help="Reference image URL (Nano Banana, repeatable)")
    p_wait.add_argument("--width", type=int, help="Image width (Lumi Girl)")
    p_wait.add_argument("--height", type=int, help="Image height (Lumi Girl)")
    p_wait.add_argument("--start-frame", help="Start frame URL (MJ Video)")
    p_wait.add_argument("--end-frame", help="End frame URL (MJ Video)")
    p_wait.add_argument("--timeout", type=int, default=300, help="Max wait time in seconds (default: 300)")
    p_wait.add_argument("--interval", type=int, default=5, help="Polling interval in seconds (default: 5)")

    # status — check generation status
    p_status = subparsers.add_parser("status", help="Check generation status")
    p_status.add_argument("--id", required=True, help="Message ID to check")

    # upscale — upscale an image
    p_upscale = subparsers.add_parser("upscale", help="Upscale an image")
    p_upscale.add_argument("--id", help="Original Midjourney message ID")
    p_upscale.add_argument("--button", default="U1", help="Button action: U1-U4, V1-V4 (default: U1)")
    p_upscale.add_argument("--image", help="Image URL for Flux upscale")
    p_upscale.add_argument("--scale", type=int, default=2, help="Upscale factor 2-4 (default: 2)")

    # removebg — remove background
    p_removebg = subparsers.add_parser("removebg", help="Remove image background")
    p_removebg.add_argument("--image", required=True, help="Image URL")

    # enhance — enhance/expand prompt
    p_enhance = subparsers.add_parser("enhance", help="Enhance/expand a prompt (free)")
    p_enhance.add_argument("--prompt", "-p", required=True, help="Short prompt to enhance")

    # models — list available models
    subparsers.add_parser("models", help="List available models and credit costs")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    raw = getattr(args, "json", False)

    # ── Dispatch commands ─────────────────────────────────────────────────
    if args.command == "imagine":
        result = imagine(
            args.prompt,
            model=args.model,
            mode=args.mode,
            n=args.n,
            ref_images=args.ref_images,
            width=args.width,
            height=args.height,
            start_frame=args.start_frame,
            end_frame=args.end_frame,
        )
        output(result, raw)

    elif args.command == "wait":
        result = wait_for_result(
            args.prompt,
            model=args.model,
            mode=args.mode,
            n=args.n,
            ref_images=args.ref_images,
            width=args.width,
            height=args.height,
            start_frame=args.start_frame,
            end_frame=args.end_frame,
            timeout=args.timeout,
            interval=args.interval,
        )
        output(result, raw)

    elif args.command == "status":
        result = check_status(args.id)
        output(result, raw)

    elif args.command == "upscale":
        result = upscale_image(
            message_id=args.id,
            button=args.button,
            image_url=args.image,
            scale=args.scale,
        )
        output(result, raw)

    elif args.command == "removebg":
        result = remove_background(args.image)
        output(result, raw)

    elif args.command == "enhance":
        result = enhance_prompt(args.prompt)
        output(result, raw)

    elif args.command == "models":
        result = list_models()
        output(result, raw)


if __name__ == "__main__":
    main()
