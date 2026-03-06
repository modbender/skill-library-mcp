#!/usr/bin/env python3
"""
Fetch FastFold job results (GET /v1/jobs/{jobId}/results) and print JSON or a short summary.

Usage:
    fetch_results.py JOB_ID [--base-url URL]
    fetch_results.py JOB_ID --json   # print full API JSON (untrusted content)

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


def summary(data: dict) -> str:
    job = data.get("job", {})
    status = job.get("status", "UNKNOWN")
    is_complex = job.get("isComplex", False)
    lines = [f"Status: {status}", f"Complex: {is_complex}"]
    if status != "COMPLETED":
        return "\n".join(lines)
    params = data.get("parameters", {})
    sequences = data.get("sequences", [])
    pred = data.get("predictionPayload")
    if is_complex and pred:
        lines.append(f"cif_url: {pred.get('cif_url') or '(none)'}")
        lines.append(f"meanPLLDT: {pred.get('meanPLLDT')}")
        lines.append(f"ptm_score: {pred.get('ptm_score')}")
        lines.append(f"iptm_score: {pred.get('iptm_score')}")
    else:
        for i, seq in enumerate(sequences):
            pp = (seq or {}).get("predictionPayload") or {}
            lines.append(f"[{i}] cif_url: {pp.get('cif_url') or '(none)'}")
            lines.append(f"[{i}] meanPLLDT: {pp.get('meanPLLDT')}")
    return "\n".join(lines)


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="Fetch FastFold job results.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument("--json", action="store_true", help="Print full API JSON (untrusted content)")
    args = ap.parse_args()

    api_key = os.environ.get("FASTFOLD_API_KEY")
    if not api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY in .env or environment.")

    job_id = validate_job_id(args.job_id)
    base_url = validate_base_url(args.base_url)
    data = get_results(base_url, api_key, job_id)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(summary(data))


if __name__ == "__main__":
    main()
