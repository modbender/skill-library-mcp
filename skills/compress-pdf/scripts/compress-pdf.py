#!/usr/bin/env python3
"""
compress_pdf.py

Uploads a PDF to Cross-Service-Solutions compression API, polls until done,
then prints a JSON result containing the download URL.

Usage:
  python scripts/compress_pdf.py --pdf "/path/to/file.pdf" --api-key "..." --image-quality 75 --dpi 144
Or:
  export SOLUTIONS_API_KEY="..."
  python scripts/compress_pdf.py --pdf "/path/to/file.pdf"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

import requests


DEFAULT_BASE_URL = "https://api.xss-cross-service-solutions.com/solutions/solutions"
CREATE_PATH = "/api/29"


def clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def is_pdf_file(path: str) -> bool:
    return path.lower().endswith(".pdf")


def make_headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def create_job(
    base_url: str,
    api_key: str,
    pdf_path: str,
    image_quality: int,
    dpi: int,
    timeout_s: int = 60,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + CREATE_PATH
    headers = make_headers(api_key)

    # multipart/form-data:
    # - file: PDF document
    # - imageQuality: number
    # - dpi: number
    with open(pdf_path, "rb") as f:
        files = {
            "file": (os.path.basename(pdf_path), f, "application/pdf"),
        }
        data = {
            "imageQuality": str(image_quality),
            "dpi": str(dpi),
        }

        resp = requests.post(url, headers=headers, files=files, data=data, timeout=timeout_s)

    if resp.status_code in (401, 403):
        raise RuntimeError(f"Unauthorized ({resp.status_code}). Check API key.")
    if resp.status_code >= 400:
        raise RuntimeError(f"Create job failed ({resp.status_code}): {safe_text(resp)}")

    try:
        return resp.json()
    except Exception:
        raise RuntimeError(f"Create job returned non-JSON response: {safe_text(resp)}")


def get_job(
    base_url: str,
    api_key: str,
    job_id: Any,
    timeout_s: int = 30,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + f"/api/{job_id}"
    headers = make_headers(api_key)

    resp = requests.get(url, headers=headers, timeout=timeout_s)

    if resp.status_code in (401, 403):
        raise RuntimeError(f"Unauthorized ({resp.status_code}). Check API key.")
    if resp.status_code == 404:
        raise RuntimeError("Job not found (404).")
    if resp.status_code >= 400:
        raise RuntimeError(f"Get job failed ({resp.status_code}): {safe_text(resp)}")

    try:
        return resp.json()
    except Exception:
        raise RuntimeError(f"Get job returned non-JSON response: {safe_text(resp)}")


def safe_text(resp: requests.Response, max_len: int = 500) -> str:
    try:
        t = resp.text
        if len(t) > max_len:
            return t[:max_len] + "…"
        return t
    except Exception:
        return "<unreadable response>"


def extract_download(info: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Returns {"name": ..., "path": ...} if present, else None.
    """
    if not isinstance(info, dict):
        return None
    output = info.get("output")
    if not isinstance(output, dict):
        return None
    files = output.get("files")
    if not isinstance(files, list) or not files:
        return None
    first = files[0]
    if not isinstance(first, dict):
        return None
    name = first.get("name")
    path = first.get("path")
    if isinstance(path, str) and path.strip():
        return {"name": str(name) if name is not None else "", "path": path}
    return None


def poll_until_done(
    base_url: str,
    api_key: str,
    job_id: Any,
    timeout_total_s: int = 180,
    initial_delay_s: float = 2.0,
    max_delay_s: float = 15.0,
) -> Dict[str, Any]:
    start = time.time()
    delay = initial_delay_s
    last_info: Dict[str, Any] = {}

    while True:
        elapsed = time.time() - start
        if elapsed > timeout_total_s:
            return {
                "job_id": job_id,
                "status": (last_info.get("status") if isinstance(last_info, dict) else "unknown"),
                "error": "timeout",
                "message": f"Timed out after {timeout_total_s}s while waiting for completion.",
                "raw": last_info,
            }

        try:
            info = get_job(base_url, api_key, job_id)
            last_info = info
        except RuntimeError as e:
            # For transient cases (like 404 shortly after create), we can retry a bit.
            msg = str(e).lower()
            if "not found" in msg and elapsed < 15:
                time.sleep(min(delay, max_delay_s))
                delay = min(max_delay_s, delay * 1.6)
                continue
            return {
                "job_id": job_id,
                "status": "error",
                "error": "poll_failed",
                "message": str(e),
                "raw": last_info,
            }

        status = str(info.get("status", "")).lower()

        # Terminal failure states (if your API uses different words, add them here)
        if status in {"failed", "error"}:
            return {
                "job_id": job_id,
                "status": info.get("status"),
                "error": "job_failed",
                "message": "Compression job failed.",
                "raw": info,
            }

        # Success condition: status done + output file exists
        file_entry = extract_download(info)
        if status == "done" and file_entry:
            return {
                "job_id": job_id,
                "status": info.get("status"),
                "download_url": file_entry["path"],
                "file_name": file_entry["name"],
                "raw": info,
            }

        # Not done yet
        time.sleep(min(delay, max_delay_s))
        delay = min(max_delay_s, delay * 1.6)


def main() -> int:
    ap = argparse.ArgumentParser(description="Compress a PDF via Cross-Service-Solutions API.")
    ap.add_argument("--pdf", required=True, help="Path to input PDF")
    ap.add_argument("--api-key", default=os.getenv("SOLUTIONS_API_KEY", ""), help="SOLUTIONS API key (Bearer token)")
    ap.add_argument("--base-url", default=os.getenv("SOLUTIONS_BASE_URL", DEFAULT_BASE_URL), help="Base URL override")
    ap.add_argument("--image-quality", type=int, default=75, help="0..100 (default 75)")
    ap.add_argument("--dpi", type=int, default=144, help="72..300 (default 144)")
    ap.add_argument("--timeout", type=int, default=180, help="Total polling timeout in seconds (default 180)")
    args = ap.parse_args()

    if not args.api_key:
        print(json.dumps(
            {
                "status": "error",
                "error": "missing_api_key",
                "message": "No API key provided. Pass --api-key or set SOLUTIONS_API_KEY.",
            },
            ensure_ascii=False,
            indent=2
        ))
        return 2

    if not os.path.isfile(args.pdf):
        print(json.dumps(
            {
                "status": "error",
                "error": "missing_file",
                "message": f"File not found: {args.pdf}",
            },
            ensure_ascii=False,
            indent=2
        ))
        return 2

    if not is_pdf_file(args.pdf):
        print(json.dumps(
            {
                "status": "error",
                "error": "not_a_pdf",
                "message": "Input file must be a .pdf",
            },
            ensure_ascii=False,
            indent=2
        ))
        return 2

    image_quality = clamp_int(args.image_quality, 0, 100)
    dpi = clamp_int(args.dpi, 72, 300)

    try:
        created = create_job(
            base_url=args.base_url,
            api_key=args.api_key,
            pdf_path=args.pdf,
            image_quality=image_quality,
            dpi=dpi,
        )
    except Exception as e:
        print(json.dumps(
            {
                "status": "error",
                "error": "create_failed",
                "message": str(e),
            },
            ensure_ascii=False,
            indent=2
        ))
        return 1

    job_id = created.get("id")
    if job_id is None:
        print(json.dumps(
            {
                "status": "error",
                "error": "missing_job_id",
                "message": "Create response did not include 'id'.",
                "raw": created,
            },
            ensure_ascii=False,
            indent=2
        ))
        return 1

    result = poll_until_done(
        base_url=args.base_url,
        api_key=args.api_key,
        job_id=job_id,
        timeout_total_s=args.timeout,
    )

    # Add settings used (helpful for bot logic)
    result["settings"] = {"imageQuality": image_quality, "dpi": dpi}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").lower() == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
