#!/usr/bin/env python3
"""
add_watermark_to_pdf.py

Uploads one or multiple PDFs + a watermark text to Solutions API watermark endpoint, polls until done,
then prints JSON with download URL(s) for the watermarked PDFs and/or ZIP.

Env vars (preferred):
  SOLUTIONS_API_KEY
  SOLUTIONS_BASE_URL

Usage:
  python scripts/add_watermark_to_pdf.py --pdf "/path/to/a.pdf" --pdf "/path/to/b.pdf" --text "CONFIDENTIAL" --api-key "..."
Or:
  export SOLUTIONS_API_KEY="..."
  python scripts/add_watermark_to_pdf.py --pdf "/path/to/a.pdf" --text "CONFIDENTIAL"
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any, Dict, List, Tuple

import requests


DEFAULT_BASE_URL = "https://api.xss-cross-service-solutions.com/solutions/solutions"
CREATE_PATH = "/api/61"


def make_headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def safe_text(resp: requests.Response, max_len: int = 500) -> str:
    try:
        t = resp.text
        return t[:max_len] + "…" if len(t) > max_len else t
    except Exception:
        return "<unreadable response>"


def is_pdf_file(path: str) -> bool:
    return path.lower().endswith(".pdf")


def create_job(
    base_url: str,
    api_key: str,
    pdf_paths: List[str],
    text: str,
    timeout_s: int = 180,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + CREATE_PATH
    headers = make_headers(api_key)

    files: List[Tuple[str, Tuple[str, Any, str]]] = []
    opened = []

    try:
        for p in pdf_paths:
            f = open(p, "rb")
            opened.append(f)
            files.append(("files", (os.path.basename(p), f, "application/pdf")))

        data = {"text": text}
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=timeout_s)
    finally:
        for f in opened:
            try:
                f.close()
            except Exception:
                pass

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


def extract_outputs(info: Dict[str, Any]) -> List[Dict[str, str]]:
    outputs: List[Dict[str, str]] = []
    if not isinstance(info, dict):
        return outputs
    output = info.get("output")
    if not isinstance(output, dict):
        return outputs
    files = output.get("files")
    if not isinstance(files, list):
        return outputs

    for item in files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        name = item.get("name")
        if isinstance(path, str) and path.strip():
            outputs.append({"name": str(name) if name is not None else "", "path": path})
    return outputs


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

        if status in {"failed", "error"}:
            return {
                "job_id": job_id,
                "status": info.get("status"),
                "error": "job_failed",
                "message": "Add-watermark job failed.",
                "raw": info,
            }

        outputs = extract_outputs(info)
        if status == "done" and outputs:
            download_urls = [o["path"] for o in outputs if o.get("path")]
            result: Dict[str, Any] = {
                "job_id": job_id,
                "status": info.get("status"),
                "outputs": outputs,
                "download_urls": download_urls,
                "raw": info,
            }
            if len(download_urls) == 1:
                result["download_url"] = download_urls[0]
                result["file_name"] = outputs[0].get("name", "")
            return result

        time.sleep(min(delay, max_delay_s))
        delay = min(max_delay_s, delay * 1.6)


def main() -> int:
    ap = argparse.ArgumentParser(description="Add a text watermark to PDFs via Solutions API.")
    ap.add_argument("--pdf", action="append", required=True, help="Path to an input PDF (repeatable)")
    ap.add_argument("--text", required=True, help="Watermark text")
    ap.add_argument("--api-key", default=os.getenv("SOLUTIONS_API_KEY", ""), help="Solutions API key (Bearer token)")
    ap.add_argument(
        "--base-url",
        default=os.getenv("SOLUTIONS_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL override",
    )
    ap.add_argument("--timeout", type=int, default=180, help="Total polling timeout in seconds (default 180)")
    args = ap.parse_args()

    pdf_paths = args.pdf
    text = args.text.strip()

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

    if not text:
        print(json.dumps(
            {
                "status": "error",
                "error": "missing_text",
                "message": "Watermark text must be non-empty.",
            },
            ensure_ascii=False,
            indent=2
        ))
        return 2

    missing = [p for p in pdf_paths if not os.path.isfile(p)]
    if missing:
        print(json.dumps(
            {
                "status": "error",
                "error": "missing_files",
                "message": "Some files were not found.",
                "files": missing,
            },
            ensure_ascii=False,
            indent=2
        ))
        return 2

    non_pdf = [p for p in pdf_paths if not is_pdf_file(p)]
    if non_pdf:
        print(json.dumps(
            {
                "status": "error",
                "error": "not_a_pdf",
                "message": "All inputs must be .pdf files.",
                "files": non_pdf,
            },
            ensure_ascii=False,
            indent=2
        ))
        return 2

    try:
        created = create_job(
            base_url=args.base_url,
            api_key=args.api_key,
            pdf_paths=pdf_paths,
            text=text,
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

    result["input_files"] = [os.path.basename(p) for p in pdf_paths]
    # Optional: include watermark text (safe in most cases, but omit if you prefer)
    result["watermark_text"] = text

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if str(result.get("status", "")).lower() == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
