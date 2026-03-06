#!/usr/bin/env python3
"""ReelWords caption job helper.

Creates a caption render job, polls until completion/failure, and optionally downloads
result.downloadUrl.

Env:
  REELWORDS_API_KEY: required
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

import requests

BASE_URL = "https://api.reelwords.ai"


class ReelWordsError(RuntimeError):
    pass


def _require_api_key(explicit: Optional[str]) -> str:
    key = explicit or os.environ.get("REELWORDS_API_KEY")
    if not key:
        raise ReelWordsError(
            "Missing API key. Set REELWORDS_API_KEY env var or pass --api-key. "
            "Expected token starting with 'rw_'."
        )
    return key


def _headers(api_key: str) -> Dict[str, str]:
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def create_caption_job(api_key: str, payload: Dict[str, Any], timeout_s: int = 60) -> Dict[str, Any]:
    url = f"{BASE_URL}/api/v1/caption-jobs"
    r = requests.post(url, headers=_headers(api_key), json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ReelWordsError(f"POST {url} failed: HTTP {r.status_code}: {r.text}")
    return r.json()


def get_caption_job(api_key: str, job_id: str, timeout_s: int = 60) -> Dict[str, Any]:
    url = f"{BASE_URL}/api/v1/caption-jobs/{job_id}"
    r = requests.get(url, headers={"x-api-key": api_key, "Accept": "application/json"}, timeout=timeout_s)
    if r.status_code >= 400:
        raise ReelWordsError(f"GET {url} failed: HTTP {r.status_code}: {r.text}")
    return r.json()


def is_terminal_status(status: Optional[str]) -> bool:
    if not status:
        return False
    s = status.strip().lower()
    return s in {"completed", "complete", "done", "failed", "error", "cancelled", "canceled"}


def is_success_status(status: Optional[str]) -> bool:
    if not status:
        return False
    s = status.strip().lower()
    return s in {"completed", "complete", "done"}


def download_from_url(url: str, out_path: str, timeout_s: int = 300) -> None:
    with requests.get(url, stream=True, timeout=timeout_s) as r:
        if r.status_code >= 400:
            raise ReelWordsError(f"Download failed: HTTP {r.status_code}: {r.text}")
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def download_via_video_endpoint(api_key: str, job_id: str, out_path: str, timeout_s: int = 300) -> None:
    """Download via GET /api/v1/caption-jobs/{id}/video which 302-redirects to signed URL."""
    url = f"{BASE_URL}/api/v1/caption-jobs/{job_id}/video"
    with requests.get(url, headers={"x-api-key": api_key, "Accept": "application/json"}, stream=True, allow_redirects=True, timeout=timeout_s) as r:
        if r.status_code == 409:
            raise ReelWordsError(f"Job not ready for download yet (HTTP 409): {r.text}")
        if r.status_code >= 400:
            raise ReelWordsError(f"Download endpoint failed: HTTP {r.status_code}: {r.text}")
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    style: Dict[str, Any] = {"styleId": args.style_id}

    # Optional style fields
    if args.position_y is not None:
        style["positionY"] = args.position_y
    if args.font_size is not None:
        style["fontSize"] = args.font_size
    if args.main_color is not None:
        style["mainColor"] = args.main_color
    if args.highlight_color is not None:
        style["highlightColor"] = args.highlight_color
    if args.hook_color is not None:
        style["hookColor"] = args.hook_color
    if args.font_family is not None:
        style["fontFamily"] = args.font_family
    if args.style_classes is not None:
        style["styleClasses"] = args.style_classes

    preferences: Dict[str, Any] = {"style": style}

    # Optional preferences
    if args.add_emojis is not None:
        preferences["addEmojis"] = bool(args.add_emojis)
    if args.max_words_per_line is not None:
        preferences["maxWordsPerLine"] = args.max_words_per_line

    return {
        "videoUrl": args.video_url,
        "preferences": preferences,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Create/poll ReelWords caption job and optionally download result.")
    p.add_argument("--api-key", default=None, help="ReelWords API key (or set REELWORDS_API_KEY env var)")
    p.add_argument("--video-url", required=True, help="Source video URL (must be reachable by ReelWords)")
    p.add_argument("--style-id", required=True, help="Style preset id (e.g., style1)")

    p.add_argument("--add-emojis", action=argparse.BooleanOptionalAction, default=None)
    p.add_argument("--max-words-per-line", type=int, default=None)

    # style fields
    p.add_argument("--position-y", type=int, default=None)
    p.add_argument("--font-size", type=int, default=None)
    p.add_argument("--main-color", default=None)
    p.add_argument("--highlight-color", default=None)
    p.add_argument("--hook-color", default=None)
    p.add_argument("--font-family", default=None)
    p.add_argument("--style-classes", default=None)

    p.add_argument("--poll-interval", type=float, default=3.0)
    p.add_argument("--timeout", type=float, default=15 * 60.0, help="Max seconds to poll before giving up")
    p.add_argument("--out", default=None, help="If set, download the rendered video to this path")
    p.add_argument(
        "--download-mode",
        choices=["auto", "result-url", "video-endpoint"],
        default="auto",
        help="Download strategy: auto (try result.downloadUrl then /video), result-url, or video-endpoint.",
    )
    p.add_argument("--print-every", type=int, default=5, help="Print status every N polls")

    args = p.parse_args()

    try:
        api_key = _require_api_key(args.api_key)
        payload = build_payload(args)

        created = create_caption_job(api_key, payload)
        job_id = created.get("id")
        if not job_id:
            raise ReelWordsError(f"Create response missing id: {json.dumps(created)[:2000]}")

        start = time.time()
        polls = 0
        latest = created
        while True:
            polls += 1
            latest = get_caption_job(api_key, job_id)
            status = latest.get("status")

            if polls % max(1, args.print_every) == 0:
                sys.stderr.write(f"poll={polls} status={status}\n")

            # Failure signals
            if latest.get("failureReason") or latest.get("failureMessage"):
                break

            # Terminal status strings
            if is_terminal_status(status):
                break

            if time.time() - start > args.timeout:
                raise ReelWordsError(f"Timed out after {args.timeout:.0f}s polling job {job_id}. Last status={status}")

            time.sleep(args.poll_interval)

        # Output final JSON
        print(json.dumps(latest, indent=2, sort_keys=True))

        # Optional download
        if args.out:
            status = latest.get("status")
            if not is_success_status(status):
                raise ReelWordsError(f"Job not successful (status={status}); not downloading.")

            job_id = latest.get("id") or job_id

            if args.download_mode in {"auto", "result-url"}:
                download_url = (latest.get("result") or {}).get("downloadUrl")
                if download_url:
                    download_from_url(download_url, args.out)
                    sys.stderr.write(f"Downloaded to: {args.out}\n")
                    return 0
                if args.download_mode == "result-url":
                    raise ReelWordsError("Missing result.downloadUrl; cannot download in result-url mode.")

            # Fallback or explicit mode
            download_via_video_endpoint(api_key, job_id, args.out)
            sys.stderr.write(f"Downloaded to: {args.out}\n")

        return 0

    except ReelWordsError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
