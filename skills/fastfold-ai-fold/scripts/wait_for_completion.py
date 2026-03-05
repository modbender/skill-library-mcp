#!/usr/bin/env python3
"""
Wait for a FastFold job to complete by polling GET /v1/jobs/{jobId}/results.

Usage:
    wait_for_completion.py JOB_ID [--poll-interval SEC] [--timeout SEC] [--base-url URL]
    wait_for_completion.py JOB_ID --json   # print final results JSON to stdout (untrusted content)

Requires: Python standard library only (no external dependencies)
Environment: FASTFOLD_API_KEY
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

from load_env import load_dotenv
from security_utils import validate_base_url, validate_job_id, validate_results_payload


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


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="Wait for FastFold job completion.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--poll-interval", type=float, default=5.0, help="Seconds between polls (default 5)")
    ap.add_argument("--timeout", type=float, default=900.0, help="Max seconds to wait (default 900)")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument("--json", action="store_true", help="Print final results JSON to stdout")
    ap.add_argument("--quiet", action="store_true", help="Do not print status lines")
    args = ap.parse_args()

    api_key = os.environ.get("FASTFOLD_API_KEY")
    if not api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY in .env or environment.")

    job_id = validate_job_id(args.job_id)
    base_url = validate_base_url(args.base_url)

    start = time.time()
    last_status = None
    while True:
        data = get_results(base_url, api_key, job_id)
        job = data.get("job", {})
        status = job.get("status", "UNKNOWN")
        if not args.quiet:
            print(f"[FastFold] job {job_id} status: {status}", file=sys.stderr)
        if status == "COMPLETED":
            if args.json:
                print(json.dumps(data, indent=2))
            sys.exit(0)
        if status in ("FAILED", "STOPPED"):
            if args.json:
                print(json.dumps(data, indent=2))
            sys.exit(1)
        if (time.time() - start) > args.timeout:
            sys.exit(2)  # timeout
        time.sleep(max(0.1, args.poll_interval))


if __name__ == "__main__":
    main()
