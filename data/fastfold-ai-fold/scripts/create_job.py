#!/usr/bin/env python3
"""
Create a FastFold job via POST /v1/jobs. Prints job ID to stdout (and optional JSON).

Supports two modes:

1. Simple mode (single protein chain):
   create_job.py --name "My Job" --sequence MALW... [--model boltz-2]
   create_job.py --name "Human insulin" --sequence MALWMRLLPLL... --model boltz-2

2. Full payload mode (same schema as FastFold Python SDK / OpenAPI JobInput):
   create_job.py --payload job.json
   create_job.py --payload -   # read JSON from stdin
   echo '{"name":"...","sequences":[...],"params":{...}}' | create_job.py --payload -

Full payload allows: multiple sequences (proteinChain, rnaSequence, dnaSequence, ligandSequence),
params (modelName, relaxPrediction, recyclingSteps, samplingSteps, etc.), constraints (pocket, bond),
isPublic, and optional "from" (library ID). See references/jobs.yaml for schema and examples.

Requires: Python standard library only (no external dependencies)
Environment: FASTFOLD_API_KEY
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# Load .env from project root so FASTFOLD_API_KEY can be set there
from load_env import load_dotenv
from security_utils import validate_base_url, validate_results_payload


def create_job_simple(
    base_url: str,
    api_key: str,
    name: str,
    sequence: str,
    model_name: str = "boltz-2",
    is_public: bool = False,
) -> dict:
    """Build and send a simple single-protein job (JobInput schema)."""
    body = {
        "name": name,
        "sequences": [{"proteinChain": {"sequence": sequence}}],
        "params": {"modelName": model_name},
    }
    if is_public is not None:
        body["isPublic"] = is_public
    return _post_job(base_url, api_key, body)


def create_job_from_payload(
    base_url: str,
    api_key: str,
    payload: dict,
    from_id: str | None = None,
) -> dict:
    """Send a full JobInput payload as-is. Optionally set ?from= for library ID."""
    if not isinstance(payload, dict):
        sys.exit("Error: Payload must be a JSON object.")
    for key in ("name", "sequences", "params"):
        if key not in payload:
            sys.exit(f"Error: Payload must include '{key}' (JobInput schema).")
    if not isinstance(payload["sequences"], list) or len(payload["sequences"]) < 1:
        sys.exit("Error: Payload 'sequences' must be a non-empty array.")
    return _post_job(base_url, api_key, payload, from_id=from_id)


def _post_job(
    base_url: str,
    api_key: str,
    body: dict,
    from_id: str | None = None,
) -> dict:
    url = f"{base_url.rstrip('/')}/v1/jobs"
    if from_id:
        url = f"{url}?from={from_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    req = urllib.request.Request(
        url=url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_text = resp.read().decode("utf-8", errors="replace")
            status = resp.getcode()
    except urllib.error.HTTPError as e:
        status = e.code
        response_text = e.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        sys.exit(f"Error: Network error while creating job: {e.reason}")

    if status == 401:
        sys.exit("Error: Unauthorized. Check FASTFOLD_API_KEY.")

    try:
        response_json = json.loads(response_text) if response_text else {}
    except json.JSONDecodeError:
        sys.exit(f"Error: API returned invalid JSON (status {status}).")

    if status in (400, 429):
        message = response_json.get("message", response_text)
        sys.exit(f"Error: {status} - {message}")
    if status >= 400:
        sys.exit(f"Error: {status} - {response_text}")

    return validate_results_payload(response_json)


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(
        description="Create a Fold job (simple mode or full JSON payload).",
        epilog="Full payload: use same JobInput as API/SDK (name, sequences, params; optional constraints, isPublic). See references/jobs.yaml.",
    )
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument("--json", action="store_true", help="Print full response JSON")
    ap.add_argument("--from", dest="from_id", metavar="UUID", help="Library item ID (query param)")

    # Simple mode
    ap.add_argument("--name", help="Job name (simple mode)")
    ap.add_argument("--sequence", help="Protein sequence, one-letter codes (simple mode)")
    ap.add_argument("--model", default="boltz-2", help="Model name (simple mode; default: boltz-2)")
    ap.add_argument(
        "--public",
        action="store_true",
        help="Make job public (simple mode)",
    )

    # Full payload mode
    ap.add_argument(
        "--payload",
        metavar="FILE",
        help="Path to JSON file or '-' for stdin. Sends body as JobInput (sequences, params, constraints, etc.). Ignores --name/--sequence/--model.",
    )

    args = ap.parse_args()

    api_key = os.environ.get("FASTFOLD_API_KEY")
    if not api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY in .env or environment.")
    base_url = validate_base_url(args.base_url)

    if args.payload is not None:
        # Full payload mode
        if args.payload == "-":
            try:
                payload = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                sys.exit(f"Error: Invalid JSON from stdin: {e}")
        else:
            try:
                with open(args.payload, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except FileNotFoundError:
                sys.exit(f"Error: File not found: {args.payload}")
            except json.JSONDecodeError as e:
                sys.exit(f"Error: Invalid JSON in {args.payload}: {e}")
        data = create_job_from_payload(base_url, api_key, payload, from_id=args.from_id)
    else:
        # Simple mode
        if not args.name or not args.sequence:
            ap.error("Simple mode requires --name and --sequence (or use --payload for full JSON).")
        data = create_job_simple(
            base_url,
            api_key,
            args.name,
            args.sequence,
            args.model,
            is_public=args.public,
        )
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(data.get("jobId", ""))


if __name__ == "__main__":
    main()
