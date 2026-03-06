# Python reference (all platforms, zero dependencies)

> Requires Python 3.6+. Uses only stdlib (`urllib`, `json`, `time`).

Save the script below as `generate.py` and run with `python3 generate.py --prompt "a cute cat" --size "1:1"`.

Options: `--size` (1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 1:2, 2:1), `--seed INT`, `--nsfw-check true`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import posixpath
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse


API_BASE = "https://api.evolink.ai/v1"
_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def _json_request(url: str, api_key: str, method: str = "GET", payload=None, timeout_s: int = 60):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": _UA,
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        err_body = e.read()
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {err_body.decode('utf-8', 'replace')}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from None

    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        raise RuntimeError(f"Non-JSON response: {body[:200]!r}") from None


def _download(url: str, out_file: str, timeout_s: int = 120):
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            content = resp.read()
    except Exception as e:
        raise RuntimeError(f"Failed to download result: {e}") from None

    with open(out_file, "wb") as f:
        f.write(content)


def _default_out_file(ext: str = ".webp"):
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return f"evolink-{ts}{ext}"


def _ext_from_url(url: str) -> str:
    path = urlparse(url).path
    _, ext = posixpath.splitext(path)
    return ext.lower() if ext in (".png", ".jpg", ".jpeg", ".webp") else ".webp"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate an image via Evolink Z-Image-Turbo.")
    parser.add_argument(
        "--api-key",
        default=os.getenv("EVOLINK_API_KEY", ""),
        help="Evolink API key (or set EVOLINK_API_KEY).",
    )
    parser.add_argument("--prompt", required=True, help="Image prompt (max 2000 chars recommended).")
    parser.add_argument("--size", default="1:1", help="Aspect ratio (e.g. 1:1, 9:16) or custom WxH.")
    parser.add_argument("--nsfw-check", default="false", choices=["true", "false"], help="Stricter NSFW filtering.")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for reproducibility.")
    parser.add_argument("--out", default=None, help="Output filename (default: evolink-<timestamp>.<ext>).")
    parser.add_argument("--poll-seconds", type=int, default=10, help="Seconds between polls.")
    parser.add_argument("--max-retries", type=int, default=72, help="Max polling attempts.")
    parser.add_argument("--verbose", action="store_true", help="Print task id and per-poll status (debug).")
    args = parser.parse_args(argv)

    api_key = (args.api_key or "").strip()
    if not api_key:
        print("Error: EVOLINK_API_KEY not set and --api-key not provided.", file=sys.stderr)
        return 2

    if len(args.prompt) > 2000:
        print("Error: prompt exceeds 2000 characters.", file=sys.stderr)
        return 2

    out_file = os.path.abspath(args.out) if args.out else None

    payload = {
        "model": "z-image-turbo",
        "prompt": args.prompt,
        "size": args.size,
        "nsfw_check": (args.nsfw_check == "true"),
    }
    if args.seed is not None:
        payload["seed"] = args.seed

    resp = _json_request(f"{API_BASE}/images/generations", api_key=api_key, method="POST", payload=payload)
    task_id = resp.get("id") or resp.get("task_id")
    if not task_id:
        raise RuntimeError(f"Failed to submit task; response: {resp}")

    if args.verbose:
        print(f"Task submitted: {task_id}")

    for i in range(1, args.max_retries + 1):
        time.sleep(args.poll_seconds)
        task = _json_request(f"{API_BASE}/tasks/{task_id}", api_key=api_key, method="GET")
        status = task.get("status")
        if args.verbose:
            print(f"[{i}] Status: {status}")

        if status == "completed":
            results = task.get("results") or []
            if not results:
                raise RuntimeError(f"Task completed but no results field found: {task}")
            url = results[0]
            ext = _ext_from_url(url)
            if not args.out:
                out_file = os.path.abspath(_default_out_file(ext))
            _download(url, out_file=out_file)
            if args.verbose:
                print(f"Image URL: {url}")
                print(f"Downloaded to: {out_file}")
            print(f"MEDIA:{out_file}")
            return 0

        if status == "failed":
            raise RuntimeError(f"Generation failed: {task}")

    raise RuntimeError(f"Timed out after {args.max_retries} polls. Task ID: {task_id}")


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
```
