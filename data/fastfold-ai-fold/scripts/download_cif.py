#!/usr/bin/env python3
"""
Download CIF file(s) for a completed FastFold job. Single CIF for complex jobs;
one file per sequence for non-complex (e.g. output_0.cif, output_1.cif).

Usage:
    download_cif.py JOB_ID [--out FILE] [--dir DIR] [--base-url URL]

- Complex job: --out single.cif or --dir ./out (writes job_id.cif in dir).
- Non-complex: --dir ./out (writes output_0.cif, output_1.cif, ...).

Requires: Python standard library only (no external dependencies)
Environment: FASTFOLD_API_KEY
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from load_env import load_dotenv
from security_utils import (
    validate_artifact_url,
    validate_base_url,
    validate_job_id,
    validate_results_payload,
)


def get_results(base_url: str, api_key: str, job_id: str) -> dict:
    url = f"{base_url.rstrip('/')}/v1/jobs/{job_id}/results"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    req = urllib.request.Request(url=url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_text = resp.read().decode("utf-8", errors="replace")
            status = resp.getcode()
    except urllib.error.HTTPError as e:
        status = e.code
        response_text = e.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        sys.exit(f"Error: Network error while fetching results: {e.reason}")

    if status == 401:
        sys.exit("Error: Unauthorized. Check FASTFOLD_API_KEY.")
    if status == 404:
        sys.exit("Error: Job not found.")
    if status >= 400:
        sys.exit(f"Error: {status} - {response_text}")
    try:
        return validate_results_payload(json.loads(response_text))
    except json.JSONDecodeError:
        sys.exit(f"Error: API returned invalid JSON (status {status}).")


def download(url: str, path: str, max_bytes: int) -> None:
    safe_url = validate_artifact_url(url)
    req = urllib.request.Request(url=safe_url, method="GET")
    no_redirect = urllib.request.build_opener(_NoRedirectHandler())
    try:
        with no_redirect.open(req, timeout=60) as resp:
            content_type = (resp.headers.get("Content-Type") or "").lower()
            if content_type and ("html" in content_type or "javascript" in content_type):
                sys.exit(f"Error: Unexpected artifact content-type: {content_type}")
            content_len = resp.headers.get("Content-Length")
            if content_len:
                try:
                    if int(content_len) > max_bytes:
                        sys.exit(f"Error: Artifact exceeds size limit ({max_bytes} bytes).")
                except ValueError:
                    pass

            bytes_written = 0
            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    bytes_written += len(chunk)
                    if bytes_written > max_bytes:
                        sys.exit(f"Error: Artifact exceeds size limit ({max_bytes} bytes).")
                    f.write(chunk)
    except urllib.error.HTTPError as e:
        if 300 <= e.code < 400:
            sys.exit("Error: Redirects are not allowed for artifact downloads.")
        sys.exit(f"Error: Failed to download artifact (HTTP {e.code}).")
    except urllib.error.URLError as e:
        sys.exit(f"Error: Network error while downloading artifact: {e.reason}")


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="Download CIF file(s) for a completed FastFold job.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--out", help="Output CIF path (single file; use for complex or single-sequence)")
    ap.add_argument("--dir", default=".", help="Output directory for multiple CIFs (default .)")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument(
        "--max-bytes",
        type=int,
        default=50_000_000,
        help="Maximum artifact size in bytes (default 50000000)",
    )
    args = ap.parse_args()

    api_key = os.environ.get("FASTFOLD_API_KEY")
    if not api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY in .env or environment.")

    job_id = validate_job_id(args.job_id)
    base_url = validate_base_url(args.base_url)
    if args.max_bytes <= 0:
        sys.exit("Error: --max-bytes must be > 0.")

    data = get_results(base_url, api_key, job_id)
    job = data.get("job", {})
    status = job.get("status")
    if status != "COMPLETED":
        sys.exit(f"Error: Job status is {status}, not COMPLETED. Wait for completion first.")

    is_complex = job.get("isComplex", False)
    sequences = data.get("sequences", [])
    pred = data.get("predictionPayload")

    if is_complex and pred and pred.get("cif_url"):
        url = pred["cif_url"]
        if args.out:
            path = args.out
        else:
            path = os.path.join(args.dir, f"{job_id}.cif")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        download(url, path, max_bytes=args.max_bytes)
        print(path)
        return

    # Non-complex: one CIF per sequence
    urls = []
    for s in sequences:
        pp = (s or {}).get("predictionPayload") or {}
        if pp.get("cif_url"):
            urls.append(pp["cif_url"])
    if not urls:
        sys.exit("Error: No CIF URLs in results.")
    if args.out and len(urls) == 1:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        download(urls[0], args.out, max_bytes=args.max_bytes)
        print(args.out)
        return
    if args.out and len(urls) > 1:
        sys.exit("Error: Job has multiple sequences; use --dir instead of --out.")
    os.makedirs(args.dir, exist_ok=True)
    for i, url in enumerate(urls):
        path = os.path.join(args.dir, f"output_{i}.cif")
        download(url, path, max_bytes=args.max_bytes)
        print(path)


if __name__ == "__main__":
    main()
