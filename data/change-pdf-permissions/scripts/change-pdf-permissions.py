#!/usr/bin/env python3
"""
change_pdf_permissions.py

Uploads a PDF + permission flags to Solutions API change-permissions endpoint, polls until done,
then prints JSON with the download URL for the updated PDF.

Env vars (preferred):
  SOLUTIONS_API_KEY
  SOLUTIONS_BASE_URL
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any, Dict, Optional

import requests


DEFAULT_BASE_URL = "https://api.xss-cross-service-solutions.com/solutions/solutions"
CREATE_PATH = "/api/75"


DEFAULT_PERMISSIONS: Dict[str, bool] = {
    "canModify": False,
    "canModifyAnnotations": False,
    "canPrint": True,
    "canPrintHighQuality": True,
    "canAssembleDocument": False,
    "canFillInForm": True,
    "canExtractContent": False,
    "canExtractForAccessibility": True,
}


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


def parse_bool(s: str) -> bool:
    v = s.strip().lower()
    if v in {"true", "t", "1", "yes", "y", "ja"}:
        return True
    if v in {"false", "f", "0", "no", "n", "nein"}:
        return False
    raise ValueError(f"Invalid boolean value: {s!r}")


def bool_to_api(v: bool) -> str:
    return "true" if v else "false"


def create_job(
    base_url: str,
    api_key: str,
    pdf_path: str,
    permissions: Dict[str, bool],
    timeout_s: int = 180,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + CREATE_PATH
    headers = make_headers(api_key)

    data = {k: bool_to_api(bool(v)) for k, v in permissions.items()}

    with open(pdf_path, "rb") as f:
        files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
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


def extract_download(info: Dict[str, Any]) -> Optional[Dict[str, str]]:
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
    path = first.get("path")
    name = first.get("name")
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
                "message": "Change-permissions job failed.",
                "raw": info,
            }

        file_entry = extract_download(info)
        if status == "done" and file_entry:
            return {
                "job_id": job_id,
                "status": info.get("status"),
                "download_url": file_entry["path"],
                "file_name": file_entry["name"],
                "raw": info,
            }

        time.sleep(min(delay, max_delay_s))
        delay = min(max_delay_s, delay * 1.6)


def main() -> int:
    ap = argparse.ArgumentParser(description="Change PDF permissions via Solutions API.")
    ap.add_argument("--pdf", required=True, help="Path to input PDF")
    ap.add_argument("--api-key", default=os.getenv("SOLUTIONS_API_KEY", ""), help="Solutions API key (Bearer token)")
    ap.add_argument(
        "--base-url",
        default=os.getenv("SOLUTIONS_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL override",
    )
    ap.add_argument("--timeout", type=int, default=180, help="Total polling timeout in seconds (default 180)")

    # Flags (all optional on CLI; we fall back to defaults)
    ap.add_argument("--can-modify", default=None)
    ap.add_argument("--can-modify-annotations", default=None)
    ap.add_argument("--can-print", default=None)
    ap.add_argument("--can-print-high-quality", default=None)
    ap.add_argument("--can-assemble-document", default=None)
    ap.add_argument("--can-fill-in-form", default=None)
    ap.add_argument("--can-extract-content", default=None)
    ap.add_argument("--can-extract-for-accessibility", default=None)

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
            {"status": "error", "error": "missing_file", "message": f"File not found: {args.pdf}"},
            ensure_ascii=False,
            indent=2
        ))
        return 2

    if not is_pdf_file(args.pdf):
        print(json.dumps(
            {"status": "error", "error": "not_a_pdf", "message": "Input file must be a .pdf"},
            ensure_ascii=False,
            indent=2
        ))
        return 2

    # Build permissions: start from defaults, override any provided flags
    perms = dict(DEFAULT_PERMISSIONS)
    override_map = {
        "canModify": args.can_modify,
        "canModifyAnnotations": args.can_modify_annotations,
        "canPrint": args.can_print,
        "canPrintHighQuality": args.can_print_high_quality,
        "canAssembleDocument": args.can_assemble_document,
        "canFillInForm": args.can_fill_in_form,
        "canExtractContent": args.can_extract_content,
        "canExtractForAccessibility": args.can_extract_for_accessibility,
    }

    try:
        for k, v in override_map.items():
            if v is not None:
                perms[k] = parse_bool(v)
    except ValueError as e:
        print(json.dumps(
            {"status": "error", "error": "invalid_permission_value", "message": str(e)},
            ensure_ascii=False,
            indent=2
        ))
        return 2

    try:
        created = create_job(
            base_url=args.base_url,
            api_key=args.api_key,
            pdf_path=args.pdf,
            permissions=perms,
        )
    except Exception as e:
        print(json.dumps(
            {"status": "error", "error": "create_failed", "message": str(e)},
            ensure_ascii=False,
            indent=2
        ))
        return 1

    job_id = created.get("id")
    if job_id is None:
        print(json.dumps(
            {"status": "error", "error": "missing_job_id", "message": "Create response did not include 'id'.", "raw": created},
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

    result["permissions"] = perms

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if str(result.get("status", "")).lower() == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
