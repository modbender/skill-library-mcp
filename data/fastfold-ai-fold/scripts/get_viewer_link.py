#!/usr/bin/env python3
"""
Print the FastFold cloud viewer URL for a job. User can open this in a browser to view
the structure (must be logged in to the same account if the job is private).

Usage:
    get_viewer_link.py JOB_ID [--base-url URL]

Output: single line with URL, e.g. https://cloud.fastfold.ai/mol/new?from=jobs&job_id=550e8400-e29b-41d4-a716-446655440000

Requires: Python standard library only (no external dependencies).
Environment: FASTFOLD_API_KEY (optional; only needed if you pass --check to verify job exists).
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from load_env import load_dotenv
from security_utils import validate_base_url, validate_job_id, validate_results_payload

VIEWER_URL_TEMPLATE = "https://cloud.fastfold.ai/mol/new?from=jobs&job_id={job_id}"


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
        sys.exit(f"Error: Network error while checking job: {e.reason}")

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
    ap = argparse.ArgumentParser(description="Print FastFold viewer URL for a job.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL (for --check)")
    ap.add_argument("--check", action="store_true", help="Verify job exists via API before printing URL")
    args = ap.parse_args()

    api_key = os.environ.get("FASTFOLD_API_KEY")
    if args.check and not api_key:
        sys.exit("Error: --check requires FASTFOLD_API_KEY in .env or environment.")

    job_id = validate_job_id(args.job_id)
    base_url = validate_base_url(args.base_url)

    if args.check:
        get_results(base_url, api_key, job_id)

    link = VIEWER_URL_TEMPLATE.format(job_id=job_id)
    print(link)


if __name__ == "__main__":
    main()
